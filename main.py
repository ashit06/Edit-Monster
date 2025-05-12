from flask import Flask, render_template, request, send_file
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# 1. Home page → renders home.html
@app.route('/')
def home():
    return render_template('home.html')

# 2. Convert page → renders convert.html
@app.route('/convert-page')
def convert_page():
    return render_template('convert.html')

# 3. Conversion handler → accepts upload, converts, returns file
@app.route('/convert', methods=['POST'])
def convert():
    image_file = request.files.get('image')
    target_format = request.form.get('format', '').lower()

    if not image_file or target_format not in {'png', 'jpg', 'bmp', 'webp'}:
        return "Invalid request", 400

    # Open with Pillow
    img = Image.open(image_file.stream)

    # Prepare in-memory buffer
    img_io = BytesIO()
    # Note: JPEG expects “JPEG” not “JPG”
    save_format = 'JPEG' if target_format == 'jpg' else target_format.upper()
    # Convert to RGB for JPEG if not already RGB
    if save_format == 'JPEG' and img.mode != 'RGB':
        img = img.convert('RGB')
    img.save(img_io, save_format)
    img_io.seek(0)

    # Send back with appropriate mimetype and download name
    return send_file(
        img_io,
        mimetype=f'image/{target_format}',
        as_attachment=True,
        download_name=f'converted.{target_format}'
    )

if __name__ == '__main__':
    app.run(debug=True)
