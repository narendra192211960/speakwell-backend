-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 07, 2026 at 05:36 AM
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
-- Database: `speakwell`
--

-- --------------------------------------------------------

--
-- Table structure for table `notification_logs`
--

CREATE TABLE `notification_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `type` varchar(100) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `sent_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` varchar(20) DEFAULT 'sent'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notification_logs`
--

INSERT INTO `notification_logs` (`id`, `user_id`, `type`, `message`, `sent_at`, `status`) VALUES
(8, 35, 'streak_1', 'Hello Narendra,\n\n🔥 Amazing! Your streak is now 1 days. Keep going!\n\nCurrent Streak: 1 days\n\n– AI Speech Rehabilitation Assistant', '2026-03-03 05:09:00', 'sent');

-- --------------------------------------------------------

--
-- Table structure for table `notification_preferences`
--

CREATE TABLE `notification_preferences` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `daily_practice_reminder` tinyint(1) DEFAULT 0,
  `streak_milestone` tinyint(1) DEFAULT 0,
  `weekly_progress` tinyint(1) DEFAULT 0,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notification_preferences`
--

INSERT INTO `notification_preferences` (`id`, `user_id`, `daily_practice_reminder`, `streak_milestone`, `weekly_progress`, `updated_at`) VALUES
(56, 35, 1, 1, 0, '2026-03-03 03:33:18');

-- --------------------------------------------------------

--
-- Table structure for table `practice_attempts`
--

CREATE TABLE `practice_attempts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `expected_sentence` text DEFAULT NULL,
  `recognized_text` text DEFAULT NULL,
  `accuracy` int(11) DEFAULT NULL,
  `feedback_tip` text DEFAULT NULL,
  `attempt_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `feedback` text DEFAULT NULL,
  `date_time` datetime DEFAULT NULL,
  `session_id` varchar(100) DEFAULT 'legacy_session',
  `exercise_name` varchar(100) DEFAULT 'General Practice'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `practice_attempts`
--

INSERT INTO `practice_attempts` (`id`, `user_id`, `expected_sentence`, `recognized_text`, `accuracy`, `feedback_tip`, `attempt_date`, `feedback`, `date_time`, `session_id`, `exercise_name`) VALUES
(337, 35, 'eat eat eat', 'eat eat', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-03 05:08:56', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-03 10:38:56', '4b81385f-c51c-4f12-badf-96ee1a6154fe', 'Basic Vowel Sounds'),
(338, 35, 'it it it', 'No speech detected', 0, 'No speech detected. Please try again.', '2026-03-03 05:09:08', 'No speech detected. Please try again.', '2026-03-03 10:39:08', '4b81385f-c51c-4f12-badf-96ee1a6154fe', 'Basic Vowel Sounds'),
(339, 35, 'ate ate ate', '8888', 0, 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-03 05:09:18', 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-03 10:39:18', '4b81385f-c51c-4f12-badf-96ee1a6154fe', 'Basic Vowel Sounds'),
(340, 35, 'at at at', 'No speech detected', 0, 'No speech detected. Please try again.', '2026-03-03 05:09:25', 'No speech detected. Please try again.', '2026-03-03 10:39:26', '4b81385f-c51c-4f12-badf-96ee1a6154fe', 'Basic Vowel Sounds'),
(341, 35, 'hot hot hot', 'hot hot hot', 100, 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-03 05:09:32', 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-03 10:39:32', '4b81385f-c51c-4f12-badf-96ee1a6154fe', 'Basic Vowel Sounds'),
(342, 35, 'out out out', 'out out out out out out', 100, 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-03 05:09:38', 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-03 10:39:38', '4b81385f-c51c-4f12-badf-96ee1a6154fe', 'Basic Vowel Sounds'),
(343, 35, 'boot boot boot', 'boot boot', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-03 05:09:44', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-03 10:39:44', '4b81385f-c51c-4f12-badf-96ee1a6154fe', 'Basic Vowel Sounds'),
(344, 35, 'but but but', 'Battu Battu Battu', 0, 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-03 05:09:50', 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-03 10:39:50', '4b81385f-c51c-4f12-badf-96ee1a6154fe', 'Basic Vowel Sounds'),
(353, 35, 'Choose your own topic and then speak atleast 3 minutes', 'hello this is Narendra Kumar and I am very great examples is computer science engineering and successful of Engineering and also CGPA in 10 completed all the', 15, 'Good effort! You spoke for 0m 28s. Keep practicing to reach the 3-minute mark.', '2026-03-04 03:03:55', 'Good effort! You spoke for 0m 28s. Keep practicing to reach the 3-minute mark.', '2026-03-04 08:33:54', '0c2257f9-7b33-4898-bfab-8e30d32fdc25', 'Self Exercise'),
(354, 35, 'I wake up early. I drink water and eat breakfast. I start my day with a smile.', 'wake up early I drink water and eat breakup breakfast I start my day with a smell', 76, 'Good attempt! Focus on clarity and stress on difficult words.', '2026-03-05 03:01:48', 'Good attempt! Focus on clarity and stress on difficult words.', '2026-03-05 08:31:47', '5090f82f-3f27-4b2a-9ec0-298d00c4d550', 'Paragraph Reading'),
(355, 35, 'I went to the market with my friend. We bought milk and fruits. It was a good day.', 'I went to the market with my friend who got milk and fruits it was a good day', 72, 'Good attempt! Focus on clarity and stress on difficult words.', '2026-03-05 03:02:03', 'Good attempt! Focus on clarity and stress on difficult words.', '2026-03-05 08:32:02', '5090f82f-3f27-4b2a-9ec0-298d00c4d550', 'Paragraph Reading'),
(356, 35, 'I practice my speech every day. I speak clearly and slowly. This helps me improve.', 'I practice my switch everyday I speak clearly under slowly this help me to improve', 53, 'Needs improvement. Practice word-by-word pronunciation.', '2026-03-05 03:02:15', 'Needs improvement. Practice word-by-word pronunciation.', '2026-03-05 08:32:14', '5090f82f-3f27-4b2a-9ec0-298d00c4d550', 'Paragraph Reading'),
(357, 35, 'We planned a short trip. The weather was cool and pleasant. We enjoyed a lot.', 'we planned a Short trip the weather was cool and pleasant we enjoyed a lot', 80, 'Very good job! Minor pronunciation improvements will make it perfect.', '2026-03-05 03:02:29', 'Very good job! Minor pronunciation improvements will make it perfect.', '2026-03-05 08:32:28', '5090f82f-3f27-4b2a-9ec0-298d00c4d550', 'Paragraph Reading'),
(358, 35, 'Helping others is a good habit. I speak kindly. Good words make people happy.', 'helping others is a good habit I speak kindly good words make people happy', 78, 'Good attempt! Focus on clarity and stress on difficult words.', '2026-03-05 03:02:41', 'Good attempt! Focus on clarity and stress on difficult words.', '2026-03-05 08:32:41', '5090f82f-3f27-4b2a-9ec0-298d00c4d550', 'Paragraph Reading'),
(359, 35, 'One One One', 'one one one one', 100, 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 03:14:25', 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 08:44:25', '858307bb-4be5-4869-930d-4f2c343ce0da', 'Numbers 1-10'),
(360, 35, 'Two Two Two', 'two two two', 100, 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 03:16:37', 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 08:46:36', '858307bb-4be5-4869-930d-4f2c343ce0da', 'Numbers 1-10'),
(361, 35, 'Three Three Three', 'three three', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:16:43', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:46:43', '858307bb-4be5-4869-930d-4f2c343ce0da', 'Numbers 1-10'),
(362, 35, 'Four Four Four', 'No speech detected', 0, 'No speech detected. Please try again.', '2026-03-06 03:16:53', 'No speech detected. Please try again.', '2026-03-06 08:46:53', '858307bb-4be5-4869-930d-4f2c343ce0da', 'Numbers 1-10'),
(363, 35, 'Five Five Five', 'five five five', 100, 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 03:16:58', 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 08:46:58', '858307bb-4be5-4869-930d-4f2c343ce0da', 'Numbers 1-10'),
(364, 35, 'Six Six Six', 'No speech detected', 0, 'No speech detected. Please try again.', '2026-03-06 03:17:08', 'No speech detected. Please try again.', '2026-03-06 08:47:07', '858307bb-4be5-4869-930d-4f2c343ce0da', 'Numbers 1-10'),
(365, 35, 'Seven Seven Seven', 'seven seven', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:17:14', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:47:14', '858307bb-4be5-4869-930d-4f2c343ce0da', 'Numbers 1-10'),
(366, 35, 'Eight Eight Eight', 'eight eight', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:17:21', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:47:20', '858307bb-4be5-4869-930d-4f2c343ce0da', 'Numbers 1-10'),
(367, 35, 'Nine Nine Nine', 'No speech detected', 0, 'No speech detected. Please try again.', '2026-03-06 03:17:31', 'No speech detected. Please try again.', '2026-03-06 08:47:31', '858307bb-4be5-4869-930d-4f2c343ce0da', 'Numbers 1-10'),
(368, 35, 'eat eat eat', 'ET eat', 33, 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-06 03:19:12', 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-06 08:49:11', '306c3c37-8195-40ff-a4d5-22d7001fd41a', 'Basic Vowel Sounds'),
(369, 35, 'it it it', 'it it', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:19:18', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:49:18', '306c3c37-8195-40ff-a4d5-22d7001fd41a', 'Basic Vowel Sounds'),
(370, 35, 'ate ate ate', 'eight eight eight', 0, 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-06 03:19:25', 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-06 08:49:24', '306c3c37-8195-40ff-a4d5-22d7001fd41a', 'Basic Vowel Sounds'),
(371, 35, 'at at at', 'at at', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:19:33', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:49:32', '306c3c37-8195-40ff-a4d5-22d7001fd41a', 'Basic Vowel Sounds'),
(372, 35, 'hot hot hot', 'hot hot', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:19:37', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:49:37', '306c3c37-8195-40ff-a4d5-22d7001fd41a', 'Basic Vowel Sounds'),
(373, 35, 'out out out', 'out out out', 100, 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 03:19:42', 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 08:49:42', '306c3c37-8195-40ff-a4d5-22d7001fd41a', 'Basic Vowel Sounds'),
(374, 35, 'boot boot boot', 'boot boot', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:19:48', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:49:47', '306c3c37-8195-40ff-a4d5-22d7001fd41a', 'Basic Vowel Sounds'),
(375, 35, 'but but but', 'but but', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:19:53', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:49:53', '306c3c37-8195-40ff-a4d5-22d7001fd41a', 'Basic Vowel Sounds'),
(376, 35, 'eat eat eat', 'No speech detected', 0, 'No speech detected. Please try again.', '2026-03-06 03:25:53', 'No speech detected. Please try again.', '2026-03-06 08:55:52', 'd6ad21aa-1704-46d7-8ce3-e4728252d428', 'Basic Vowel Sounds'),
(377, 35, 'it it it', 'Ittu Ittu it', 33, 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-06 03:25:59', 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-06 08:55:59', 'd6ad21aa-1704-46d7-8ce3-e4728252d428', 'Basic Vowel Sounds'),
(378, 35, 'ice ice ice', 'ice ice', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:26:05', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:56:05', 'd6ad21aa-1704-46d7-8ce3-e4728252d428', 'Basic Vowel Sounds'),
(379, 35, 'at at at', 'at at', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:26:11', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:56:11', 'd6ad21aa-1704-46d7-8ce3-e4728252d428', 'Basic Vowel Sounds'),
(380, 35, 'hot hot hot', 'hot hot', 66, 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 03:26:17', 'Fair effort. Try slowing down and pronouncing each word carefully.', '2026-03-06 08:56:16', 'd6ad21aa-1704-46d7-8ce3-e4728252d428', 'Basic Vowel Sounds'),
(381, 35, 'out out out', 'out out out', 100, 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 03:26:23', 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 08:56:22', 'd6ad21aa-1704-46d7-8ce3-e4728252d428', 'Basic Vowel Sounds'),
(382, 35, 'boot boot boot', 'बहुत-बहुत', 0, 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-06 03:26:33', 'Keep practicing. Try repeating the sentence slowly and clearly.', '2026-03-06 08:56:33', 'd6ad21aa-1704-46d7-8ce3-e4728252d428', 'Basic Vowel Sounds'),
(383, 35, 'but but but', 'but but but', 100, 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 03:26:39', 'Outstanding performance! Your pronunciation is excellent. Keep maintaining this consistency.', '2026-03-06 08:56:39', 'd6ad21aa-1704-46d7-8ce3-e4728252d428', 'Basic Vowel Sounds');

-- --------------------------------------------------------

--
-- Table structure for table `schedules`
--

CREATE TABLE `schedules` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `scheduled_date` varchar(50) DEFAULT NULL,
  `scheduled_time` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password` varchar(200) NOT NULL,
  `phone_number` varchar(13) NOT NULL,
  `age` int(10) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `start_date` date DEFAULT NULL,
  `profile_picture` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `phone_number`, `age`, `created_at`, `start_date`, `profile_picture`) VALUES
(35, 'Nani', 'ambatinarendra610@gmail.com', 'scrypt:32768:8:1$vsrSU6sLpLTfQQoy$c67bcf91680eb13c67491a05628c7780b1d72505724757b9cf1e5224815fcc2b68523e640a6be6d06ca7d899b279111270c85a12a3b23820f4060144b1949fb6', '9182424714', 26, '2026-03-03 03:32:12', '2026-03-03', 'http://10.190.77.173:5000/uploads/user_35_profile_pic_1772769921604.jpg');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `notification_logs`
--
ALTER TABLE `notification_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `notification_preferences`
--
ALTER TABLE `notification_preferences`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `practice_attempts`
--
ALTER TABLE `practice_attempts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `schedules`
--
ALTER TABLE `schedules`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `notification_logs`
--
ALTER TABLE `notification_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `notification_preferences`
--
ALTER TABLE `notification_preferences`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=62;

--
-- AUTO_INCREMENT for table `practice_attempts`
--
ALTER TABLE `practice_attempts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=384;

--
-- AUTO_INCREMENT for table `schedules`
--
ALTER TABLE `schedules`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=48;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `notification_logs`
--
ALTER TABLE `notification_logs`
  ADD CONSTRAINT `notification_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notification_preferences`
--
ALTER TABLE `notification_preferences`
  ADD CONSTRAINT `notification_preferences_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `practice_attempts`
--
ALTER TABLE `practice_attempts`
  ADD CONSTRAINT `practice_attempts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `schedules`
--
ALTER TABLE `schedules`
  ADD CONSTRAINT `schedules_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
