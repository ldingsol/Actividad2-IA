from flask import Flask, jsonify, request
from flask_cors import CORS 
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time
from decimal import Decimal

# --- Configuración de la Aplicación ---
app = Flask(__name__)

# Configuración de CORS: Permite la comunicación con el Frontend de Vue/Vite
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# Configuración de la conexión a PostgreSQL
DB_CONFIG = {
    'database': os.environ.get('DB_NAME', 'postgres'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'Hummer08..'), 
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432')
}

def get_db_connection():
    """Establece una conexión a la base de datos."""
    return psycopg2.connect(**DB_CONFIG)

# --- ENDPOINT 1: Rutas de Prueba (Status) ---
@app.route('/api/v1/status', methods=['GET'])
def home():
    return jsonify({"message": "API de Gestión de Cuotas en linea y lista.", "endpoints": "/api/v1/dues..."}), 200

# --- ENDPOINT 2: Obtener Resumen de Deuda (Residente) ---
@app.route('/api/v1/dues/summary/<int:resident_id>', methods=['GET'])
def get_dues_summary(resident_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Log del ID que se está usando para la consulta
        app.logger.info(f"Consultando deuda para Residente ID: {resident_id}")

        # Consulta SQL con JOIN y LOWER() para robustez
        cursor.execute("""
            SELECT 
                COALESCE(SUM(c.monto_base), 0.00) AS total_balance, 
                COALESCE(COUNT(c.id_cuota), 0) AS months_due
            FROM cuotas c
            JOIN llaves_acceso la ON c.id_llave_fk = la.id_llave
            JOIN residente_llave rl ON la.id_llave = rl.id_llave_fk
            WHERE rl.id_residente_fk = %s 
              AND LOWER(c.estado) IN ('pendiente', 'vencido');
        """, (resident_id,))
        
        result = cursor.fetchone()
        
        # 1. Obtener valores brutos (pueden ser Decimal o None)
        total_balance_raw = result.get('total_balance') if result else 0.00
        months_due_raw = result.get('months_due') if result else 0

        # Log de debugging para validar la respuesta de la DB
        app.logger.info(f"DB Result (raw): {result}")
        if result and total_balance_raw is not None:
            app.logger.info(f"Type of total_balance: {type(total_balance_raw)}")
        
        # 2. Conversión segura (Decimal -> str -> float para serialización JSON)
        try:
            # Manejo del objeto Decimal de Psycopg2
            total_balance = float(str(total_balance_raw)) if total_balance_raw is not None else 0.00
            months_due = int(months_due_raw) if months_due_raw is not None else 0
        except Exception:
            total_balance = 0.00
            months_due = 0

        monthly_fee_placeholder = 50.00 

        app.logger.info(f"JSON being sent: Total Balance={total_balance}, Months Due={months_due}")
        
        cursor.close()
        
        return jsonify({
            "id_residente": resident_id,
            "total_balance": total_balance,
            "months_due": months_due,
            "monthly_fee": monthly_fee_placeholder
        }), 200

    except psycopg2.Error as e:
        app.logger.error(f"Error de base de datos: {e.pgerror}")
        return jsonify({"error": "Error interno al consultar la base de datos"}), 500
    except Exception as e:
        app.logger.error(f"Error inesperado: {e}")
        return jsonify({"error": "Error inesperado del servidor"}), 500
    finally:
        if conn:
            conn.close() 

# --- ENDPOINT 4: SOLICITUD DE REFERENCIA DE PAGO (Residente) ---
@app.route('/api/v1/dues/request-reference', methods=['POST'])
def request_payment_reference():
    """Genera una referencia única para que el residente pague en caja (estado 'pendiente_caja')."""
    data = request.get_json()
    app.logger.info(f"Datos recibidos para referencia: {data}")
    
    id_residente = data.get('id_residente')
    monto_a_pagar = data.get('monto_a_pagar')

    # Validación robusta de monto
    try:
        monto_a_pagar = float(monto_a_pagar)
        if monto_a_pagar <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Monto a pagar no válido o es cero."}), 400

    if not id_residente:
        return jsonify({"error": "Falta ID de residente."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Generar una referencia única
        referencia_unica = f"REF-{id_residente}-{int(time.time())}"
        
        # Insertar el registro de pago en estado 'pendiente_caja'
        cursor.execute("""
            INSERT INTO pagos (id_residente_fk, monto_pagado, referencia_pago, estado)
            VALUES (%s, %s, %s, 'pendiente_caja')
            RETURNING id_pago;
        """, (id_residente, monto_a_pagar, referencia_unica))
        
        conn.commit()
        
        return jsonify({
            "message": "Referencia generada con éxito.",
            "referencia_pago": referencia_unica,
            "monto_a_pagar": monto_a_pagar
        }), 201

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        app.logger.error(f"Error DB al generar referencia: {e.pgerror}")
        return jsonify({"error": "Error de base de datos al generar la referencia."}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        app.logger.error(f"Error inesperado: {e}")
        return jsonify({"error": "Error interno del servidor."}), 500
    finally:
        if conn:
            conn.close()

# --- ENDPOINT 5: Búsqueda de Pago Pendiente por Referencia (Cajero) ---
@app.route('/api/v1/admin/search-pending-payment/<string:referencia>', methods=['GET'])
def search_pending_payment(referencia):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Consulta para encontrar la referencia en estado 'pendiente_caja'
        cursor.execute("""
            SELECT 
                p.referencia_pago,
                p.monto_pagado,
                p.id_residente_fk AS id_residente,
                r.nombre_completo AS residente_nombre,
                r.cedula AS residente_cedula
            FROM pagos p
            JOIN residentes r ON p.id_residente_fk = r.id_residente
            WHERE p.referencia_pago = %s AND p.estado = 'pendiente_caja';
        """, (referencia,))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": f"Referencia '{referencia}' no encontrada o ya ha sido pagada/cancelada."}), 404

        # Conversión del monto de Decimal a float (necesario para el frontend)
        monto_pagado = float(str(result['monto_pagado'])) if result['monto_pagado'] is not None else 0.00
        
        data = {
            "referencia_pago": result['referencia_pago'],
            "monto_pagado": monto_pagado,
            "id_residente": result['id_residente'],
            "residente_nombre": result['residente_nombre'],
            "residente_cedula": result['residente_cedula']
        }

        return jsonify({"message": "Referencia pendiente encontrada.", "data": data}), 200

    except psycopg2.Error as e:
        app.logger.error(f"Error DB al buscar referencia: {e.pgerror}")
        return jsonify({"error": "Error de base de datos durante la búsqueda."}), 500
    except Exception as e:
        app.logger.error(f"Error inesperado al buscar referencia: {e}")
        return jsonify({"error": "Error interno del servidor."}), 500
    finally:
        if conn:
            conn.close()


# --- ENDPOINT 3: Registro de Pago en Caja (Aplicación de Cuotas) ---
@app.route('/api/v1/admin/register-cash-payment', methods=['POST'])
def register_cash_payment():
    data = request.get_json()
    
    referencia_pago = data.get('referencia_pago')
    id_cajero = data.get('id_cajero')
    id_residente_pagador = data.get('id_residente_pagador')

    # Validación robusta de monto
    try:
        monto_pagado = float(data.get('monto_pagado'))
        if monto_pagado <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Monto pagado no válido"}), 400

    if not all([referencia_pago, id_cajero, id_residente_pagador]):
        return jsonify({"error": "Faltan campos requeridos (referencia, monto, IDs)"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Marcar el registro existente de la referencia como 'pagado'
        # Esto es crucial para evitar que la misma referencia se pague dos veces
        cursor.execute("""
            UPDATE pagos
            SET 
                id_cajero_fk = %s,
                estado = 'pagado'
            WHERE referencia_pago = %s AND estado = 'pendiente_caja'
            RETURNING id_pago;
        """, (id_cajero, referencia_pago))
        
        update_result = cursor.fetchone()
        if not update_result:
             # Podría ser que la referencia ya fue pagada o nunca existió
            return jsonify({"error": f"La referencia {referencia_pago} no pudo ser marcada como pagada. Verifique su estado."}), 400

        id_pago_registrado = update_result['id_pago']
        remaining_amount = monto_pagado

        # 2. Obtener y Aplicar el Pago a las Cuotas más Antiguas (transaccional)
        cursor.execute("""
            SELECT c.id_cuota, c.monto_base
            FROM cuotas c
            JOIN residente_llave rl ON c.id_llave_fk = rl.id_llave_fk
            WHERE rl.id_residente_fk = %s AND LOWER(c.estado) IN ('pendiente', 'vencido')
            ORDER BY c.fecha_generacion ASC;
        """, (id_residente_pagador,))

        pending_dues = cursor.fetchall()
        applied_dues_count = 0

        for cuota in pending_dues:
            # Aseguramos que monto_base es float para la resta
            monto_base = float(str(cuota['monto_base'])) 
            
            if remaining_amount >= monto_base:
                # Marcar cuota como pagada
                cursor.execute("UPDATE cuotas SET estado = 'pagado', id_pago_fk = %s WHERE id_cuota = %s;", 
                               (id_pago_registrado, cuota['id_cuota']))
                remaining_amount -= monto_base
                applied_dues_count += 1
            else:
                # No hay suficiente monto para cubrir esta cuota
                break 

        conn.commit()
        
        return jsonify({
            "message": "Pago registrado y aplicado con éxito.",
            "id_pago": id_pago_registrado,
            "cuotas_aplicadas": applied_dues_count,
            "remaining_unapplied": round(remaining_amount, 2)
        }), 201

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        app.logger.error(f"Error de DB al registrar pago: {e.pgerror}")
        return jsonify({"error": "Error de base de datos durante el registro del pago."}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        app.logger.error(f"Error inesperado: {e}")
        return jsonify({"error": "Error interno del servidor."}), 500
    finally:
        if conn:
            conn.close()

# --- ENDPOINT 6: Historial de Pagos por Residente (Residente) ---
@app.route('/api/v1/dues/history/<int:resident_id>', methods=['GET'])
def get_payment_history(resident_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                id_pago, 
                referencia_pago, 
                monto_pagado, 
                fecha_pago, 
                estado,
                COALESCE(cajero.nombre_completo, 'En Línea') AS procesado_por
            FROM pagos p
            LEFT JOIN residentes cajero ON p.id_cajero_fk = cajero.id_residente
            WHERE p.id_residente_fk = %s
            ORDER BY fecha_pago DESC;
        """, (resident_id,))
        
        results = cursor.fetchall()
        
        # Convertir Decimal a float para serialización JSON
        for row in results:
            if row['monto_pagado'] is not None:
                row['monto_pagado'] = float(str(row['monto_pagado']))

        return jsonify({
            "message": "Historial de pagos recuperado con éxito.", 
            "data": results
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener historial de pagos: {e}")
        return jsonify({"error": "Error interno del servidor al obtener el historial."}), 500
    finally:
        if conn:
            conn.close()
# --- ENDPOINT 7: Registro Completo de Nuevo Residente y Llave (Admin) ---
@app.route('/api/v1/admin/register-resident', methods=['POST'])
def register_resident():
    """Registra un nuevo residente, crea una llave de acceso asociada, 
    y vincula ambos a través de la tabla residente_llave, todo en una transacción."""
    data = request.get_json()
    
    # Datos del Residente
    nombre_completo = data.get('nombre_completo')
    cedula = data.get('cedula')
    telefono = data.get('telefono')
    email = data.get('email')
    
    # Datos de la Llave
    num_llave = data.get('num_llave')
    
    if not all([nombre_completo, cedula, telefono, email, num_llave]):
        return jsonify({"error": "Faltan datos obligatorios para el registro del residente/llave."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Insertar en la tabla 'residentes'
        cursor.execute("""
            INSERT INTO residentes (nombre_completo, cedula, telefono, email)
            VALUES (%s, %s, %s, %s)
            RETURNING id_residente;
        """, (nombre_completo, cedula, telefono, email))
        id_residente = cursor.fetchone()[0]
        
        # 2. Insertar en la tabla 'llaves_acceso'
        cursor.execute("""
            INSERT INTO llaves_acceso (numero_llave, estado)
            VALUES (%s, 'activa')
            RETURNING id_llave;
        """, (num_llave,))
        id_llave = cursor.fetchone()[0]

        # 3. Insertar en la tabla 'residente_llave' (Vínculo)
        cursor.execute("""
            INSERT INTO residente_llave (id_residente_fk, id_llave_fk)
            VALUES (%s, %s);
        """, (id_residente, id_llave))
        
        conn.commit()
        
        return jsonify({
            "message": "Residente, llave y vínculo registrados con éxito.",
            "id_residente": id_residente,
            "id_llave": id_llave,
            "num_llave": num_llave
        }), 201

    except psycopg2.IntegrityError as e:
        if conn: conn.rollback()
        # Captura errores de duplicidad (ej. cédula o número de llave ya existen)
        app.logger.error(f"Error de integridad al registrar residente: {e.pgerror}")
        return jsonify({"error": "Error de integridad: La cédula o el número de llave ya existen."}), 409
    except Exception as e:
        if conn: conn.rollback()
        app.logger.error(f"Error inesperado en registro de residente: {e}")
        return jsonify({"error": "Error interno del servidor al registrar el residente."}), 500
    finally:
        if conn: conn.close()
# --- Ejecución de la Aplicación ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)