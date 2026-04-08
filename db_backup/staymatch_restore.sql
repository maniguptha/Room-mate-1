-- ============================================================
--  StayMatch Database Backup / Restore Script
--  Generated: 2026-03-10
--  Use this SQL in phpMyAdmin or mysql CLI after reinstalling
--  XAMPP to recreate the staymatch database from scratch.
-- ============================================================

CREATE DATABASE IF NOT EXISTS `staymatch` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `staymatch`;

-- ─────────────────────────────────────────────────────────────
-- Table: user
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `user` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20),
  `location` VARCHAR(200),
  `bio` TEXT,
  `budget` VARCHAR(50),
  `age` INT,
  `traits` TEXT,
  `onboarding_complete` BOOLEAN DEFAULT FALSE,
  `fcm_token` VARCHAR(255),
  `profile_pic` VARCHAR(500),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- Table: blocked_user
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `blocked_user` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `blocker_id` INT NOT NULL,
  `blocked_id` INT NOT NULL,
  FOREIGN KEY (`blocker_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`blocked_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- Table: quiz_answer
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `quiz_answer` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `sleep_schedule` VARCHAR(50),
  `cleanliness` VARCHAR(50),
  `noise_level` VARCHAR(50),
  `guests` VARCHAR(50),
  `budget_max` INT,
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- Table: room
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `room` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `posted_by` INT,
  `title` VARCHAR(200) NOT NULL,
  `location` VARCHAR(200) NOT NULL,
  `price` VARCHAR(50) NOT NULL,
  `score` FLOAT,
  `gradient_color` VARCHAR(50),
  `description` TEXT,
  `amenities` VARCHAR(500),
  `photos` TEXT,
  `ai_score` FLOAT DEFAULT 0,
  `ai_hygiene` INT DEFAULT 0,
  `ai_safety` INT DEFAULT 0,
  `ai_lifestyle` INT DEFAULT 0,
  `ai_feedback` TEXT,
  `room_type` VARCHAR(50),
  `furnishing` VARCHAR(50),
  FOREIGN KEY (`posted_by`) REFERENCES `user`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- Table: compatibility_score
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `compatibility_score` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT,
  `target_user_id` INT,
  `score` INT,
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`target_user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- Table: wishlist
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `wishlist` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT,
  `room_id` INT,
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`room_id`) REFERENCES `room`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- Table: conversation
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `conversation` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_a_id` INT NOT NULL,
  `user_b_id` INT NOT NULL,
  `name_for_a` VARCHAR(100),
  `name_for_b` VARCHAR(100),
  `last_message` VARCHAR(255),
  `last_message_time` VARCHAR(50),
  `unread_a` INT DEFAULT 0,
  `unread_b` INT DEFAULT 0,
  `avatar_color` VARCHAR(50) DEFAULT 'violet',
  `is_deleted_a` BOOLEAN DEFAULT FALSE,
  `is_deleted_b` BOOLEAN DEFAULT FALSE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_a_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_b_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- Table: message
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `message` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `conversation_id` INT NOT NULL,
  `sender_id` INT NOT NULL,
  `text` TEXT,
  `media_url` VARCHAR(500),
  `media_type` VARCHAR(20),
  `time` VARCHAR(50),
  `reply_to_id` INT,
  `is_deleted_for_a` BOOLEAN DEFAULT FALSE,
  `is_deleted_for_b` BOOLEAN DEFAULT FALSE,
  `is_deleted_everyone` BOOLEAN DEFAULT FALSE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`conversation_id`) REFERENCES `conversation`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`sender_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`reply_to_id`) REFERENCES `message`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- Seed: Demo Users (plain-text passwords for dev only)
-- ─────────────────────────────────────────────────────────────
INSERT IGNORE INTO `user`
  (name, email, password, phone, location, bio, budget, age, traits, onboarding_complete)
VALUES
  ('Priya Sharma',  'priya@example.com',  'password123', '9876543210', 'Koramangala, Bangalore', 'Software engineer who loves yoga and cooking.', '20000', 25, '["Quiet","Clean","Early Bird"]', TRUE),
  ('Jordan Chen',   'jordan@example.com', 'password123', '9876543211', 'Indiranagar, Bangalore', 'Product manager, gym enthusiast.', '25000', 28, '["Active","Social","Pet-friendly"]', TRUE),
  ('Sarah Johnson', 'sarah@example.com',  'password123', '9876543212', 'HSR Layout, Bangalore',  'Designer, bookworm, loves quiet evenings.', '15000', 26, '["Introverted","Neat","Vegetarian"]', TRUE),
  ('Marcus Williams','marcus@example.com','password123', '9876543213', 'Whitefield, Bangalore',  'Data scientist, foodie, remote worker.', '30000', 30, '["Night Owl","Foodie","Clean"]', TRUE);

-- Seed: Demo Rooms
INSERT IGNORE INTO `room`
  (posted_by, title, location, price, score, gradient_color, description, amenities, ai_score, ai_hygiene, ai_safety, ai_lifestyle)
VALUES
  (1, 'Cozy Studio near Koramangala',  'Koramangala, Bangalore', '18000', 8.5, 'teal',   'A bright, well-maintained studio apartment.', 'WiFi,AC,Laundry', 8.5, 85, 70, 80),
  (2, 'Spacious 1BHK in Indiranagar',  'Indiranagar, Bangalore', '22000', 9.1, 'violet', 'Modern flat with all amenities included.',    'WiFi,Gym,Parking,AC', 9.1, 90, 85, 88),
  (3, 'Affordable PG in HSR Layout',   'HSR Layout, Bangalore',  '12000', 7.8, 'amber',  'Budget-friendly PG with meals included.',     'WiFi,Meals,Laundry', 7.8, 78, 65, 72),
  (4, 'Premium 2BHK in Whitefield',    'Whitefield, Bangalore',  '28000', 9.4, 'blue',   'Luxury flat near IT park. Fully furnished.',  'WiFi,AC,Gym,Parking,CCTV', 9.4, 92, 95, 90);

-- ─────────────────────────────────────────────────────────────
-- LOGIN CREDENTIALS (for reference)
--   priya@example.com    / password123
--   jordan@example.com   / password123
--   sarah@example.com    / password123
--   marcus@example.com   / password123
-- ─────────────────────────────────────────────────────────────
