from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
import uuid
from watermark import embed_watermark, extract_watermark
from utils import log_request  # Importing the log_request function from utils.py

app = Flask(__name__)
CORS(app)

# Add MongoDB connection with error handling
try:
    client = MongoClient('mongodb://localhost:27017/')
    client.server_info()  # Test connection
    db = client['watermarkDB']
    print("MongoDB connected successfully")
except Exception as e:
    print(f"MongoDB Error: {e}")
    db = None

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    email = request.form['email']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    media_id, output_path = embed_watermark(filepath, email)
    db.media.insert_one({'media_id': media_id, 'email': email, 'file': output_path})
    
    log_request(f"Uploaded file: {filename} with media_id: {media_id}")  # Log the request
    
    return jsonify({'message': 'File uploaded successfully', 'media_id': media_id})

@app.route('/check', methods=['POST'])
def check_watermark():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    media_id = extract_watermark(filepath)
    if media_id:
        return jsonify({'media_id': media_id})
    else:
        return jsonify({'error': 'No watermark found'}), 400

@app.route('/status', methods=['GET'])
def status():
    if db:
        return jsonify({'status': 'running', 'db': 'connected'})
    return jsonify({'status': 'running', 'db': 'disconnected'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
