-- ------------------------------------------------
-- 1. TABLA: RESIDENTES (Tabla de referencia de usuarios y roles)
-- ------------------------------------------------
CREATE TABLE residentes (
    id_residente SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    rol VARCHAR(10) DEFAULT 'residente' NOT NULL -- 'residente', 'administrador', 'cajero'
);

-- ------------------------------------------------
-- 2. TABLA: LLAVES_ACCESO (Unidad de Cobro/Membresía)
-- ------------------------------------------------
CREATE TABLE llaves_acceso (
    id_llave SERIAL PRIMARY KEY,
    codigo_llave VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100) NOT NULL,
    monto_mensual_base NUMERIC(10, 2) NOT NULL, -- Valor fijo de la cuota
    activo BOOLEAN DEFAULT TRUE NOT NULL
);

-- ------------------------------------------------
-- 3. TABLA: RESIDENTE_LLAVE (Relación Muchos a Muchos entre Residente y Llave)
-- ------------------------------------------------
CREATE TABLE residente_llave (
    id_relacion SERIAL PRIMARY KEY,
    id_residente_fk INTEGER NOT NULL,
    id_llave_fk INTEGER NOT NULL,
    es_pagador_principal BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- Definición de Claves Foráneas (FK)
    FOREIGN KEY (id_residente_fk) REFERENCES residentes(id_residente) ON DELETE CASCADE,
    FOREIGN KEY (id_llave_fk) REFERENCES llaves_acceso(id_llave) ON DELETE CASCADE,

    -- Restricción para asegurar que una pareja de residente-llave sea única
    UNIQUE (id_residente_fk, id_llave_fk)
);

-- ------------------------------------------------
-- 4. TABLA: CUOTAS (Registro de la Deuda Generada)
-- ------------------------------------------------
CREATE TABLE cuotas (
    id_cuota SERIAL PRIMARY KEY,
    id_llave_fk INTEGER NOT NULL,
    monto_base NUMERIC(10, 2) NOT NULL,
    fecha_generacion DATE NOT NULL,
    estado VARCHAR(10) DEFAULT 'pendiente' NOT NULL, -- 'pendiente', 'pagado', 'vencido'
    
    -- Definición de Clave Foránea (FK)
    FOREIGN KEY (id_llave_fk) REFERENCES llaves_acceso(id_llave) ON DELETE CASCADE
);

-- ------------------------------------------------
-- 5. TABLA: PAGOS (Registro de Transacciones de Caja)
-- ------------------------------------------------
CREATE TABLE pagos (
    id_pago SERIAL PRIMARY KEY,
    id_residente_fk INTEGER NOT NULL, -- Quién está logueado y haciendo el pago
    id_cajero_fk INTEGER, -- Quién registró el pago (Si es un administrador/cajero)
    monto_pagado NUMERIC(10, 2) NOT NULL,
    referencia_pago VARCHAR(50) UNIQUE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT NOW() NOT NULL,
    
    -- Definición de Claves Foráneas (FK)
    FOREIGN KEY (id_residente_fk) REFERENCES residentes(id_residente) ON DELETE RESTRICT,
    FOREIGN KEY (id_cajero_fk) REFERENCES residentes(id_residente) ON DELETE SET NULL
);