-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 20, 2025 at 12:13 PM
-- Server version: 8.0.30
-- PHP Version: 8.2.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `client_analysis`
--

-- --------------------------------------------------------

--
-- Table structure for table `analysis_results`
--

CREATE TABLE `analysis_results` (
  `id` int NOT NULL,
  `client_id` int DEFAULT NULL,
  `skor_potensi` int DEFAULT NULL,
  `segmentasi` varchar(50) DEFAULT NULL,
  `prioritas` varchar(20) DEFAULT NULL,
  `kategori_rekomendasi` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `analysis_results`
--

INSERT INTO `analysis_results` (`id`, `client_id`, `skor_potensi`, `segmentasi`, `prioritas`, `kategori_rekomendasi`, `created_at`) VALUES
(1, 1, 40, 'High-Value - Potensi Besar', 'Rendah', 'Prioritas Standar - Nurturing', '2025-09-20 08:02:57'),
(2, 2, 41, 'High-Value - Potensi Besar', 'Rendah', 'Prioritas Standar - Nurturing', '2025-09-20 09:08:58');

-- --------------------------------------------------------

--
-- Table structure for table `clients`
--

CREATE TABLE `clients` (
  `id` int NOT NULL,
  `nama` varchar(255) NOT NULL,
  `nomor_telepon` varchar(20) DEFAULT NULL,
  `kategori_usaha` varchar(100) DEFAULT NULL,
  `lokasi` varchar(255) DEFAULT NULL,
  `riwayat_transaksi` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `clients`
--

INSERT INTO `clients` (`id`, `nama`, `nomor_telepon`, `kategori_usaha`, `lokasi`, `riwayat_transaksi`, `created_at`) VALUES
(1, 'udin', '081926278837', 'Pendidikan', 'sukoharjo', '3 transaksi bulan lalu rata-rata 2 juta', '2025-09-20 08:02:57'),
(2, 'nur rohman', '098324872349', 'Fashion', 'sukoharjo', '3 transaksi bulan lalu, dan rata rata 2 juta per transaksi', '2025-09-20 09:08:58');

-- --------------------------------------------------------

--
-- Table structure for table `csv_analysis_results`
--

CREATE TABLE `csv_analysis_results` (
  `id` int NOT NULL,
  `upload_id` int DEFAULT NULL,
  `client_name` varchar(255) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `business_category` varchar(100) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `transaction_history` text,
  `potential_score` int DEFAULT NULL,
  `segmentation` varchar(50) DEFAULT NULL,
  `priority` varchar(20) DEFAULT NULL,
  `recommendation_category` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `csv_analysis_results`
--

INSERT INTO `csv_analysis_results` (`id`, `upload_id`, `client_name`, `phone_number`, `business_category`, `location`, `transaction_history`, `potential_score`, `segmentation`, `priority`, `recommendation_category`, `created_at`) VALUES
(85, 15, 'Budi Santoso', '8123456789', 'Retail', 'Jakarta Selatan', '10 transaksi dalam 3 bulan terakhir, rata-rata nilai Rp 2.500.000 per transaksi, sudah beroperasi 3 tahun, lokasi strategis di mall', 29, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(86, 15, 'Sari Wijaya', '87654321', 'Fashion', 'Bandung Pusat', '25 transaksi tahun 2024, total nilai Rp 75.000.000, pelanggan setia sejak 2021, online dan offline store', 43, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(87, 15, 'Ahmad Fauzi', '811223344', 'Makanan', 'Surabaya Barat', 'Buka 8 bulan, 5 transaksi catering corporate, nilai rata-rata Rp 3.000.000, potensi berkembang', 30, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(88, 15, 'Dewi Anggraini', '813344556', 'Kesehatan', 'Medan', 'Klinik kecantikan, 30 transaksi bulanan rata-rata Rp 1.200.000, sudah 4 tahun beroperasi', 51, 'Menengah - Stabil', 'Rendah', 'Prioritas Standard - Targeted Marketing Campaign dengan Established Business Focus', '2025-09-20 11:27:43'),
(89, 15, 'Rudi Hermawan', '821234567', 'Otomotif', 'Semarang', 'Showroom mobil, 2 transaksi besar senilai Rp 500.000.000, jaringan nasional', 25, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(90, 15, 'Linda Sari', '856789012', 'Retail', 'Yogyakarta', 'Toko souvenir, 15-20 transaksi harian, rata-rata Rp 250.000, lokasi turis', 34, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(91, 15, 'Joko Prasetyo', '815554443', 'Teknologi', 'Jakarta Pusat', 'Startup SaaS, funding Series B $2 juta, 100+ client enterprise', 44, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(92, 15, 'Maya Indah', '877778888', 'Fashion', 'Denpasar', 'Brand fashion lokal, 500+ transaksi online monthly, ekspor ke 3 negara', 28, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(93, 15, 'Agus Salim', '829876543', 'Makanan', 'Makassar', 'Restaurant keluarga, 40-50 transaksi daily, average Rp 350.000, 10 tahun experience', 70, 'Menengah - Stabil', 'Sedang', 'Prioritas Standard - Targeted Marketing Campaign dengan Established Business Focus', '2025-09-20 11:27:43'),
(94, 15, 'Rina Melati', '812340987', 'Kesehatan', 'Surakarta', 'Dental clinic, 25 appointments monthly, average Rp 1.800.000 per treatment', 23, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(95, 15, 'Bambang Sutrisno', '818765432', 'Jasa', 'Malang', 'Jasa konsultan IT, 8 project corporate, nilai total Rp 350.000.000', 21, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(96, 15, 'Citra Dewi', '854123789', 'Pendidikan', 'Bogor', 'Lembaga kursus, 120 siswa aktif, rata-rata fee Rp 2.000.000 per semester', 25, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(97, 15, 'Dodi Pratama', '823456789', 'Otomotif', 'Tangerang', 'Bengkel spesialis, 15-20 transaksi harian, sparepart dan service', 33, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(98, 15, 'Eva Nurjanah', '819988776', 'Fashion', 'Jakarta Barat', 'Boutique designer, client VIP, average transaction Rp 5.000.000', 31, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(99, 15, 'Fajar Ramadan', '878123456', 'Makanan', 'Bekasi', 'Food truck network, 10+ locations, 1000+ transactions monthly', 24, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(100, 15, 'Gita Saraswati', '812233445', 'Kesehatan', 'Depok', 'Apotek dan klinik, 50+ transaksi harian, established 8 years', 24, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(101, 15, 'Hendra Gunawan', '824567890', 'Teknologi', 'Serang', 'Software development, 12 corporate clients, annual contract basis', 24, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(102, 15, 'Ira Mandasari', '855678901', 'Retail', 'Bali', 'Souvenir and craft, tourist area, 30-40 transactions daily during season', 20, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(103, 15, 'Johan Setiawan', '813344556', 'Jasa', 'Surabaya', 'Digital marketing agency, 15 retained clients, monthly fee average Rp 15.000.000', 26, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43'),
(104, 15, 'Kartika Sari', '878456789', 'Pendidikan', 'Medan', 'International school, 200+ students, annual tuition Rp 20.000.000+', 27, 'Pemula - Potensi Berkembang', 'Rendah', 'Prioritas Nurturing - Education & Development', '2025-09-20 11:27:43');

-- --------------------------------------------------------

--
-- Table structure for table `csv_uploads`
--

CREATE TABLE `csv_uploads` (
  `id` int NOT NULL,
  `filename` varchar(255) NOT NULL,
  `original_name` varchar(255) NOT NULL,
  `total_rows` int DEFAULT NULL,
  `processed_rows` int DEFAULT NULL,
  `status` enum('pending','processing','completed','failed') DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `csv_uploads`
--

INSERT INTO `csv_uploads` (`id`, `filename`, `original_name`, `total_rows`, `processed_rows`, `status`, `created_at`) VALUES
(15, '2139831c8a7d495a83d633f4aefcc426_template_klien.csv', 'template_klien.csv', 20, 20, 'completed', '2025-09-20 11:27:39');

-- --------------------------------------------------------

--
-- Table structure for table `features`
--

CREATE TABLE `features` (
  `id` int NOT NULL,
  `client_id` int DEFAULT NULL,
  `frekuensi_transaksi` int DEFAULT NULL,
  `nilai_transaksi_rata_rata` decimal(15,2) DEFAULT NULL,
  `lama_usaha_bulan` int DEFAULT NULL,
  `luas_area_usaha` decimal(10,2) DEFAULT NULL,
  `potensi_bisnis_lokasi` int DEFAULT NULL,
  `kepadatan_penduduk` int DEFAULT NULL,
  `daya_beli_lokasi` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `features`
--

INSERT INTO `features` (`id`, `client_id`, `frekuensi_transaksi`, `nilai_transaksi_rata_rata`, `lama_usaha_bulan`, `luas_area_usaha`, `potensi_bisnis_lokasi`, `kepadatan_penduduk`, `daya_beli_lokasi`, `created_at`) VALUES
(1, 1, 1, '2500000.00', 12, '50.00', 5, 5, 5, '2025-09-20 08:02:57'),
(2, 2, 2, '2500000.00', 12, '50.00', 5, 5, 5, '2025-09-20 09:08:58');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `analysis_results`
--
ALTER TABLE `analysis_results`
  ADD PRIMARY KEY (`id`),
  ADD KEY `client_id` (`client_id`);

--
-- Indexes for table `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `csv_analysis_results`
--
ALTER TABLE `csv_analysis_results`
  ADD PRIMARY KEY (`id`),
  ADD KEY `upload_id` (`upload_id`);

--
-- Indexes for table `csv_uploads`
--
ALTER TABLE `csv_uploads`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `features`
--
ALTER TABLE `features`
  ADD PRIMARY KEY (`id`),
  ADD KEY `client_id` (`client_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `analysis_results`
--
ALTER TABLE `analysis_results`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `clients`
--
ALTER TABLE `clients`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `csv_analysis_results`
--
ALTER TABLE `csv_analysis_results`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=105;

--
-- AUTO_INCREMENT for table `csv_uploads`
--
ALTER TABLE `csv_uploads`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `features`
--
ALTER TABLE `features`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `analysis_results`
--
ALTER TABLE `analysis_results`
  ADD CONSTRAINT `analysis_results_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`);

--
-- Constraints for table `csv_analysis_results`
--
ALTER TABLE `csv_analysis_results`
  ADD CONSTRAINT `csv_analysis_results_ibfk_1` FOREIGN KEY (`upload_id`) REFERENCES `csv_uploads` (`id`);

--
-- Constraints for table `features`
--
ALTER TABLE `features`
  ADD CONSTRAINT `features_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
