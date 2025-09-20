# Project structure:

- backend: Python backend
- frontend: React frontend

# Maestro Suspension Web - Dokumentasi Instalasi & Menjalankan Sistem 🙌
Selamat datang di repository Maestro Suspension!
Berikut adalah panduan lengkap untuk menjalankan project React JS ini dari awal di lokal Anda.😉

 **1. Clone Repository**

```bash
git clone https://github.com/ahmadshol/digital-marketing-ai.git

cd client-analysis-system
```

**2. Install Dependencies**
***Verifikasi instalasi***

```bash
# Cek versi Python
python --version
# Output: Python 3.8.0 atau lebih tinggi

# Cek versi Node.js
node --version
# Output: v14.0.0 atau lebih tinggi

# Cek versi MySQL
mysql --version
# Output: mysql Ver 8.0.0 atau lebih tinggi

# Cek versi Git
git --version
# Output: git version 2.0.0 atau lebih tinggi
```

**3. Setup Backend **

```bash

# Masuk ke directory backend
cd backend

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Untuk Windows:
venv\Scripts\activate
# Untuk Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

**4. Setup Frontend**

```bash
# Masuk ke directory frontend (dari root project)
cd frontend

# Install dependencies
npm install

# Jika ada error permission, gunakan:
npm install --legacy-peer-deps
```

# 📃 Konfigurasi Database

**1. Buat Database Di MYSQL**

```sql
CREATE DATABASE client_analysis;
```

**2. Konfigurasi environment**

```env
# Konfigurasi Environment
FLASK_ENV=development
FLASK_DEBUG=True

# Konfigurasi Database MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=client_analysis
DB_USER=root
DB_PASSWORD=your_mysql_password

# Konfigurasi Model AI
MODEL_PATH=potensi_model.joblib
SCALER_PATH=scaler.joblib
KMEANS_PATH=kmeans_model.joblib

# Konfigurasi Feature Extraction
MIN_SAMPLE_SIZE=10
TRAINING_THRESHOLD=50

# Konfigurasi Keamanan
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Konfigurasi Server
HOST=0.0.0.0
PORT=5000
```

**3. Inisialisasi Database**

```bash
# Masuk ke MySQL
mysql -u root -p

# Jalankan script SQL
USE client_analysis;

-- Buat tabel clients
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(255) NOT NULL,
    nomor_telepon VARCHAR(20),
    kategori_usaha VARCHAR(100),
    lokasi VARCHAR(255),
    riwayat_transaksi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Buat tabel features
CREATE TABLE features (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    frekuensi_transaksi INT,
    nilai_transaksi_rata_rata DECIMAL(15,2),
    lama_usaha_bulan INT,
    luas_area_usaha DECIMAL(10,2),
    potensi_bisnis_lokasi INT,
    kepadatan_penduduk INT,
    daya_beli_lokasi INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Buat tabel analysis_results
CREATE TABLE analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    skor_potensi INT,
    segmentasi VARCHAR(50),
    prioritas VARCHAR(20),
    kategori_rekomendasi VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Buat tabel untuk CSV uploads
CREATE TABLE csv_uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    total_rows INT,
    processed_rows INT,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE csv_analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    upload_id INT,
    client_name VARCHAR(255),
    phone_number VARCHAR(20),
    business_category VARCHAR(100),
    location VARCHAR(255),
    transaction_history TEXT,
    potential_score INT,
    segmentation VARCHAR(50),
    priority VARCHAR(20),
    recommendation_category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_id) REFERENCES csv_uploads(id)
);

```

# 🚀 Menjalankan Aplikasi

**1. Jalankan Backend Server**

```bash
# Dari directory backend
cd backend

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Jalankan Flask server
python app.py
```

**Output Yang Diharapkan**

```bash
Initializing models...
Initial models trained with 1000 samples
Model R2 score: 0.923
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

**2. Jalankan Frontend Server**

```bash
# Buka terminal baru, dari directory frontend
cd frontend

# Jalankan React development server
npm start
```

**Output Yang Diharapkan**

```bash
Compiled successfully!

You can now view client-analysis-system in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.5:3000

Note that the development build is not optimized.
To create a production build, use npm run build.
```

**3. Akses Aplikasi**

> Buka Browser Dan Kunjungi: http://localhost:3000

**Format Csv Yang Benar**

***File CSV harus mengandung kolom: ***

```csv
nama,nomor_telepon,kategori_usaha,lokasi,riwayat_transaksi
Budi Santoso,08123456789,Retail,Jakarta Selatan,3 transaksi bulan lalu rata-rata 2 juta
Sari Wijaya,087654321,Fashion,Bandung Pusat,5 transaksi tahun ini nilai total 15 juta
```

