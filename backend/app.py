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
    """Extract features from client data dengan algoritma yang lebih akurat"""
    features = {}
    
    nama = client_data['nama'] or ''
    nomor = client_data['nomor_telepon'] or ''
    kategori = client_data['kategori_usaha'].lower()
    lokasi = client_data['lokasi'].lower()
    riwayat = client_data['riwayat_transaksi'] or ''
    
    # 1. FREKUENSI TRANSAKSI (Weight: 25%)
    transaction_count = 0
    # Pattern matching untuk berbagai format
    patterns = [
        r'(\d+)\s*(transaksi|trx|tx|order|pembelian|purchase)',
        r'(rata-rata|rata|sekitar|about|approx)\s*(\d+)\s*(transaksi|trx)',
        r'(\d+)\s*(kali)\s*(dalam|per|every)\s*(bulan|month|minggu|week|hari|day)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, riwayat.lower())
        for match in matches:
            if match[0].isdigit():
                transaction_count += int(match[0])
            elif len(match) > 1 and match[1].isdigit():
                transaction_count += int(match[1])
    
    # Fallback: count keywords
    if transaction_count == 0:
        transaction_count = (riwayat.lower().count('transaksi') + 
                           riwayat.lower().count('beli') + 
                           riwayat.lower().count('pembelian') + 
                           riwayat.lower().count('order'))
    
    features['frekuensi_transaksi'] = min(transaction_count, 50)  # Cap at 50
    
    # 2. NILAI TRANSAKSI (Weight: 25%)
    nilai_rata_rata = 0
    # Pattern matching untuk nilai uang
    money_patterns = [
        r'rp\s*[\.]?\s*(\d+[\.,]?\d*)[\s]*(ribu|rb|juta|jt|m)',
        r'(\d+[\.,]?\d*)\s*(ribu|rb|juta|jt|m)\s*(rupiah|rp)',
        r'nilai\s*(rata-rata|rata)\s*(\d+[\.,]?\d*)\s*(ribu|rb|juta|jt|m)',
        r'(\d+[\.,]?\d*)\s*(juta|jt|m)\s*per\s*(transaksi|order)'
    ]
    
    detected_values = []
    for pattern in money_patterns:
        matches = re.findall(pattern, riwayat.lower())
        for match in matches:
            try:
                nilai = float(match[0].replace(',', '.'))
                multiplier = 1
                if any(x in match[1] for x in ['juta', 'jt', 'm']):
                    multiplier = 1000000
                elif any(x in match[1] for x in ['ribu', 'rb']):
                    multiplier = 1000
                detected_values.append(nilai * multiplier)
            except:
                continue
    
    if detected_values:
        nilai_rata_rata = sum(detected_values) / len(detected_values)
    else:
        # Heuristic fallback
        if 'juta' in riwayat.lower() or 'jt' in riwayat.lower():
            nilai_rata_rata = 2500000
        elif 'ribu' in riwayat.lower() or 'rb' in riwayat.lower():
            nilai_rata_rata = 750000
        else:
            nilai_rata_rata = 500000
    
    features['nilai_transaksi_rata_rata'] = nilai_rata_rata
    
    # 3. LAMA USAHA (Weight: 15%)
    lama_usaha = 12  # Default 1 year
    
    time_patterns = [
        r'(\d+)\s*(tahun|thn|th)',
        r'(\d+)\s*(bulan|bln)',
        r'sudah\s*(\d+)\s*(tahun|thn|th)',
        r'berjalan\s*(\d+)\s*(tahun|thn|th|bulan|bln)'
    ]
    
    for pattern in time_patterns:
        matches = re.findall(pattern, riwayat.lower())
        for match in matches:
            try:
                value = int(match[0])
                if any(x in match[1] for x in ['tahun', 'thn', 'th']):
                    lama_usaha = value * 12
                elif any(x in match[1] for x in ['bulan', 'bln']):
                    lama_usaha = value
                break
            except:
                continue
    
    features['lama_usaha_bulan'] = min(lama_usaha, 120)  # Cap at 10 years
    
    # 4. LUAS AREA (Weight: 10%)
    luas_area = 50.0  # Default 50m²
    
    area_patterns = [
        r'(\d+)\s*(m2|m²|meter|meter persegi)',
        r'luas\s*(\d+)\s*(m2|m²|meter)',
        r'(\d+)\s*(m2|m²)\s*(luas|area)'
    ]
    
    for pattern in area_patterns:
        matches = re.findall(pattern, riwayat.lower())
        for match in matches:
            try:
                luas_area = float(match[0])
                break
            except:
                continue
    
    features['luas_area_usaha'] = min(luas_area, 500)  # Cap at 500m²
    
    # 5-7. LOKASI-BASED FEATURES (Weight: 25% total)
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
        'pendidikan': 6, 'education': 6, 'sekolah': 5
    }
    
    features['kategori_bonus'] = kategori_bonus.get(kategori, 0)
    
    return features

def analyze_potential(features):
    """Analyze client potential menggunakan weighted scoring system"""
    # Weighting system
    weights = {
        'frekuensi_transaksi': 0.25,      # 25%
        'nilai_transaksi_rata_rata': 0.25, # 25%
        'lama_usaha_bulan': 0.15,         # 15%
        'luas_area_usaha': 0.10,          # 10%
        'potensi_bisnis_lokasi': 0.08,    # 8%
        'kepadatan_penduduk': 0.07,       # 7%
        'daya_beli_lokasi': 0.10          # 10%
    }
    
    # Normalize each feature to 0-100 scale
    normalized_features = {}
    
    # Frekuensi transaksi (0-50 → 0-100)
    normalized_features['frekuensi_transaksi'] = (features['frekuensi_transaksi'] / 50) * 100
    
    # Nilai transaksi (0-10M → 0-100)
    normalized_features['nilai_transaksi_rata_rata'] = min((features['nilai_transaksi_rata_rata'] / 10000000) * 100, 100)
    
    # Lama usaha (0-120 bulan → 0-100)
    normalized_features['lama_usaha_bulan'] = (features['lama_usaha_bulan'] / 120) * 100
    
    # Luas area (0-500 m² → 0-100)
    normalized_features['luas_area_usaha'] = (features['luas_area_usaha'] / 500) * 100
    
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
    
    # Determine segmentation based on business maturity
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
    """Apply business rules adjustments"""
    adjusted_score = score
    
    # Bonus for premium clients
    if features['nilai_transaksi_rata_rata'] > 5000000:  # Above 5 juta
        adjusted_score += 8
    elif features['nilai_transaksi_rata_rata'] > 2000000:  # Above 2 juta
        adjusted_score += 5
    
    # Bonus for established business
    if features['lama_usaha_bulan'] > 60:  # More than 5 years
        adjusted_score += 7
    elif features['lama_usaha_bulan'] > 36:  # More than 3 years
        adjusted_score += 4
    
    # Bonus for premium location
    if features['potensi_bisnis_lokasi'] >= 80:  # High potential location
        adjusted_score += 6
    
    # Bonus for high density area
    if features['kepadatan_penduduk'] >= 80:  # High density
        adjusted_score += 4
    
    # Bonus for high purchasing power
    if features['daya_beli_lokasi'] >= 80:  # High purchasing power
        adjusted_score += 5
    
    # Penalty for very new business
    if features['lama_usaha_bulan'] < 6:  # Less than 6 months
        adjusted_score -= 5
    
    return min(100, adjusted_score)  # Cap at 100

def determine_segmentation(score, features):
    """Determine segmentation based on multiple factors"""
    # Base segmentation on score
    if score >= 85:
        return "High-Value - Potensi Besar"
    elif score >= 70:
        return "Expert - Berpengalaman"
    elif score >= 50:
        return "Menengah - Stabil"
    else:
        return "Pemula - Potensi Berkembang"

def get_recommendation_category(score, segment, features):
    """Get personalized recommendation based on multiple factors"""
    recommendations = {
        'High-Value - Potensi Besar': [
            "Prioritas Utama - Pendekatan Personal Executive",
            "Program Khusus VIP - Dedicated Account Manager",
            "Premium Service Package - Custom Solution"
        ],
        'Expert - Berpengalaman': [
            "Prioritas Menengah - Campaign Khusus Growth",
            "Business Development Program - Strategic Partnership",
            "Value-Added Services Package"
        ],
        'Menengah - Stabil': [
            "Prioritas Standard - Targeted Marketing Campaign",
            "Business Optimization Program - Efficiency Focus",
            "Standard Service Package with Upsell Opportunities"
        ],
        'Pemula - Potensi Berkembang': [
            "Prioritas Nurturing - Education & Development",
            "Starter Program - Basic Support Package",
            "Growth Foundation Program - Capacity Building"
        ]
    }
    
    # Select recommendation based on segment
    segment_recommendations = recommendations.get(segment, [
        "Program Development - Custom Approach"
    ])
    
    # Further customize based on business characteristics
    if features['nilai_transaksi_rata_rata'] > 3000000:
        return segment_recommendations[0] + " dengan Focus High-Value"
    elif features['lama_usaha_bulan'] > 24:
        return segment_recommendations[0] + " dengan Established Business Focus"
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
    """Add a new client"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        client_data = {
            'nama': data.get('nama', ''),
            'nomor_telepon': data.get('nomor_telepon', ''),
            'kategori_usaha': data.get('kategori_usaha', ''),
            'lokasi': data.get('lokasi', ''),
            'riwayat_transaksi': data.get('riwayat_transaksi', '')
        }
        
        # Extract features and analyze
        features = extract_features_from_data(client_data)
        analysis_result = analyze_potential(features)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert client
        cursor.execute(
            "INSERT INTO clients (nama, nomor_telepon, kategori_usaha, lokasi, riwayat_transaksi) VALUES (%s, %s, %s, %s, %s)",
            (
                client_data['nama'],
                client_data['nomor_telepon'],
                client_data['kategori_usaha'],
                client_data['lokasi'],
                client_data['riwayat_transaksi']
            )
        )
        client_id = cursor.lastrowid
        
        # Insert features
        cursor.execute("""
            INSERT INTO features 
            (client_id, frekuensi_transaksi, nilai_transaksi_rata_rata, lama_usaha_bulan, 
             luas_area_usaha, potensi_bisnis_lokasi, kepadatan_penduduk, daya_beli_lokasi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            client_id, features['frekuensi_transaksi'], features['nilai_transaksi_rata_rata'],
            features['lama_usaha_bulan'], features['luas_area_usaha'], 
            features['potensi_bisnis_lokasi'], features['kepadatan_penduduk'], 
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
                required_columns = ['nama', 'kategori_usaha', 'lokasi', 'riwayat_transaksi']
                if not all(col in csv_reader.fieldnames for col in required_columns):
                    raise Exception(f"CSV must contain columns: {', '.join(required_columns)}")
                
                for row in csv_reader:
                    try:
                        # Extract client data from CSV row
                        client_data = {
                            'nama': row.get('nama', '').strip(),
                            'nomor_telepon': row.get('nomor_telepon', '').strip(),
                            'kategori_usaha': row.get('kategori_usaha', '').strip(),
                            'lokasi': row.get('lokasi', '').strip(),
                            'riwayat_transaksi': row.get('riwayat_transaksi', '').strip()
                        }
                        
                        # Skip row if essential data is missing
                        if not client_data['nama'] or not client_data['kategori_usaha']:
                            continue
                        
                        # Extract features and analyze
                        features = extract_features_from_data(client_data)
                        analysis_result = analyze_potential(features)
                        
                        # Save to analysis results
                        cursor.execute("""
                            INSERT INTO csv_analysis_results 
                            (upload_id, client_name, phone_number, business_category, location, 
                             transaction_history, potential_score, segmentation, priority, recommendation_category)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            upload_id, client_data['nama'], client_data['nomor_telepon'],
                            client_data['kategori_usaha'], client_data['lokasi'],
                            client_data['riwayat_transaksi'], analysis_result['skor_potensi'],
                            analysis_result['segmentasi'], analysis_result['prioritas'],
                            analysis_result['kategori_rekomendasi']
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
            return jsonify({'error': f'Failed to process CSV: {str(e)}'}), 500
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
    """Download CSV results"""
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
        
        # Create CSV in memory
        output = io.StringIO()
        fieldnames = ['client_name', 'phone_number', 'business_category', 'location', 
                     'potential_score', 'segmentation', 'priority', 'recommendation_category']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'client_name': result['client_name'],
                'phone_number': result['phone_number'],
                'business_category': result['business_category'],
                'location': result['location'],
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
    
