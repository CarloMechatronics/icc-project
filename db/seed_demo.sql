-- Datos de ejemplo para ambiente de desarrollo inicial.
-- Este archivo se ejecuta en el bootstrap de MySQL dentro de Docker
-- (se monta como /docker-entrypoint-initdb.d/03-seed-demo.sql).

USE smarthome;

-- Usuario admin
INSERT INTO users (id, email, password, name, global_role, created_at, updated_at)
VALUES (
    1,
    'carlo.torres@utec.edu.pe',
    'scrypt:32768:8:1$DUHaclGdPVmgGZQQ$928a7cd51d570c68afdcd3b1ba3c5df3d35047a861cad7f0f51769b11899dbfd9cf181b4acf4d55a052f17616aa73f7e1e12bfd80224a9a13e4f1c2c2d0c015c',
    'Carlo Torres',
    'SYSTEM_ADMIN',
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    global_role = VALUES(global_role),
    updated_at = NOW();

-- Hogar demo
INSERT INTO homes (id, name, description, address, timezone, created_at, updated_at)
VALUES (
    1,
    'Depa portatil',
    'Mi casa portatil de bolsillo (casi)',
    'Lima, Peru',
    'America/Lima',
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE
    description = VALUES(description),
    address = VALUES(address),
    timezone = VALUES(timezone),
    updated_at = NOW();

-- Relacion usuario-hogar
INSERT INTO user_homes (
    id,
    user_id,
    home_id,
    home_role,
    can_manage_devices,
    can_manage_rules,
    can_view_metrics,
    can_invite_members,
    created_at,
    updated_at
)
VALUES (
    1,
    1,
    1,
    'OWNER',
    1,
    1,
    1,
    1,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE
    home_role = VALUES(home_role),
    can_manage_devices = VALUES(can_manage_devices),
    can_manage_rules = VALUES(can_manage_rules),
    can_view_metrics = VALUES(can_view_metrics),
    can_invite_members = VALUES(can_invite_members),
    updated_at = NOW();

-- Controlador y dispositivo demo (alineados con el backend Flask)
INSERT INTO controllers (id, home_id, name, description, ip_address, hardware_id, created_at, updated_at)
VALUES (
    1,
    1,
    'ESP32 Gateway',
    'Autoregistrado para demo',
    NULL,
    'esp32-gw',
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE
    description = VALUES(description),
    ip_address = VALUES(ip_address),
    updated_at = NOW();

INSERT INTO devices (
    id,
    home_id,
    controller_id,
    name,
    description,
    type,
    pin,
    model,
    http_path,
    state,
    active,
    created_at,
    updated_at
)
VALUES (
    1,
    1,
    1,
    'esp32-1',
    'ESP32 S3 demo',
    'HYBRID',
    0,
    'esp32-s3',
    NULL,
    'OFF',
    1,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE
    description = VALUES(description),
    model = VALUES(model),
    state = VALUES(state),
    active = VALUES(active),
    updated_at = NOW();

-- Lecturas iniciales para que el dashboard muestre algo
INSERT INTO readings (device_id, home_id, measure, value, unit, timestamp)
VALUES
    (1, 1, 'TEMPERATURE', 23.5, 'C', NOW() - INTERVAL 2 MINUTE),
    (1, 1, 'HUMIDITY', 52.0, '%', NOW() - INTERVAL 1 MINUTE),
    (1, 1, 'MOTION', 0.0, 'bool', NOW());
