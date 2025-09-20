import React, { useState, useEffect } from "react";

const ClientList = () => {
  const [clients, setClients] = useState([]);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetchClients();
    fetchSummary();
  }, []);

  const fetchClients = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/clients");
      const data = await response.json();
      setClients(data);
    } catch (error) {
      console.error("Error fetching clients:", error);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/analysis");
      const data = await response.json();
      setSummary(data);
    } catch (error) {
      console.error("Error fetching summary:", error);
    }
  };

  const getPriorityClass = (priority) => {
    switch (priority) {
      case "Tinggi":
        return "priority-high";
      case "Sedang":
        return "priority-medium";
      case "Rendah":
        return "priority-low";
      default:
        return "";
    }
  };

  return (
    <div className="client-list-container">
      <h2>Daftar Klien & Analisis</h2>

      {summary && (
        <div className="summary-cards">
          <div className="summary-card">
            <h3>Total Klien</h3>
            <p className="summary-value">{summary.total_clients}</p>
          </div>
          <div className="summary-card">
            <h3>Rata-rata Skor</h3>
            <p className="summary-value">{Math.round(summary.avg_score)}</p>
          </div>
          <div className="summary-card priority-high">
            <h3>Prioritas Tinggi</h3>
            <p className="summary-value">{summary.high_priority}</p>
          </div>
          <div className="summary-card priority-medium">
            <h3>Prioritas Sedang</h3>
            <p className="summary-value">{summary.medium_priority}</p>
          </div>
          <div className="summary-card priority-low">
            <h3>Prioritas Rendah</h3>
            <p className="summary-value">{summary.low_priority}</p>
          </div>
        </div>
      )}

      <div className="clients-table-container">
        <table className="clients-table">
          <thead>
            <tr>
              <th>Nama Klien</th>
              <th>Kategori Usaha</th>
              <th>Lokasi</th>
              <th>Skor Potensi</th>
              <th>Segmentasi</th>
              <th>Prioritas</th>
              <th>Rekomendasi</th>
            </tr>
          </thead>
          <tbody>
            {clients.map((client) => (
              <tr key={client.id}>
                <td>{client.nama}</td>
                <td>{client.kategori_usaha}</td>
                <td>{client.lokasi}</td>
                <td>
                  <div className="score-cell">
                    <span className="score-number">{client.skor_potensi}</span>
                    <div className="score-bar">
                      <div
                        className="score-fill"
                        style={{ width: `${client.skor_potensi}%` }}
                      ></div>
                    </div>
                  </div>
                </td>
                <td>{client.segmentasi}</td>
                <td>
                  <span
                    className={`priority-badge ${getPriorityClass(
                      client.prioritas
                    )}`}
                  >
                    {client.prioritas}
                  </span>
                </td>
                <td>{client.kategori_rekomendasi}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ClientList;
