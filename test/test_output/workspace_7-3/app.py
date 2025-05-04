import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from image_processor import ImageProcessor
from storage import Storage

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

storage = Storage(app.config['UPLOAD_FOLDER'])
processor = ImageProcessor()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = storage.save(file, filename)
        return jsonify({
            'filename': filename,
            'url': storage.get_url(filename)
        })
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process', methods=['POST'])
def process_image():
    data = request.json
    filename = data.get('filename')
    operations = data.get('operations', [])
    
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
        
    try:
        processed_path = processor.process(
            storage.get_path(filename),
            operations
        )
        return jsonify({
            'url': storage.get_url(os.path.basename(processed_path))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)