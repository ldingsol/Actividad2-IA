
-- Conectado a control_pagos
CREATE TABLE cuotas AS TABLE postgres.public.cuotas;
 select * from cuotas

select * from residente_llave

 select * from llaves_acceso

 select * from pagos

 select * from residentes

 INSERT INTO residentes (id_residente, nombre_completo, cedula, email, rol) 
VALUES 
(3, 'Sara Peña', '12345670', 'sarapeña@correo.com', 'resiedente'),
(4, 'Antonio Pérez', '89654321', 'Antonio@perez.com', 'residente')
ON CONFLICT (id_residente) DO NOTHING;

SELECT c.id_cuota, c.monto_base
FROM cuotas c
JOIN residente_llave rl ON c.id_llave_fk = rl.id_llave_fk
WHERE rl.id_residente_fk = %s AND c.estado IN ('pendiente', 'vencido')
ORDER BY c.fecha_generacion ASC;



SELECT * FROM cuotas c
JOIN llaves_acceso la ON c.id_llave_fk = la.id_llave
JOIN residente_llave rl ON la.id_llave = rl.id_llave_fk
WHERE rl.id_residente_fk = 2 AND c.estado IN ('pendiente', 'vencido');

INSERT INTO cuotas (id_llave_fk, fecha_generacion, monto_base, estado)
VALUES (2, CURRENT_DATE, 100.00, 'pendiente');

INSERT INTO residentes (nombre_completo, cedula, email, rol) 
VALUES 
    ('Ana Pérez (Cajera Principal)', '12345678', 'ana.perez@admin.com', 'cajero');

INSERT INTO llaves_acceso (codigo_llave, descripcion, monto_mensual_base) 
VALUES 
('CASA-A02', 'Cuota de Mantenimiento Mensual', 50.00);


INSERT INTO residente_llave (id_residente_fk, id_llave_fk, es_pagador_principal) 
VALUES 
(2, 2, TRUE);

INSERT INTO cuotas (id_llave_fk, monto_base, fecha_generacion, estado) 
VALUES 
(2, 50.00, '2025-09-01', 'vencido'),    -- Vencida
(2, 50.00, '2025-10-01', 'pendiente'),   -- Pendiente
(2, 50.00, '2025-11-01', 'pendiente'),
(2, 50.00, '2025-12-01', 'pendiente');


SELECT id_residente, nombre_completo, rol FROM residentes ORDER BY id_residente;

UPDATE cuotas
SET id_llave_fk = 2
WHERE id_llave_fk = 1;


SELECT 
    SUM(c.monto_base) AS total_balance, 
    COUNT(c.id_cuota) AS months_due
FROM cuotas c
JOIN llaves_acceso la ON c.id_llave_fk = la.id_llave
JOIN residente_llave rl ON la.id_llave = rl.id_llave_fk
WHERE rl.id_residente_fk = 2 AND c.estado IN ('pendiente', 'vencido');

SELECT id_residente_fk, id_llave_fk, es_pagador_principal 
FROM residente_llave 
WHERE id_residente_fk = 2;

SELECT id_cuota, id_llave_fk, monto_base, estado 
FROM cuotas 
WHERE id_llave_fk = 1 AND estado IN ('pendiente', 'vencido');

SELECT 
    r.nombre_completo,
    c.monto_base,
    c.estado,
    la.descripcion
FROM residentes r
JOIN residente_llave rl ON r.id_residente = rl.id_residente_fk
JOIN llaves_acceso la ON rl.id_llave_fk = la.id_llave
JOIN cuotas c ON la.id_llave = c.id_llave_fk
WHERE r.id_residente = 2 AND c.estado IN ('pendiente', 'vencido');


SELECT SUM(c.monto_base) AS total_balance, COUNT(c.id_cuota) AS months_due
FROM cuotas c
JOIN llaves_acceso la ON c.id_llave_fk = la.id_llave      -- (1) Cuota -> Llave
JOIN residente_llave rl ON la.id_llave = rl.id_llave_fk  -- (2) Llave -> Vínculo
WHERE rl.id_residente_fk = 2 AND c.estado IN ('pendiente', 'vencido'); -- (3) Vínculo -> Residente + Estado

SELECT * FROM residente_llave WHERE id_residente_fk = 2;

SELECT id_cuota, monto_base, estado 
FROM cuotas 
WHERE id_llave_fk = 2 AND estado IN ('pendiente', 'vencido');

SELECT 
    r.nombre_completo,
    la.descripcion,
    c.monto_base,
    c.estado
FROM cuotas c
JOIN llaves_acceso la ON c.id_llave_fk = la.id_llave
JOIN residente_llave rl ON la.id_llave = rl.id_llave_fk
JOIN residentes r ON rl.id_residente_fk = r.id_residente -- Agregamos JOIN a residentes solo para claridad
WHERE rl.id_residente_fk = 2 AND c.estado IN ('pendiente', 'vencido');

UPDATE cuotas
SET id_llave_fk = 2
WHERE estado IN ('pendiente', 'vencido');

INSERT INTO residente_llave (id_residente_fk, id_llave_fk, es_pagador_principal) 
VALUES (2, 2, TRUE)
ON CONFLICT (id_residente_fk, id_llave_fk) DO UPDATE SET es_pagador_principal = TRUE;


SELECT * FROM residentes WHERE id_residente = 2;

SELECT id_llave_fk FROM residente_llave WHERE id_residente_fk = 2;

SELECT id_cuota, monto_base, estado 
FROM cuotas 
WHERE id_llave_fk = 2 AND estado IN ('pendiente', 'vencido');

delete from llaves_acceso where id_relacion = '1';

SELECT 
    SUM(c.monto_base) AS total_balance, 
    COUNT(c.id_cuota) AS months_due
FROM cuotas c
JOIN llaves_acceso la ON c.id_llave_fk = la.id_llave
JOIN residente_llave rl ON la.id_llave = rl.id_llave_fk
WHERE rl.id_residente_fk = 2 AND c.estado IN ('pendiente', 'vencido');

DELETE FROM llaves_acceso WHERE id_llave = 1;

DELETE FROM residente_llave WHERE id_llave_fk = 1;


            SELECT 
                COALESCE(SUM(c.monto_base), 0.00) AS total_balance, 
                COUNT(c.id_cuota) AS months_due
            FROM cuotas c
            JOIN llaves_acceso la ON c.id_llave_fk = la.id_llave
            JOIN residente_llave rl ON la.id_llave = rl.id_llave_fk
            WHERE rl.id_residente_fk = %s AND c.estado IN ('pendiente', 'vencido');

            SELECT 
                COALESCE(SUM(c.monto_base), 0.00) AS total_balance, 
                COALESCE(COUNT(c.id_cuota), 0) AS months_due
            FROM cuotas c
            JOIN llaves_acceso la ON c.id_llave_fk = la.id_llave
            JOIN residente_llave rl ON la.id_llave = rl.id_llave_fk
            WHERE rl.id_residente_fk = 2 AND c.estado IN ('pendiente', 'vencido');
SELECT id_llave_fk FROM residente_llave WHERE id_residente_fk = 2;

SELECT count(*), sum(monto_base) 
FROM cuotas 
WHERE id_llave_fk = 2 AND estado IN ('pendiente', 'vencido');


ALTER TABLE pagos
ADD COLUMN estado VARCHAR(50) NOT NULL DEFAULT 


DELETE FROM pagos
WHERE referencia_pago = 'REF-2-1765745995' AND estado = 'pendiente_caja';

SELECT * FROM pagos WHERE referencia_pago = 'REF-2-1765742208';

ALTER TABLE cuotas
ADD COLUMN id_pago_fk INTEGER REFERENCES pagos(id_pago);

ALTER TABLE pagos
ADD COLUMN fecha_pago TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW();

ALTER TABLE residentes
ADD COLUMN telefono VARCHAR(50);

SELECT setval('residentes_id_residente_seq', 1000, false);