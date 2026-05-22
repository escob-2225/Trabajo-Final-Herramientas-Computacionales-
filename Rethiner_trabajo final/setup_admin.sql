-- Ejecutar en optica_db si la app no pudo migrar automáticamente

USE optica_db;

ALTER TABLE productos
  ADD COLUMN estado VARCHAR(20) DEFAULT 'activo';

ALTER TABLE usuarios
  ADD COLUMN rol VARCHAR(20) DEFAULT 'cliente';

ALTER TABLE usuarios
  ADD COLUMN identificacion VARCHAR(30) UNIQUE;

ALTER TABLE citas
  ADD COLUMN usuario_id INT NULL;

-- El administrador por defecto se crea al iniciar la app:
-- Email: admin@rethiner.com
-- Contraseña: admin1234
