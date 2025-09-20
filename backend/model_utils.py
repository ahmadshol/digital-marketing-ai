import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
from config import get_config

config = get_config()

def train_initial_models():
    """Train initial models dengan data yang lebih realistis dan variatif"""
    np.random.seed(42)
    n_samples = 2000  # More samples for better accuracy
    
    # Realistic data distributions for Indonesian market
    # Frekuensi transaksi (Poisson distribution, mean 12)
    frekuensi = np.random.poisson(12, n_samples)
    frekuensi = np.clip(frekuensi, 1, 50)
    
    # Nilai transaksi (Log-normal distribution for Indonesian business)
    nilai_transaksi = np.random.lognormal(13.5, 1.0, n_samples)  # Mean around 1.5-2 juta
    nilai_transaksi = np.clip(nilai_transaksi, 500000, 10000000)  # 500rb - 10 juta
    
    # Lama usaha (Gamma distribution)
    lama_usaha = np.random.gamma(2.5, 10, n_samples)  # Mean around 2.5 years
    lama_usaha = np.clip(lama_usaha, 3, 120)  # 3 bulan - 10 tahun
    
    # Luas area (Normal distribution)
    luas_area = np.random.normal(75, 30, n_samples)  # Mean 75m², std 30
    luas_area = np.clip(luas_area, 10, 300)  # 10-300 m²
    
    # Location features (Categorical distributions)
    potensi_lokasi = np.random.choice([4, 5, 6, 7, 8, 9], n_samples, 
                                    p=[0.15, 0.20, 0.25, 0.20, 0.15, 0.05])
    
    kepadatan = np.random.choice([5, 6, 7, 8, 9], n_samples, 
                               p=[0.20, 0.25, 0.25, 0.20, 0.10])
    
    daya_beli = np.random.choice([5, 6, 7, 8, 9], n_samples, 
                               p=[0.20, 0.25, 0.25, 0.20, 0.10])
    
    # Combine features
    X = np.column_stack([frekuensi, nilai_transaksi/1000000, lama_usaha, luas_area, 
                        potensi_lokasi, kepadatan, daya_beli])
    
    # Calculate realistic target scores using weighted formula
    weights = np.array([0.25, 0.25, 0.15, 0.10, 0.08, 0.07, 0.10])
    
    # Normalize each feature to 0-1 scale
    X_normalized = np.zeros_like(X)
    for i in range(X.shape[1]):
        X_normalized[:, i] = (X[:, i] - X[:, i].min()) / (X[:, i].max() - X[:, i].min())
    
    # Calculate base score
    y_base = np.dot(X_normalized, weights) * 100
    
    # Add realistic noise and variations
    noise = np.random.normal(0, 8, n_samples)  # Realistic noise
    y = y_base + noise
    
    # Apply business rules simulation
    for i in range(n_samples):
        # Bonus for high transaction value
        if X[i, 1] > 2:  # Above 2 juta
            y[i] += 8
        elif X[i, 1] > 5:  # Above 5 juta
            y[i] += 12
        
        # Bonus for established business
        if X[i, 2] > 36:  # More than 3 years
            y[i] += 5
        elif X[i, 2] > 60:  # More than 5 years
            y[i] += 8
        
        # Bonus for premium location
        if X[i, 4] >= 8:  # High potential location
            y[i] += 6
    
    # Ensure scores are within 0-100 range
    y = np.clip(y, 0, 100)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train improved Random Forest model
    model = RandomForestRegressor(
        n_estimators=200, 
        random_state=42,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features=0.8,
        bootstrap=True
    )
    
    model.fit(X_scaled, y)
    
    # Train KMeans for segmentation
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=20, max_iter=300)
    kmeans.fit(X_scaled)
    
    # Save models
    joblib.dump(model, config.MODEL_PATH)
    joblib.dump(scaler, config.SCALER_PATH)
    joblib.dump(kmeans, config.KMEANS_PATH)
    
    # Calculate and print model performance
    train_score = model.score(X_scaled, y)
    print(f"Initial models trained with {n_samples} samples")
    print(f"Model R2 score: {train_score:.3f}")
    print(f"Score distribution: Min={y.min():.1f}, Max={y.max():.1f}, Mean={y.mean():.1f}")
    
    return model, scaler, kmeans

def get_segment_name(cluster_id):
    """Map cluster ID to segment name"""
    segments = [
        "Pemula - Potensi Berkembang",
        "Menengah - Stabil",
        "Expert - Berpengalaman",
        "High-Value - Potensi Besar"
    ]
    return segments[cluster_id % len(segments)]

def get_recommendation_category(score, segment):
    """Get recommendation based on score and segment"""
    if score >= 80:
        return "Prioritas Utama - Pendekatan Personal"
    elif score >= 60:
        return "Prioritas Menengah - Campaign Khusus"
    else:
        return "Prioritas Standar - Nurturing"