-- Datos de ejemplo para entorno de desarrollo
-- Se ejecuta solo la primera vez que se inicializa el volumen de MySQL

INSERT INTO `homes` (`name`, `description`, `address`, `timezone`, `created_at`, `updated_at`)
VALUES ('Demo Home', 'Hogar de demostracion', 'N/A', 'UTC', NOW(), NOW())
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);

