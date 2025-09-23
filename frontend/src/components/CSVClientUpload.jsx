import React, { useState, useEffect } from "react";

const CSVClientUpload = () => {
  const [file, setFile] = useState(null);
  const [uploads, setUploads] = useState([]);
  const [selectedUpload, setSelectedUpload] = useState(null);
  const [results, setResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]); // Hasil yang difilter
  const [processing, setProcessing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [searchTerm, setSearchTerm] = useState(""); // State untuk pencarian

  // Load uploads on component mount
  useEffect(() => {
    fetchUploads();
  }, []);

  // Filter results ketika searchTerm atau results berubah
  useEffect(() => {
    if (searchTerm.trim() === "") {
      setFilteredResults(results);
    } else {
      const filtered = results.filter(item =>
        item.client_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredResults(filtered);
    }
  }, [searchTerm, results]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const extension = selectedFile.name.split(".").pop().toLowerCase();
      if (extension !== "csv") {
        setErrorMessage("Hanya file CSV yang diizinkan");
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setErrorMessage("");
      setSuccessMessage("");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setErrorMessage("Silakan pilih file CSV terlebih dahulu");
      return;
    }

    setUploading(true);
    setErrorMessage("");
    setSuccessMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "http://localhost:5000/api/upload-clients-csv",
        {
          method: "POST",
          body: formData,
        }
      );

      const result = await response.json();
      if (response.ok) {
        setSuccessMessage(
          `File berhasil diupload. ${result.total_rows} data ditemukan.`
        );
        setFile(null);
        // Reset file input
        document.querySelector('input[type="file"]').value = "";
        fetchUploads();
      } else {
        setErrorMessage(result.error || "Error uploading file");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      setErrorMessage("Koneksi error. Pastikan backend berjalan di port 5000.");
    } finally {
      setUploading(false);
    }
  };

  const fetchUploads = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/csv-uploads");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setUploads(data);
    } catch (error) {
      console.error("Error fetching uploads:", error);
      setErrorMessage("Gagal memuat data uploads. Pastikan backend berjalan.");
    }
  };

  const processUpload = async (uploadId) => {
    setProcessing(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const response = await fetch(
        `http://localhost:5000/api/process-csv-upload/${uploadId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const result = await response.json();
      if (response.ok) {
        setSuccessMessage(
          `CSV processing completed. ${result.processed_rows} rows analyzed.`
        );
        fetchUploads();
      } else {
        setErrorMessage(result.error || "Error processing upload");
      }
    } catch (error) {
      console.error("Error processing upload:", error);
      setErrorMessage("Error processing upload. Pastikan backend berjalan.");
    } finally {
      setProcessing(false);
    }
  };

  const deleteUpload = async (uploadId, filename) => {
    if (
      !window.confirm(
        `Apakah Anda yakin ingin menghapus upload "${filename}"? Data yang terkait juga akan dihapus.`
      )
    ) {
      return;
    }

    setDeleting(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      console.log(`Deleting upload ${uploadId}...`);
      const response = await fetch(
        `http://localhost:5000/api/delete-csv-upload/${uploadId}`,
        {
          method: "DELETE",
        }
      );

      // Check if response is OK first
      if (!response.ok) {
        // Try to get error message from response
        let errorText;
        try {
          const errorData = await response.json();
          errorText = errorData.error || `HTTP ${response.status}`;
        } catch {
          errorText = `HTTP ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorText);
      }

      // Try to parse JSON response
      let result;
      try {
        result = await response.json();
      } catch (jsonError) {
        console.warn("Response is not JSON, but delete may have succeeded");
        result = { message: "Delete completed" };
      }

      setSuccessMessage(result.message || "Upload berhasil dihapus");
      // Refresh uploads list
      fetchUploads();
      // Clear results if viewing the deleted upload
      if (selectedUpload && selectedUpload.id === uploadId) {
        setResults([]);
        setFilteredResults([]);
        setSelectedUpload(null);
        setSearchTerm(""); // Reset pencarian
      }
    } catch (error) {
      console.error("Error deleting upload:", error);
      setErrorMessage(
        `Gagal menghapus: ${error.message}. Pastikan endpoint delete tersedia.`
      );
    } finally {
      setDeleting(false);
    }
  };

  const viewResults = async (uploadId) => {
    setErrorMessage("");
    setSuccessMessage("");
    setSearchTerm(""); // Reset pencarian saat melihat hasil baru

    try {
      const response = await fetch(
        `http://localhost:5000/api/csv-results/${uploadId}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results);
      setFilteredResults(data.results); // Set filtered results sama dengan results awal
      setSelectedUpload(data.upload_info);
    } catch (error) {
      console.error("Error fetching results:", error);
      setErrorMessage("Error fetching results");
    }
  };

  const downloadResults = async (uploadId) => {
    try {
      const response = await fetch(
        `http://localhost:5000/api/download-csv-results/${uploadId}`
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `client_analysis_complete_${uploadId}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        const errorData = await response.json();
        setErrorMessage(errorData.error || "Error downloading results");
      }
    } catch (error) {
      console.error("Error downloading results:", error);
      setErrorMessage("Error downloading results");
    }
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      pending: "status-pending",
      processing: "status-processing",
      completed: "status-completed",
      failed: "status-failed",
    };

    return (
      <span className={`status-badge ${statusClasses[status]}`}>{status}</span>
    );
  };

  const clearMessages = () => {
    setErrorMessage("");
    setSuccessMessage("");
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const clearSearch = () => {
    setSearchTerm("");
  };

  return (
    <div className="csv-upload-container">
      <h2>Upload CSV Klien</h2>

      {/* Tampilkan pesan error dan success */}
      {errorMessage && (
        <div className="error-message">
          <span>{errorMessage}</span>
          <button onClick={clearMessages} className="close-message">
            ×
          </button>
        </div>
      )}

      {successMessage && (
        <div className="success-message">
          <span>{successMessage}</span>
          <button onClick={clearMessages} className="close-message">
            ×
          </button>
        </div>
      )}

      <div className="upload-section">
        <h3>Upload File CSV</h3>
        <p>
          CSV harus mengandung kolom:{" "}
          <strong>
            nama, nomor_telepon, kategori_usaha, lokasi, rating , jumlah_ulasan, email, website
          </strong>
        </p>

        <div className="file-input-container">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            disabled={uploading}
          />
          <button onClick={handleUpload} disabled={uploading || !file}>
            {uploading ? "Uploading..." : "Upload CSV"}
          </button>
        </div>
      </div>

      <div className="uploads-section">
        <div className="section-header">
          <h3>History Upload</h3>
          <button onClick={fetchUploads} className="btn-refresh">
            Refresh
          </button>
        </div>

        {uploads.length === 0 ? (
          <p className="no-uploads">Belum ada file yang diupload</p>
        ) : (
          <table className="uploads-table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Upload Date</th>
                <th>Clients</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {uploads.map((upload) => (
                <tr key={upload.id}>
                  <td>{upload.original_name}</td>
                  <td>{new Date(upload.created_at).toLocaleDateString()}</td>
                  <td>{upload.total_rows} client</td>
                  <td>{getStatusBadge(upload.status)}</td>
                  <td>
                    <div className="action-buttons">
                      {upload.status === "pending" && (
                        <button
                          onClick={() => processUpload(upload.id)}
                          disabled={processing}
                          className="btn-process"
                        >
                          {processing ? "Processing..." : "Process"}
                        </button>
                      )}
                      {upload.status === "completed" && (
                        <>
                          <button
                            onClick={() => viewResults(upload.id)}
                            className="btn-view"
                          >
                            View
                          </button>
                          <button
                            onClick={() => downloadResults(upload.id)}
                            className="btn-download"
                          >
                            Download
                          </button>
                        </>
                      )}
                      <button
                        onClick={() =>
                          deleteUpload(upload.id, upload.original_name)
                        }
                        disabled={deleting}
                        className="btn-delete"
                        title="Delete upload"
                      >
                        {deleting ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {results.length > 0 && (
        <div className="results-section">
          <div className="results-header">
            <h3>Hasil Analisis untuk {selectedUpload.original_name}</h3>
            <button
              onClick={() =>
                deleteUpload(selectedUpload.id, selectedUpload.original_name)
              }
              disabled={deleting}
              className="btn-delete"
            >
              {deleting ? "Deleting..." : "Hapus Analisis Ini"}
            </button>
          </div>

          {/* Search Bar */}
          <div className="search-container">
            <div className="search-box">
              <input
                type="text"
                placeholder="Cari nama klien..."
                value={searchTerm}
                onChange={handleSearchChange}
                className="search-input"
              />
              {searchTerm && (
                <button onClick={clearSearch} className="clear-search">
                  ×
                </button>
              )}
              <span className="search-icon">🔍</span>
            </div>
            <div className="search-info">
              Menampilkan {filteredResults.length} dari {results.length} hasil
              {searchTerm && (
                <span className="search-term"> untuk "{searchTerm}"</span>
              )}
            </div>
          </div>

          <div className="results-summary">
            <div className="summary-item">
              <h4>Total Klien</h4>
              <p>{results.length}</p>
            </div>
            <div className="summary-item">
              <h4>Rata-rata Skor</h4>
              <p>
                {Math.round(
                  results.reduce((sum, item) => sum + item.potential_score, 0) /
                    results.length
                )}
              </p>
            </div>
            <div className="summary-item">
              <h4>Prioritas Tinggi</h4>
              <p>
                {results.filter((item) => item.priority === "Tinggi").length}
              </p>
            </div>
            <div className="summary-item">
              <h4>Prioritas Sedang</h4>
              <p>
                {results.filter((item) => item.priority === "Sedang").length}
              </p>
            </div>
            <div className="summary-item">
              <h4>Prioritas Rendah</h4>
              <p>
                {results.filter((item) => item.priority === "Rendah").length}
              </p>
            </div>
          </div>

          <div className="results-table-container">
            <table className="results-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Nama Klien</th>
                  <th>Email</th>
                  <th>Website</th>
                  <th>Kategori Usaha</th>
                  <th>Lokasi</th>
                  <th>Rating</th>
                  <th>Ulasan</th>
                  <th>Skor Potensi</th>
                  <th>Segmentasi</th>
                  <th>Prioritas</th>
                  <th>Rekomendasi</th>
                </tr>
              </thead>
              <tbody>
                {filteredResults.map((result, index) => (
                  <tr key={result.id}>
                    <td className="rank-cell">{index + 1}</td>
                    <td>
                      <div className="client-info">
                        <div className="client-name">{result.client_name}</div>
                        {result.phone_number && (
                          <div className="client-phone">{result.phone_number}</div>
                        )}
                      </div>
                    </td>
                    <td>
                      {result.email ? (
                        <a href={`mailto:${result.email}`} className="email-link">
                          {result.email}
                        </a>
                      ) : (
                        <span className="no-data">-</span>
                      )}
                    </td>
                    <td>
                      {result.website ? (
                        <a 
                          href={result.website.startsWith('http') ? result.website : `https://${result.website}`} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="website-link"
                        >
                          {result.website}
                        </a>
                      ) : (
                        <span className="no-data">-</span>
                      )}
                    </td>
                    <td>{result.business_category}</td>
                    <td>{result.location}</td>
                    <td>
                      <div className="rating-display">
                        <span className="rating-value">{result.rating}</span>
                        <div className="rating-stars">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <span
                              key={star}
                              className={star <= result.rating ? 'star filled' : 'star'}
                            >
                              ★
                            </span>
                          ))}
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="review-count">{result.jumlah_ulasan} ulasan</span>
                    </td>
                    <td>
                      <div className="score-cell">
                        <span className="score-number">{result.potential_score}</span>
                        <div className="score-bar">
                          <div
                            className="score-fill"
                            style={{ width: `${result.potential_score}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td>{result.segmentation}</td>
                    <td>
                      <span
                        className={`priority-badge ${result.priority.toLowerCase()}`}
                      >
                        {result.priority}
                      </span>
                    </td>
                    <td>{result.recommendation_category}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredResults.length === 0 && searchTerm && (
              <div className="no-results">
                <p>Tidak ditemukan klien dengan nama "{searchTerm}"</p>
                <button onClick={clearSearch} className="btn-clear-search">
                  Tampilkan Semua
                </button>
              </div>
            )}
          </div>

          <div className="results-actions">
            <button
              onClick={() => downloadResults(selectedUpload.id)}
              className="download-btn"
            >
              Download Hasil Analisis
            </button>
            <button
              onClick={() => {
                setResults([]);
                setFilteredResults([]);
                setSelectedUpload(null);
                setSearchTerm("");
              }}
              className="btn-clear"
            >
              Tutup Hasil
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CSVClientUpload;