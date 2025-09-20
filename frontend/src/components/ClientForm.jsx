import React, { useState } from "react";

const ClientForm = ({ onClientAdded }) => {
  const [formData, setFormData] = useState({
    nama: "",
    nomor_telepon: "",
    kategori_usaha: "",
    lokasi: "",
    riwayat_transaksi: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/clients", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      setResult(data.analysis);

      if (onClientAdded) {
        onClientAdded();
      }

      // Reset form
      setFormData({
        nama: "",
        nomor_telepon: "",
        kategori_usaha: "",
        lokasi: "",
        riwayat_transaksi: "",
      });
    } catch (error) {
      console.error("Error adding client:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Tambah Klien Baru</h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Nama Klien:</label>
          <input
            type="text"
            name="nama"
            value={formData.nama}
            onChange={handleChange}
            required
            placeholder="Nama lengkap klien"
          />
        </div>

        <div className="form-group">
          <label>Nomor Telepon:</label>
          <input
            type="tel"
            name="nomor_telepon"
            value={formData.nomor_telepon}
            onChange={handleChange}
            placeholder="081234567890"
          />
        </div>

        <div className="form-group">
          <label>Kategori Usaha:</label>
          <select
            name="kategori_usaha"
            value={formData.kategori_usaha}
            onChange={handleChange}
            required
          >
            <option value="">Pilih Kategori</option>
            <option value="Retail">Retail</option>
            <option value="Makanan">Makanan & Restoran</option>
            <option value="Fashion">Fashion</option>
            <option value="Teknologi">Teknologi</option>
            <option value="Jasa">Jasa</option>
            <option value="Kesehatan">Kesehatan & Kecantikan</option>
            <option value="Pendidikan">Pendidikan</option>
            <option value="Otomotif">Otomotif</option>
          </select>
        </div>

        <div className="form-group">
          <label>Lokasi:</label>
          <input
            type="text"
            name="lokasi"
            value={formData.lokasi}
            onChange={handleChange}
            required
            placeholder="Contoh: Jakarta Selatan, Bandung Pusat, dll."
          />
        </div>

        <div className="form-group">
          <label>Riwayat Transaksi:</label>
          <textarea
            name="riwayat_transaksi"
            value={formData.riwayat_transaksi}
            onChange={handleChange}
            rows="4"
            placeholder="Deskripsi riwayat transaksi, contoh: '3 transaksi bulan lalu, rata-rata nilai 2 juta, sudah berjalan 2 tahun'"
          ></textarea>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Menganalisis..." : "Tambah & Analisis Klien"}
        </button>
      </form>

      {result && (
        <div className="analysis-result">
          <h3>Hasil Analisis</h3>
          <div className="score-display">
            <div className="score-circle">
              <span className="score-value">{result.skor_potensi}</span>
              <span className="score-label">Skor Potensi</span>
            </div>
          </div>

          <div className="result-details">
            <p>
              <strong>Segmentasi:</strong> {result.segmentasi}
            </p>
            <p>
              <strong>Prioritas:</strong>
              <span
                className={`priority-badge ${result.prioritas.toLowerCase()}`}
              >
                {result.prioritas}
              </span>
            </p>
            <p>
              <strong>Rekomendasi:</strong> {result.kategori_rekomendasi}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientForm;
