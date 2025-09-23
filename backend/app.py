from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from werkzeug.utils import secure_filename
import joblib
import os
import uuid
import csv
import io
import re
from dotenv import load_dotenv
from config import get_config

# Load environment variables
load_dotenv()

# Get configuration
config = get_config()

app = Flask(__name__)
CORS(app)

# Database configuration using config
db_config = {
    'host': config.DB_HOST,
    'port': config.DB_PORT,
    'user': config.DB_USER,
    'password': config.DB_PASSWORD,
    'database': config.DB_NAME
}

# Model paths from config
MODEL_PATH = config.MODEL_PATH
SCALER_PATH = config.SCALER_PATH
KMEANS_PATH = config.KMEANS_PATH

# Konfigurasi upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'csv_uploads')
ALLOWED_EXTENSIONS = {'csv'}

# Pastikan folder upload ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def get_db_connection():
    return mysql.connector.connect(**db_config)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_features_from_data(client_data):
    """Extract features from client data berdasarkan rating"""
    features = {}
    
    nama = client_data['nama'] or ''
    nomor = client_data['nomor_telepon'] or ''
    kategori = client_data['kategori_usaha'].lower()
    lokasi = client_data['lokasi'].lower()
    rating = float(client_data.get('rating', 0))
    jumlah_ulasan = int(client_data.get('jumlah_ulasan', 0))
    
    # 1. RATING (Weight: 35%)
    features['rating'] = max(0, min(5, rating))  # Ensure 0-5 range
    
    # 2. JUMLAH ULASAN (Weight: 25%)
    # Normalize: 0-1000 ulasan → 0-100 scale
    features['jumlah_ulasan'] = min(jumlah_ulasan, 1000)  # Cap at 1000
    
    # 3. LOKASI-BASED FEATURES (Weight: 40% total)
    # Predefined scoring dictionaries
    location_scores = {
        'jakarta': {'potensi': 9, 'kepadatan': 9, 'daya_beli': 8},
        'surabaya': {'potensi': 8, 'kepadatan': 8, 'daya_beli': 7},
        'bandung': {'potensi': 8, 'kepadatan': 8, 'daya_beli': 7},
        'yogyakarta': {'potensi': 7, 'kepadatan': 7, 'daya_beli': 6},
        'semarang': {'potensi': 7, 'kepadatan': 7, 'daya_beli': 6},
        'medan': {'potensi': 7, 'kepadatan': 8, 'daya_beli': 6},
        'denpasar': {'potensi': 7, 'kepadatan': 7, 'daya_beli': 7},
        'makassar': {'potensi': 6, 'kepadatan': 7, 'daya_beli': 6},
        'malang': {'potensi': 6, 'kepadatan': 6, 'daya_beli': 5},
        'bogor': {'potensi': 6, 'kepadatan': 7, 'daya_beli': 6},
        'tangerang': {'potensi': 6, 'kepadatan': 7, 'daya_beli': 6},
        'bekasi': {'potensi': 6, 'kepadatan': 7, 'daya_beli': 6},
        'depok': {'potensi': 5, 'kepadatan': 6, 'daya_beli': 5}
    }
    
    keyword_scores = {
        'mall': {'potensi': 9, 'kepadatan': 9, 'daya_beli': 9},
        'pusat': {'potensi': 8, 'kepadatan': 8, 'daya_beli': 8},
        'strategis': {'potensi': 8, 'kepadatan': 7, 'daya_beli': 8},
        'utama': {'potensi': 8, 'kepadatan': 8, 'daya_beli': 8},
        'perkantoran': {'potensi': 7, 'kepadatan': 6, 'daya_beli': 8},
        'perumahan': {'potensi': 6, 'kepadatan': 7, 'daya_beli': 6},
        'komersial': {'potensi': 8, 'kepadatan': 8, 'daya_beli': 7},
        'desa': {'potensi': 4, 'kepadatan': 4, 'daya_beli': 3},
        'kecil': {'potensi': 4, 'kepadatan': 4, 'daya_beli': 3},
        'pinggiran': {'potensi': 4, 'kepadatan': 4, 'daya_beli': 3}
    }
    
    # Initialize scores
    potensi = 5
    kepadatan = 5
    daya_beli = 5
    
    # Check for city matches
    for city, scores in location_scores.items():
        if city in lokasi:
            potensi = max(potensi, scores['potensi'])
            kepadatan = max(kepadatan, scores['kepadatan'])
            daya_beli = max(daya_beli, scores['daya_beli'])
    
    # Check for keyword matches
    for keyword, scores in keyword_scores.items():
        if keyword in lokasi:
            potensi = max(potensi, scores['potensi'])
            kepadatan = max(kepadatan, scores['kepadatan'])
            daya_beli = max(daya_beli, scores['daya_beli'])
    
    # Special cases for high-end areas
    if any(x in lokasi for x in ['selatan', 'pusat', 'menteng', 'pondok indah', 'kebayoran']):
        daya_beli = max(daya_beli, 9)
    
    features['potensi_bisnis_lokasi'] = potensi
    features['kepadatan_penduduk'] = kepadatan
    features['daya_beli_lokasi'] = daya_beli
    
    # KATEGORI USAHA BONUS (Additional 0-10 points)
    kategori_bonus = {
        'teknologi': 8, 'technology': 8, 'it': 7, 'software': 8,
        'kesehatan': 7, 'health': 7, 'medis': 7, 'klinik': 6,
        'fashion': 6, 'clothing': 6, 'apparel': 6,
        'makanan': 5, 'food': 5, 'restoran': 5, 'kuliner': 5,
        'retail': 4, 'toko': 4, 'store': 4,
        'jasa': 3, 'service': 3,
        'otomotif': 4, 'automotive': 4,
        'pendidikan': 6, 'education': 6, 'sekolah': 5,
    }
    
    features['kategori_bonus'] = kategori_bonus.get(kategori, 0)
    
    return features

def analyze_potential(features):
    """Analyze client potential menggunakan weighted scoring system berdasarkan rating"""
    # Weighting system
    weights = {
        'rating': 0.35,                   # 35% - Rating 0-5
        'jumlah_ulasan': 0.25,            # 25% - Jumlah ulasan
        'potensi_bisnis_lokasi': 0.15,    # 15% - Potensi lokasi
        'kepadatan_penduduk': 0.10,       # 10% - Kepadatan
        'daya_beli_lokasi': 0.15          # 15% - Daya beli
    }
    
    # Normalize each feature to 0-100 scale
    normalized_features = {}
    
    # Rating (0-5 → 0-100)
    normalized_features['rating'] = (features['rating'] / 5) * 100
    
    # Jumlah ulasan (0-1000 → 0-100)
    normalized_features['jumlah_ulasan'] = (features['jumlah_ulasan'] / 1000) * 100
    
    # Location features (already 0-10 scale → 0-100)
    normalized_features['potensi_bisnis_lokasi'] = features['potensi_bisnis_lokasi'] * 10
    normalized_features['kepadatan_penduduk'] = features['kepadatan_penduduk'] * 10
    normalized_features['daya_beli_lokasi'] = features['daya_beli_lokasi'] * 10
    
    # Calculate weighted score
    base_score = 0
    for feature_name, weight in weights.items():
        base_score += normalized_features[feature_name] * weight
    
    # Add kategori bonus (0-10 points)
    base_score += features.get('kategori_bonus', 0)
    
    # Apply business rules adjustments
    final_score = apply_business_rules(base_score, features)
    
    # Ensure score is within 0-100 range
    final_score = max(0, min(100, final_score))
    
    # Determine segmentation based on rating and business factors
    segmentasi = determine_segmentation(final_score, features)
    
    # Determine priority
    if final_score >= 80:
        prioritas = "Tinggi"
    elif final_score >= 60:
        prioritas = "Sedang"
    else:
        prioritas = "Rendah"
    
    # Recommendation category
    kategori_rekomendasi = get_recommendation_category(final_score, segmentasi, features)
    
    return {
        'skor_potensi': int(round(final_score)),
        'segmentasi': segmentasi,
        'prioritas': prioritas,
        'kategori_rekomendasi': kategori_rekomendasi
    }

def apply_business_rules(score, features):
    """Apply business rules adjustments berdasarkan rating"""
    adjusted_score = score
    
    # Bonus for high rating
    if features['rating'] >= 4.5:  # Rating sangat tinggi
        adjusted_score += 12
    elif features['rating'] >= 4.0:  # Rating tinggi
        adjusted_score += 8
    elif features['rating'] >= 3.5:  # Rating baik
        adjusted_score += 4
    
    # Bonus for many reviews (social proof)
    if features['jumlah_ulasan'] > 500:  # Ulasan sangat banyak
        adjusted_score += 10
    elif features['jumlah_ulasan'] > 200:  # Ulasan banyak
        adjusted_score += 6
    elif features['jumlah_ulasan'] > 50:  # Ulasan cukup
        adjusted_score += 3
    
    # Bonus for premium location
    if features['potensi_bisnis_lokasi'] >= 80:  # High potential location
        adjusted_score += 6
    
    # Bonus for high density area
    if features['kepadatan_penduduk'] >= 80:  # High density
        adjusted_score += 4
    
    # Bonus for high purchasing power
    if features['daya_beli_lokasi'] >= 80:  # High purchasing power
        adjusted_score += 5
    
    # Penalty for low rating
    if features['rating'] < 2.0:  # Rating sangat rendah
        adjusted_score -= 15
    elif features['rating'] < 3.0:  # Rating rendah
        adjusted_score -= 8
    
    # Penalty for very few reviews
    if features['jumlah_ulasan'] < 10:  # Very few reviews
        adjusted_score -= 5
    
    return min(100, adjusted_score)  # Cap at 100

def determine_segmentation(score, features):
    """Determine segmentation based on rating and business factors"""
    # Base segmentation on score dengan pertimbangan rating
    if score >= 85:
        return "Premium - Rating Tinggi"
    elif score >= 70:
        if features['rating'] >= 4.0:
            return "Expert - Berpengalaman & Terpercaya"
        else:
            return "Menengah - Berkembang"
    elif score >= 50:
        return "Standard - Potensi Berkembang"
    else:
        return "Pemula - Perlu Pembinaan"

def get_recommendation_category(score, segment, features):
    """Get personalized recommendation based on rating factors"""
    recommendations = {
        'Premium - Rating Tinggi': [
            "Prioritas Utama - Program Exclusive",
            "Partnership Premium - Kolaborasi Strategis",
            "VIP Treatment - Layanan Prioritas"
        ],
        'Expert - Berpengalaman & Terpercaya': [
            "Prioritas Menengah - Program Growth",
            "Business Expansion - Pengembangan Jangkauan", 
            "Loyalty Program - Program Loyalitas"
        ],
        'Menengah - Berkembang': [
            "Prioritas Standard - Program Pengembangan",
            "Quality Improvement - Peningkatan Kualitas",
            "Marketing Support - Dukungan Pemasaran"
        ],
        'Standard - Potensi Berkembang': [
            "Basic Support - Dukungan Dasar",
            "Training Program - Program Pelatihan",
            "Mentorship - Program Pendampingan"
        ],
        'Pemula - Perlu Pembinaan': [
            "Starter Package - Paket Pemula",
            "Foundation Building - Pembangunan Dasar",
            "Basic Guidance - Panduan Dasar"
        ]
    }
    
    # Select recommendation based on segment
    segment_recommendations = recommendations.get(segment, [
        "Custom Program - Program Khusus"
    ])
    
    # Further customize based on rating characteristics
    if features['rating'] >= 4.5:
        return segment_recommendations[0] + " (Rating Excellent)"
    elif features['rating'] >= 4.0:
        return segment_recommendations[0] + " (Rating Very Good)"
    else:
        return segment_recommendations[0]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint untuk mengecek status server"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'models_loaded': os.path.exists(MODEL_PATH) and 
                            os.path.exists(SCALER_PATH) and 
                            os.path.exists(KMEANS_PATH)
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

@app.route('/api/retrain', methods=['POST'])
def retrain_models():
    """Endpoint untuk melatih ulang model dengan data terbaru"""
    try:
        # Ambil data dari database untuk training
        conn = get_db_connection()
        query = """
            SELECT f.frekuensi_transaksi, f.nilai_transaksi_rata_rata, 
                   f.lama_usaha_bulan, f.luas_area_usaha, 
                   f.potensi_bisnis_lokasi, f.kepadatan_penduduk, 
                   f.daya_beli_lokasi, a.skor_potensi
            FROM features f
            JOIN analysis_results a ON f.client_id = a.client_id
            WHERE a.skor_potensi IS NOT NULL
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        if len(df) < config.MIN_SAMPLE_SIZE:
            return jsonify({
                'error': f'Not enough data for training. Minimum {config.MIN_SAMPLE_SIZE} samples required.',
                'available_samples': len(df)
            }), 400
        
        # Prepare data for training
        X = df.drop('skor_potensi', axis=1).values
        y = df['skor_potensi'].values / 100.0  # Convert to 0-1 scale
        
        # Train new models
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        
        kmeans = KMeans(n_clusters=4, random_state=42)
        kmeans.fit(X_scaled)
        
        # Save models
        joblib.dump(model, MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)
        joblib.dump(kmeans, KMEANS_PATH)
        
        return jsonify({
            'message': 'Models retrained successfully',
            'samples_used': len(df),
            'model_score': model.score(X_scaled, y)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all clients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients ORDER BY created_at DESC")
        clients = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(clients)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clients', methods=['POST'])
def add_client():
    """Add a new client dengan rating"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        client_data = {
            'nama': data.get('nama', ''),
            'nomor_telepon': data.get('nomor_telepon', ''),
            'kategori_usaha': data.get('kategori_usaha', ''),
            'lokasi': data.get('lokasi', ''),
            'rating': float(data.get('rating', 0)),
            'jumlah_ulasan': int(data.get('jumlah_ulasan', 0))
        }
        
        # Validate rating
        if client_data['rating'] < 0 or client_data['rating'] > 5:
            return jsonify({'error': 'Rating must be between 0-5'}), 400
        
        # Validate jumlah_ulasan
        if client_data['jumlah_ulasan'] < 0:
            return jsonify({'error': 'Jumlah ulasan cannot be negative'}), 400
        
        # Extract features and analyze
        features = extract_features_from_data(client_data)
        analysis_result = analyze_potential(features)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert client
        cursor.execute(
            "INSERT INTO clients (nama, nomor_telepon, kategori_usaha, lokasi, rating, jumlah_ulasan) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                client_data['nama'],
                client_data['nomor_telepon'],
                client_data['kategori_usaha'],
                client_data['lokasi'],
                client_data['rating'],
                client_data['jumlah_ulasan']
            )
        )
        client_id = cursor.lastrowid
        
        # Insert features
        cursor.execute("""
            INSERT INTO features 
            (client_id, rating, jumlah_ulasan, potensi_bisnis_lokasi, kepadatan_penduduk, daya_beli_lokasi)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            client_id, 
            features['rating'], 
            features['jumlah_ulasan'],
            features['potensi_bisnis_lokasi'], 
            features['kepadatan_penduduk'], 
            features['daya_beli_lokasi']
        ))
        
        # Insert analysis result
        cursor.execute("""
            INSERT INTO analysis_results 
            (client_id, skor_potensi, segmentasi, prioritas, kategori_rekomendasi)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            client_id, analysis_result['skor_potensi'], analysis_result['segmentasi'],
            analysis_result['prioritas'], analysis_result['kategori_rekomendasi']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Client added successfully',
            'client_id': client_id,
            'analysis': analysis_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# CSV Upload 

@app.route('/api/upload-clients-csv', methods=['POST'])
def upload_clients_csv():
    """Upload CSV file with clients data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Count rows in CSV
            row_count = 0
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    # Skip header and count rows
                    next(reader, None)  # Skip header
                    row_count = sum(1 for row in reader)
            except Exception as e:
                os.remove(filepath)
                return jsonify({'error': f'Invalid CSV file: {str(e)}'}), 400
            
            # Save to database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO csv_uploads (filename, original_name, total_rows) VALUES (%s, %s, %s)",
                (unique_filename, original_filename, row_count)
            )
            upload_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'message': 'File uploaded successfully',
                'upload_id': upload_id,
                'original_name': original_filename,
                'total_rows': row_count
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-csv-upload/<int:upload_id>', methods=['POST'])
def process_csv_upload(upload_id):
    """Process uploaded CSV file"""
    try:
        # Get upload record
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM csv_uploads WHERE id = %s", (upload_id,))
        upload_record = cursor.fetchone()
        
        if not upload_record:
            return jsonify({'error': 'Upload record not found'}), 404
        
        # Update status to processing
        cursor.execute("UPDATE csv_uploads SET status = 'processing' WHERE id = %s", (upload_id,))
        conn.commit()
        
        # Load the CSV file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_record['filename'])
        
        processed_rows = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                
                # Validate required columns
                required_columns = ['nama', 'kategori_usaha', 'lokasi', 'rating', 'jumlah_ulasan']
                if not all(col in csv_reader.fieldnames for col in required_columns):
                    raise Exception(f"CSV must contain columns: {', '.join(required_columns)}")
                
                for row in csv_reader:
                    try:
                        # Extract client data from CSV row
                        client_data = {
                            'nama': row.get('nama', '').strip(),
                            'nomor_telepon': row.get('nomor_telepon', '').strip(),
                            'email': row.get('email', '').strip(),  # Tambahkan email
                            'website': row.get('website', '').strip(),  # Tambahkan website
                            'kategori_usaha': row.get('kategori_usaha', '').strip(),
                            'lokasi': row.get('lokasi', '').strip(),
                            'rating': float(row.get('rating', 0)),
                            'jumlah_ulasan': int(row.get('jumlah_ulasan', 0))
                        }
                        
                        # Skip row jika data penting kosong
                        if not client_data['nama'] or not client_data['kategori_usaha']:
                            continue
                        
                        # Validate rating
                        if client_data['rating'] < 0 or client_data['rating'] > 5:
                            continue
                        
                        # Validate jumlah_ulasan
                        if client_data['jumlah_ulasan'] < 0:
                            continue
                        
                        # Extract features and analyze
                        features = extract_features_from_data(client_data)
                        analysis_result = analyze_potential(features)
                        
                         # Save to analysis results dengan email dan website
                        cursor.execute("""
                            INSERT INTO csv_analysis_results 
                            (upload_id, client_name, phone_number, email, website, business_category, location, 
                            rating, jumlah_ulasan, potential_score, segmentation, priority, recommendation_category)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            upload_id, client_data['nama'], client_data['nomor_telepon'],
                            client_data['email'], client_data['website'],  # Tambahkan email dan website
                            client_data['kategori_usaha'], client_data['lokasi'],
                            client_data['rating'], client_data['jumlah_ulasan'],
                            analysis_result['skor_potensi'], analysis_result['segmentasi'],
                            analysis_result['prioritas'], analysis_result['kategori_rekomendasi']
                        ))
                        
                        processed_rows += 1
                        
                    except Exception as e:
                        print(f"Error processing row {processed_rows + 1}: {str(e)}")
                        continue
                
                # Update upload status
                cursor.execute(
                    "UPDATE csv_uploads SET status = 'completed', processed_rows = %s WHERE id = %s",
                    (processed_rows, upload_id)
                )
                conn.commit()
                
        except Exception as e:
            cursor.execute("UPDATE csv_uploads SET status = 'failed' WHERE id = %s", (upload_id,))
            conn.commit()
            return jsonify ({'error': f'Failed to process CSV: {str(e)}'}), 500
        finally:
            cursor.close()
            conn.close()
        
        return jsonify({
            'message': 'CSV processing completed',
            'processed_rows': processed_rows,
            'upload_id': upload_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/csv-uploads', methods=['GET'])
def get_csv_uploads():
    """Get all CSV uploads"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM csv_uploads ORDER BY created_at DESC")
        uploads = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(uploads)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/csv-results/<int:upload_id>', methods=['GET'])
def get_csv_results(upload_id):
    """Get results for a specific CSV upload"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get upload info
        cursor.execute("SELECT * FROM csv_uploads WHERE id = %s", (upload_id,))
        upload_info = cursor.fetchone()
        
        if not upload_info:
            return jsonify({'error': 'Upload not found'}), 404
        
        # Get results with sorting by score
        cursor.execute("""
            SELECT * FROM csv_analysis_results 
            WHERE upload_id = %s 
            ORDER BY potential_score DESC
        """, (upload_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'upload_info': upload_info,
            'results': results,
            'total_results': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-csv-results/<int:upload_id>', methods=['GET'])
def download_csv_results(upload_id):
    """Download CSV results - hanya kolom penting untuk download"""
    try:
        # Get results
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM csv_analysis_results 
            WHERE upload_id = %s 
            ORDER BY potential_score DESC
        """, (upload_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Create CSV in memory - GABUNGAN LENGKAP
        output = io.StringIO()
        fieldnames = [
            'rank', 
            'client_name', 
            'phone_number', 
            'email', 
            'website',
            'business_category', 
            'location', 
            'rating', 
            'review_count',
            'potential_score', 
            'segmentation', 
            'priority', 
            'recommendation_category'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, result in enumerate(results):
            writer.writerow({
                'rank': i + 1,
                'client_name': result['client_name'],
                'phone_number': result['phone_number'] or '-',
                'email': result['email'] or '-',
                'website': result['website'] or '-',
                'business_category': result['business_category'],
                'location': result['location'],
                'rating': result['rating'],
                'review_count': result['jumlah_ulasan'],
                'potential_score': result['potential_score'],
                'segmentation': result['segmentation'],
                'priority': result['priority'],
                'recommendation_category': result['recommendation_category']
            })
        
        output.seek(0)
        
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=client_analysis_{upload_id}.csv"}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/uploads', methods=['GET'])
def debug_uploads():
    """Debug endpoint to check upload folder"""
    try:
        files = []
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })
        
        return jsonify({
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'exists': os.path.exists(app.config['UPLOAD_FOLDER']),
            'files': files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete Action

@app.route('/api/delete-csv-upload/<int:upload_id>', methods=['DELETE'])
def delete_csv_upload(upload_id):
    """Delete CSV upload and associated data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get upload record to find filename
        cursor.execute("SELECT * FROM csv_uploads WHERE id = %s", (upload_id,))
        upload_record = cursor.fetchone()
        
        if not upload_record:
            return jsonify({'error': 'Upload record not found'}), 404
        
        # Delete associated analysis results first
        cursor.execute("DELETE FROM csv_analysis_results WHERE upload_id = %s", (upload_id,))
        
        # Delete the upload record
        cursor.execute("DELETE FROM csv_uploads WHERE id = %s", (upload_id,))
        
        # Delete the actual CSV file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_record['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'CSV upload and associated data deleted successfully',
            'deleted_upload_id': upload_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete CSV upload: {str(e)}'}), 500
    
    

if __name__ == '__main__':
    # Initialize models if they don't exist
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH) or not os.path.exists(KMEANS_PATH):
        print("Initializing models...")
        from model_utils import train_initial_models
        train_initial_models()
    
    app.run(
        debug=config.FLASK_DEBUG, 
        host=config.HOST, 
        port=config.PORT
    )
    
