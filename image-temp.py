from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image
import os
from openpyxl import Workbook, load_workbook
import pandas as pd


app = Flask(__name__)
uploaded_image_path = './temp/images/uploaded_image.jpg'

# Define the temperature range for mapping
MIN_TEMP = 28.2  # Minimum temperature in °C
MAX_TEMP = 59.1  # Maximum temperature in °C
TEMP_DATA = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    global original_filename 
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    original_filename = os.path.splitext(file.filename)[0]
    
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
    TEMP_DATA.append((x,y,temp))
    return jsonify({'temperature': temp})

@app.route('/save-to-excel', methods=['POST'])
def save_to_excel():
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)

    # Create the Excel file path
    excel_filename = f"{original_filename}_temp_data.xlsx"
    excel_path = os.path.join(output_dir, excel_filename)
    try:
        # Convert TEMP_DATA to a DataFrame
        df = pd.DataFrame(TEMP_DATA)

        # Keep only unique rows
        df = df.drop_duplicates()

        # Save the data to an Excel file
        df.to_excel(excel_path, index=False, header=['x-coordinate','y-coordinate','Temp'])

        return jsonify({'success': True, 'file': excel_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    os.makedirs('temp/images/', exist_ok=True)  # Create the images directory if it doesn't exist
    app.run(debug=True)
