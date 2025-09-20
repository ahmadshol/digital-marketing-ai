import React, { useState } from "react";
import ClientForm from "./components/ClientForm";
import ClientList from "./components/ClientList";
import CSVClientUpload from "./components/CSVClientUpload";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("tambah");
  const [refreshList, setRefreshList] = useState(false);

  const handleClientAdded = () => {
    setRefreshList(!refreshList);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Sistem Analisis Potensi Klien</h1>
        <nav>
          <button
            className={activeTab === "tambah" ? "active" : ""}
            onClick={() => setActiveTab("tambah")}
          >
            Tambah Klien
          </button>
          <button
            className={activeTab === "daftar" ? "active" : ""}
            onClick={() => setActiveTab("daftar")}
          >
            Daftar Klien
          </button>
          <button
            className={activeTab === "csv-upload" ? "active" : ""}
            onClick={() => setActiveTab("csv-upload")}
          >
            Upload CSV
          </button>
        </nav>
      </header>

      <main>
        {activeTab === "tambah" && (
          <ClientForm onClientAdded={handleClientAdded} />
        )}

        {activeTab === "daftar" && <ClientList key={refreshList} />}

        {activeTab === "csv-upload" && <CSVClientUpload />}
      </main>
    </div>
  );
}

export default App;
