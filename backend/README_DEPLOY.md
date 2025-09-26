# Digital Marketing AI Backend (Flask)

## Setup Environment

1. **Copy file .env.example menjadi .env**
   
   Untuk development (local):
   ```
   cp .env.example .env
   ```
   Atau buat manual file `.env` di folder backend dan isi sesuai kebutuhan.

2. **Jalankan backend**
   ```
   pip install -r requirements.txt
   python app.py
   ```
   atau untuk production (misal pakai gunicorn):
   ```
   gunicorn -b 0.0.0.0:5000 app:app
   ```

3. **Deploy ke server/hosting sesuai kebutuhan**
   - Pastikan file `.env` sudah diisi dan tidak di-commit ke git.
   - Untuk Heroku/Render, pastikan variabel environment diatur di dashboard.

## Catatan
- Semua konfigurasi (database, secret key, model path, dsb) diatur lewat file `.env`.
- Jangan commit file `.env` ke repository publik.
- Untuk production, gunakan `SECRET_KEY` yang kuat dan unik.
