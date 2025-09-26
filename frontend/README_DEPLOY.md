# Digital Marketing AI Frontend

## Setup Environment

1. **Copy file .env.example menjadi .env**
   
   Untuk development (local):
   ```
   cp .env.example .env
   ```
   Atau buat manual file `.env` di folder frontend:
   ```
   VITE_API_BASE_URL=http://localhost:5000
   ```

   Untuk production, isi dengan URL backend Anda:
   ```
   VITE_API_BASE_URL=https://your-backend-url.com
   ```

2. **Jalankan build**
   ```
   npm install
   npm run build
   ```

3. **Deploy hasil build (folder dist/) ke hosting static (Vercel, Netlify, dsb)**

## Catatan
- Semua endpoint API akan otomatis menggunakan URL dari `VITE_API_BASE_URL`.
- Jika environment variable tidak di-set, maka fallback ke `http://localhost:5000`.
- Pastikan backend Flask Anda sudah di-deploy dan dapat diakses dari domain frontend.
