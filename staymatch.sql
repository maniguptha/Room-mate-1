-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 10, 2026 at 11:14 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `staymatch`
--

-- --------------------------------------------------------

--
-- Table structure for table `blocked_user`
--

CREATE TABLE `blocked_user` (
  `id` int(11) NOT NULL,
  `blocker_id` int(11) NOT NULL,
  `blocked_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `compatibility_score`
--

CREATE TABLE `compatibility_score` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `target_user_id` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `conversation`
--

CREATE TABLE `conversation` (
  `id` int(11) NOT NULL,
  `user_a_id` int(11) NOT NULL,
  `user_b_id` int(11) NOT NULL,
  `name_for_a` varchar(100) DEFAULT NULL,
  `name_for_b` varchar(100) DEFAULT NULL,
  `last_message` varchar(255) DEFAULT NULL,
  `last_message_time` varchar(50) DEFAULT NULL,
  `unread_a` int(11) DEFAULT NULL,
  `unread_b` int(11) DEFAULT NULL,
  `avatar_color` varchar(50) DEFAULT NULL,
  `is_deleted_a` tinyint(1) DEFAULT NULL,
  `is_deleted_b` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `message`
--

CREATE TABLE `message` (
  `id` int(11) NOT NULL,
  `conversation_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `text` text DEFAULT NULL,
  `media_url` varchar(500) DEFAULT NULL,
  `media_type` varchar(20) DEFAULT NULL,
  `time` varchar(50) DEFAULT NULL,
  `reply_to_id` int(11) DEFAULT NULL,
  `is_deleted_for_a` tinyint(1) DEFAULT NULL,
  `is_deleted_for_b` tinyint(1) DEFAULT NULL,
  `is_deleted_everyone` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quiz_answer`
--

CREATE TABLE `quiz_answer` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `sleep_schedule` varchar(50) DEFAULT NULL,
  `cleanliness` varchar(50) DEFAULT NULL,
  `noise_level` varchar(50) DEFAULT NULL,
  `guests` varchar(50) DEFAULT NULL,
  `budget_max` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `room`
--

CREATE TABLE `room` (
  `id` int(11) NOT NULL,
  `posted_by` int(11) DEFAULT NULL,
  `title` varchar(200) NOT NULL,
  `location` varchar(200) NOT NULL,
  `price` varchar(50) NOT NULL,
  `score` float DEFAULT NULL,
  `gradient_color` varchar(50) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `amenities` varchar(500) DEFAULT NULL,
  `photos` text DEFAULT NULL,
  `ai_score` float DEFAULT NULL,
  `ai_hygiene` int(11) DEFAULT NULL,
  `ai_safety` int(11) DEFAULT NULL,
  `ai_lifestyle` int(11) DEFAULT NULL,
  `ai_feedback` text DEFAULT NULL,
  `room_type` varchar(50) DEFAULT NULL,
  `furnishing` varchar(50) DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `room`
--

INSERT INTO `room` (`id`, `posted_by`, `title`, `location`, `price`, `score`, `gradient_color`, `description`, `amenities`, `photos`, `ai_score`, `ai_hygiene`, `ai_safety`, `ai_lifestyle`, `ai_feedback`, `room_type`, `furnishing`, `latitude`, `longitude`) VALUES
(1, 1, 'Sunny Studio in SoMa', 'SoMa, San Francisco', '₹18,000', 9.4, 'amber', 'Beautiful naturally lit studio near tech hubs.', 'WiFi,Laundry,Gym', NULL, 0, 0, 0, 0, NULL, NULL, NULL, 0, 0),
(2, 2, 'Modern Loft', 'Mission District', '₹24,000', 8.8, 'purple', 'Spacious loft with high ceilings.', 'WiFi,AC,Parking', NULL, 0, 0, 0, 0, NULL, NULL, NULL, 0, 0),
(3, 3, 'Cozy Private Room', 'Hayes Valley', '₹16,000', 9.1, 'blue', 'Quiet room in a 3BHK flat.', 'WiFi,Kitchen,Balcony', NULL, 0, 0, 0, 0, NULL, NULL, NULL, 0, 0),
(4, 4, 'Shared Apartment', 'Sunset District', '₹12,000', 7.5, 'green', 'Budget friendly shared space.', 'WiFi,Kitchen', NULL, 0, 0, 0, 0, NULL, NULL, NULL, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `room_rating`
--

CREATE TABLE `room_rating` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `rating` float NOT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `location` varchar(200) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `budget` varchar(50) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `traits` text DEFAULT NULL,
  `onboarding_complete` tinyint(1) DEFAULT NULL,
  `fcm_token` varchar(255) DEFAULT NULL,
  `profile_pic` varchar(500) DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `reset_otp` varchar(10) DEFAULT NULL,
  `reset_otp_expiry` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `name`, `email`, `password`, `phone`, `location`, `bio`, `budget`, `age`, `traits`, `onboarding_complete`, `fcm_token`, `profile_pic`, `latitude`, `longitude`, `created_at`, `reset_otp`, `reset_otp_expiry`) VALUES
(1, 'Priya Sharma', 'priya@example.com', 'password123', NULL, 'SoMa, SF', 'Looking for a shared flat in SoMa.', '₹18,000/mo', 24, 'Early Bird,Clean,WFH', 1, NULL, NULL, 0, 0, '2026-04-08 04:52:54', NULL, NULL),
(2, 'Jordan Mike', 'jordan@example.com', 'password123', NULL, 'Mission District', 'Techie looking for a modern loft.', '₹22,000/mo', 26, 'Night Owl,Social,Gym', 1, NULL, NULL, 0, 0, '2026-04-08 04:52:54', NULL, NULL),
(3, 'Sarah Long', 'sarah@example.com', 'password123', NULL, 'Hayes Valley', 'Peaceful vibes only.', '₹20,000/mo', 23, 'Quiet,Pet Friendly,Reader', 1, NULL, NULL, 0, 0, '2026-04-08 04:52:54', NULL, NULL),
(4, 'Marcus Tan', 'marcus@example.com', 'password123', NULL, 'Sunset District', 'Budget student living.', '₹12,000/mo', 28, 'Student,Gamer,Night Owl', 1, NULL, NULL, 0, 0, '2026-04-08 04:52:54', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `wishlist`
--

CREATE TABLE `wishlist` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `room_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `blocked_user`
--
ALTER TABLE `blocked_user`
  ADD PRIMARY KEY (`id`),
  ADD KEY `blocker_id` (`blocker_id`),
  ADD KEY `blocked_id` (`blocked_id`);

--
-- Indexes for table `compatibility_score`
--
ALTER TABLE `compatibility_score`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `target_user_id` (`target_user_id`);

--
-- Indexes for table `conversation`
--
ALTER TABLE `conversation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_a_id` (`user_a_id`),
  ADD KEY `user_b_id` (`user_b_id`);

--
-- Indexes for table `message`
--
ALTER TABLE `message`
  ADD PRIMARY KEY (`id`),
  ADD KEY `conversation_id` (`conversation_id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `reply_to_id` (`reply_to_id`);

--
-- Indexes for table `quiz_answer`
--
ALTER TABLE `quiz_answer`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `room`
--
ALTER TABLE `room`
  ADD PRIMARY KEY (`id`),
  ADD KEY `posted_by` (`posted_by`);

--
-- Indexes for table `room_rating`
--
ALTER TABLE `room_rating`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `room_id` (`room_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `room_id` (`room_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `blocked_user`
--
ALTER TABLE `blocked_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `compatibility_score`
--
ALTER TABLE `compatibility_score`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `conversation`
--
ALTER TABLE `conversation`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `message`
--
ALTER TABLE `message`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `quiz_answer`
--
ALTER TABLE `quiz_answer`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `room`
--
ALTER TABLE `room`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `room_rating`
--
ALTER TABLE `room_rating`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `wishlist`
--
ALTER TABLE `wishlist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `blocked_user`
--
ALTER TABLE `blocked_user`
  ADD CONSTRAINT `blocked_user_ibfk_1` FOREIGN KEY (`blocker_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `blocked_user_ibfk_2` FOREIGN KEY (`blocked_id`) REFERENCES `user` (`id`);

--
-- Constraints for table `compatibility_score`
--
ALTER TABLE `compatibility_score`
  ADD CONSTRAINT `compatibility_score_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `compatibility_score_ibfk_2` FOREIGN KEY (`target_user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `conversation`
--
ALTER TABLE `conversation`
  ADD CONSTRAINT `conversation_ibfk_1` FOREIGN KEY (`user_a_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `conversation_ibfk_2` FOREIGN KEY (`user_b_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `message`
--
ALTER TABLE `message`
  ADD CONSTRAINT `message_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `conversation` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `message_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `message_ibfk_3` FOREIGN KEY (`reply_to_id`) REFERENCES `message` (`id`);

--
-- Constraints for table `quiz_answer`
--
ALTER TABLE `quiz_answer`
  ADD CONSTRAINT `quiz_answer_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Constraints for table `room`
--
ALTER TABLE `room`
  ADD CONSTRAINT `room_ibfk_1` FOREIGN KEY (`posted_by`) REFERENCES `user` (`id`);

--
-- Constraints for table `room_rating`
--
ALTER TABLE `room_rating`
  ADD CONSTRAINT `room_rating_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `room_rating_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `room` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `room` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
