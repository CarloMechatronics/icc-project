CREATE TABLE IF NOT EXISTS `users` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
	`email` VARCHAR(63) NOT NULL UNIQUE,
	`password` VARCHAR(255) NOT NULL COMMENT 'hashed password, not plain text',
	`name` VARCHAR(63) NOT NULL,
	`global_role` ENUM('USER', 'SYSTEM_ADMIN') NOT NULL DEFAULT 'USER',
	`created_at` DATETIME NOT NULL,
	`updated_at` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `homes` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
	`name` VARCHAR(63) NOT NULL,
	`description` VARCHAR(255),
	`address` VARCHAR(127),
	`timezone` VARCHAR(63) NOT NULL,
	`created_at` DATETIME NOT NULL,
	`updated_at` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `user_homes` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
	`user_id` BIGINT UNSIGNED NOT NULL,
	`home_id` BIGINT UNSIGNED NOT NULL,
	`home_role` ENUM('OWNER', 'MEMBER', 'GUEST') NOT NULL,
	`can_manage_devices` BOOLEAN NOT NULL DEFAULT 0,
	`can_manage_rules` BOOLEAN NOT NULL DEFAULT 0,
	`can_view_metrics` BOOLEAN NOT NULL DEFAULT 1,
	`can_invite_members` BOOLEAN NOT NULL DEFAULT 0,
	`created_at` DATETIME NOT NULL,
	`updated_at` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE UNIQUE INDEX `uk_user_homes_user_id_home_id`
ON `user_homes` (`user_id`, `home_id`);
CREATE TABLE IF NOT EXISTS `controllers` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
	`home_id` BIGINT UNSIGNED NOT NULL,
	`name` VARCHAR(63) NOT NULL,
	`description` VARCHAR(255),
	`ip_address` VARCHAR(31),
	`hardware_id` VARCHAR(63) NOT NULL UNIQUE,
	`created_at` DATETIME NOT NULL,
	`updated_at` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE INDEX `idx_controllers_home_id`
ON `controllers` (`home_id`);
CREATE TABLE IF NOT EXISTS `devices` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
	`home_id` BIGINT UNSIGNED NOT NULL,
	`controller_id` BIGINT UNSIGNED NOT NULL,
	`name` VARCHAR(63) NOT NULL,
	`description` VARCHAR(255) NOT NULL,
	`type` ENUM('SENSOR', 'ACTUATOR', 'HYBRID') NOT NULL,
	`pin` TINYINT UNSIGNED NOT NULL,
	`model` VARCHAR(63) NOT NULL,
	`http_path` VARCHAR(255),
	`state` ENUM('ON', 'OFF', 'OPEN', 'CLOSED', 'ACTING', 'READING', 'ERROR'),
	`active` BOOLEAN NOT NULL DEFAULT 1 COMMENT '''0'' inactive
''1'' active',
	`created_at` DATETIME NOT NULL,
	`updated_at` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE INDEX `idx_devices_home_id`
ON `devices` (`home_id`);
CREATE INDEX `idx_devices_controller_id`
ON `devices` (`controller_id`);
CREATE TABLE IF NOT EXISTS `readings` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
	`device_id` BIGINT UNSIGNED NOT NULL,
	`home_id` BIGINT UNSIGNED NOT NULL,
	`measure` ENUM('TEMPERATURE', 'HUMIDITY', 'MOTION') NOT NULL,
	`value` DOUBLE NOT NULL,
	`unit` VARCHAR(32) NOT NULL,
	`timestamp` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE INDEX `idx_readings_device_id_timestamp`
ON `readings` (`device_id`, `timestamp`);
CREATE INDEX `idx_readings_home_id_timestamp`
ON `readings` (`home_id`, `timestamp`);
CREATE TABLE IF NOT EXISTS `events` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
	`device_id` BIGINT UNSIGNED NOT NULL,
	`home_id` BIGINT UNSIGNED NOT NULL,
	`type` ENUM('TRIGGER', 'MANUAL', 'ERROR') NOT NULL,
	`origin` ENUM('USER', 'SYSTEM', 'RULE') NOT NULL,
	`detail` VARCHAR(255) NOT NULL,
	`prev_value` DOUBLE NOT NULL,
	`next_value` DOUBLE NOT NULL,
	`timestamp` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE INDEX `idx_events_device_id_timestamp`
ON `events` (`device_id`, `timestamp`);
CREATE INDEX `idx_events_home_id_timestamp`
ON `events` (`home_id`, `timestamp`);
CREATE TABLE IF NOT EXISTS `rules` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
	`home_id` BIGINT UNSIGNED NOT NULL,
	`condition` VARCHAR(100) NOT NULL,
	`active` BOOLEAN NOT NULL DEFAULT 1,
	`created_at` DATETIME NOT NULL,
	`update_at` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `rule_actions` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
	`rule_id` BIGINT NOT NULL,
	`action_type` VARCHAR(100) NOT NULL COMMENT 'Examples: TURN_ON, TURN_OFF, OPEN, CLOSE, DEACTIVATE, ACTIVATE, NOTIFY',
	`device_id` BIGINT NOT NULL,
	`created_at` DATETIME NOT NULL,
	`updated_at` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE INDEX `idx_rule_actions_rule_id`
ON `rule_actions` (`rule_id`);

ALTER TABLE `user_homes`
ADD CONSTRAINT `fk_user_homes_users_id`
FOREIGN KEY(`user_id`) REFERENCES `users`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `user_homes`
ADD CONSTRAINT `fk_user_homes_homes_id`
FOREIGN KEY(`home_id`) REFERENCES `homes`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `controllers`
ADD CONSTRAINT `fk_controllers_homes_id`
FOREIGN KEY(`home_id`) REFERENCES `homes`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `devices`
ADD CONSTRAINT `fk_devices_controllers_id`
FOREIGN KEY(`controller_id`) REFERENCES `controllers`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `devices`
ADD CONSTRAINT `fk_devices_homes_id`
FOREIGN KEY(`home_id`) REFERENCES `homes`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `readings`
ADD CONSTRAINT `fk_readings_device_id`
FOREIGN KEY(`device_id`) REFERENCES `devices`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `readings`
ADD CONSTRAINT `fk_readings_home_id`
FOREIGN KEY(`home_id`) REFERENCES `homes`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `events`
ADD CONSTRAINT `fk_events_home_id`
FOREIGN KEY(`home_id`) REFERENCES `homes`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `events`
ADD CONSTRAINT `fk_events_device_id`
FOREIGN KEY(`device_id`) REFERENCES `devices`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `rules`
ADD CONSTRAINT `fk_rules_home_id`
FOREIGN KEY(`home_id`) REFERENCES `homes`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `rule_actions`
ADD CONSTRAINT `fk_rule_actions_rule_id`
FOREIGN KEY(`rule_id`) REFERENCES `rules`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `rule_actions`
ADD CONSTRAINT `fk_rule_actions_device_id_devices`
FOREIGN KEY(`device_id`) REFERENCES `devices`(`id`)
ON UPDATE CASCADE ON DELETE CASCADE;
