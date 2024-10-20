from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image
import os

app = Flask(__name__)
uploaded_image_path = './temp/images/uploaded_image.jpg'

# Define the temperature range for mapping
MIN_TEMP = 28.2  # Minimum temperature in °C
MAX_TEMP = 59.1  # Maximum temperature in °C

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    file.save(uploaded_image_path)
    return jsonify({'success': 'Image uploaded successfully'})

@app.route('/temp/images/uploaded_image.jpg')
def serve_image():
    return send_from_directory('temp/images', "uploaded_image.jpg")

@app.route('/temperature-data/<int:x>/<int:y>')
def calculate_temperature(x, y):
    img = Image.open(uploaded_image_path).convert('L')
    img = img.resize((400, 400))  # Resize to match displayed size

    pixel = img.getpixel((x, y))
    temp = MIN_TEMP + (pixel / 255) * (MAX_TEMP - MIN_TEMP)

    return jsonify({'temperature': temp})

if __name__ == '__main__':
    os.makedirs('temp/images/', exist_ok=True)  # Create the images directory if it doesn't exist
    app.run(debug=True)
