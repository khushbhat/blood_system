-- Database initialization for blood_system
-- Run this file as a MySQL user with privileges to create databases and users (e.g., root)

-- 1) Create the database
CREATE DATABASE IF NOT EXISTS `blood_system` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `blood_system`;

-- 2) Create the application user and grant privileges
-- Note: these credentials match those used in app.py
CREATE USER IF NOT EXISTS 'flaskuser'@'localhost' IDENTIFIED BY 'FlaskPass123!';
GRANT ALL PRIVILEGES ON `blood_system`.* TO 'flaskuser'@'localhost';
FLUSH PRIVILEGES;

-- 3) Tables

-- Users table
CREATE TABLE IF NOT EXISTS `Users` (
  `user_id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` ENUM('Donor','Hospital','Admin') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Donors table
CREATE TABLE IF NOT EXISTS `Donors` (
  `donor_id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `blood_group` VARCHAR(10) NOT NULL,
  `city` VARCHAR(100),
  `last_donation_date` DATE,
  CONSTRAINT `fk_donors_user` FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Hospitals table
CREATE TABLE IF NOT EXISTS `Hospitals` (
  `hospital_id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL UNIQUE,
  `hospital_name` VARCHAR(255) NOT NULL,
  `city` VARCHAR(100),
  `contact_number` VARCHAR(50),
  CONSTRAINT `fk_hospitals_user` FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Donations table
CREATE TABLE IF NOT EXISTS `Donations` (
  `donation_id` INT AUTO_INCREMENT PRIMARY KEY,
  `donor_id` INT NOT NULL,
  `hospital_id` INT NULL,
  `donation_date` DATE NOT NULL,
  `units_donated` INT NOT NULL,
  CONSTRAINT `fk_donations_donor` FOREIGN KEY (`donor_id`) REFERENCES `Donors`(`donor_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_donations_hospital` FOREIGN KEY (`hospital_id`) REFERENCES `Hospitals`(`hospital_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- BloodRequests table
CREATE TABLE IF NOT EXISTS `BloodRequests` (
  `request_id` INT AUTO_INCREMENT PRIMARY KEY,
  `hospital_id` INT NOT NULL,
  `blood_group` VARCHAR(10) NOT NULL,
  `units_required` INT NOT NULL,
  `request_date` DATE NOT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'Pending',
  CONSTRAINT `fk_requests_hospital` FOREIGN KEY (`hospital_id`) REFERENCES `Hospitals`(`hospital_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Optional indexes for common lookups
-- MySQL versions may not support `CREATE INDEX IF NOT EXISTS`.
-- Use INFORMATION_SCHEMA checks with prepared statements to create indexes only when missing.

-- idx_users_email
SET @cnt = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'Users' AND INDEX_NAME = 'idx_users_email');
SET @sql = IF(@cnt = 0, 'CREATE INDEX idx_users_email ON Users(email)', 'SELECT "idx_users_email exists"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- idx_donors_user
SET @cnt = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'Donors' AND INDEX_NAME = 'idx_donors_user');
SET @sql = IF(@cnt = 0, 'CREATE INDEX idx_donors_user ON Donors(user_id)', 'SELECT "idx_donors_user exists"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- idx_hospitals_user
SET @cnt = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'Hospitals' AND INDEX_NAME = 'idx_hospitals_user');
SET @sql = IF(@cnt = 0, 'CREATE INDEX idx_hospitals_user ON Hospitals(user_id)', 'SELECT "idx_hospitals_user exists"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- idx_requests_status
SET @cnt = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'BloodRequests' AND INDEX_NAME = 'idx_requests_status');
SET @sql = IF(@cnt = 0, 'CREATE INDEX idx_requests_status ON BloodRequests(status)', 'SELECT "idx_requests_status exists"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- End of file
