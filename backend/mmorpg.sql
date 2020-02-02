-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 31, 2020 at 08:49 AM
-- Server version: 5.7.29-0ubuntu0.16.04.1
-- PHP Version: 7.0.33-0ubuntu0.16.04.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `mmorpg`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

CREATE TABLE `accounts` (
  `id` int(11) NOT NULL,
  `login` varchar(32) NOT NULL,
  `pass` varchar(128) NOT NULL,
  `last_login` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`id`, `login`, `pass`, `last_login`) VALUES
(1, '123', '6a8e7a542a4bed02e5d2920d7c5458a34c6d75377a4b2c5d2a96b5c152e52aa8f22e24e7d85cc6c47a01c5e7ee5df02b22e296b5ae849b42372a86314135912e', '2020-01-19 15:16:31'),
(2, '', 'ee26b0dd4af7e749aa1a8ee3c10ae9923f618980772e473f8819a5d4940e0db27ac185f8a0e1d5f84f88bc887fd67b143732c304cc5fa9ad8e6f57f50028a8ff', '2020-01-20 21:22:37'),
(9, 'new3', '69b8982b4d0a0dab66aa92a2e4f8eb6f3f8f0b5f9d902a127df556a55426523b45596f6471e477f02f4061acb88af461b928aa468dd1aa5a3faaa663e4d60379', '2020-01-23 18:10:26'),
(10, 'checkChar', '6a8e7a542a4bed02e5d2920d7c5458a34c6d75377a4b2c5d2a96b5c152e52aa8f22e24e7d85cc6c47a01c5e7ee5df02b22e296b5ae849b42372a86314135912e', '2020-01-25 14:23:59'),
(11, 'newChar', '6a8e7a542a4bed02e5d2920d7c5458a34c6d75377a4b2c5d2a96b5c152e52aa8f22e24e7d85cc6c47a01c5e7ee5df02b22e296b5ae849b42372a86314135912e', '2020-01-25 14:34:30'),
(12, 'testnewacc', '6a8e7a542a4bed02e5d2920d7c5458a34c6d75377a4b2c5d2a96b5c152e52aa8f22e24e7d85cc6c47a01c5e7ee5df02b22e296b5ae849b42372a86314135912e', '2020-01-25 21:19:40'),
(13, 'testpos', '6a8e7a542a4bed02e5d2920d7c5458a34c6d75377a4b2c5d2a96b5c152e52aa8f22e24e7d85cc6c47a01c5e7ee5df02b22e296b5ae849b42372a86314135912e', '2020-01-26 13:30:59'),
(14, 'testclic', '7791033ef951f8b51a2c21b7a99a0b5260888d5c8301e71926275a65294811024239257665085042a139789a464955326df3c1213c18d88e07d8817e71c073d4', '2020-01-27 21:28:33');

-- --------------------------------------------------------

--
-- Table structure for table `chars`
--

CREATE TABLE `chars` (
  `id` int(11) NOT NULL,
  `acc_id` int(11) NOT NULL,
  `charname` varchar(32) NOT NULL,
  `race_id` smallint(6) NOT NULL,
  `portrait_id` int(11) NOT NULL,
  `guild_id` int(11) NOT NULL DEFAULT '0',
  `level` smallint(6) NOT NULL DEFAULT '1',
  `locx` int(11) NOT NULL,
  `locy` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `chars`
--

INSERT INTO `chars` (`id`, `acc_id`, `charname`, `race_id`, `portrait_id`, `guild_id`, `level`, `locx`, `locy`) VALUES
(1, 1, '123', 1, 1001, 0, 1, 3, 0),
(2, 11, 'newchar', 2, 2001, 0, 1, 0, 3),
(3, 11, 'xtest', 1, 1001, 0, 1, 3, 0),
(4, 12, 'xd', 1, 1001, 0, 1, 3, 0),
(5, 13, 'orc1', 2, 2001, 0, 1, 0, 3);

-- --------------------------------------------------------

--
-- Table structure for table `guilds`
--

CREATE TABLE `guilds` (
  `id` int(11) NOT NULL,
  `guild_name` varchar(128) NOT NULL,
  `guild_leader` int(11) NOT NULL,
  `chat_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `hist_messages`
--

CREATE TABLE `hist_messages` (
  `id` int(11) NOT NULL,
  `chat_id` int(11) NOT NULL,
  `char_id` int(11) NOT NULL,
  `message` varchar(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `hist_sessions`
--

CREATE TABLE `hist_sessions` (
  `id` int(11) NOT NULL,
  `login_id` int(11) NOT NULL,
  `token` varchar(512) NOT NULL,
  `char_id` int(11) NOT NULL,
  `created` timestamp NULL DEFAULT NULL,
  `destroyed` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `maps`
--

CREATE TABLE `maps` (
  `id` int(11) NOT NULL,
  `map_data` longtext NOT NULL,
  `comment` varchar(128) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `login` (`login`);

--
-- Indexes for table `chars`
--
ALTER TABLE `chars`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nickname` (`charname`);

--
-- Indexes for table `guilds`
--
ALTER TABLE `guilds`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `hist_messages`
--
ALTER TABLE `hist_messages`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `hist_sessions`
--
ALTER TABLE `hist_sessions`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `maps`
--
ALTER TABLE `maps`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts`
--
ALTER TABLE `accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;
--
-- AUTO_INCREMENT for table `chars`
--
ALTER TABLE `chars`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT for table `guilds`
--
ALTER TABLE `guilds`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `hist_messages`
--
ALTER TABLE `hist_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `hist_sessions`
--
ALTER TABLE `hist_sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `maps`
--
ALTER TABLE `maps`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
