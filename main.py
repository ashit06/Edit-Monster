from flask import Flask, render_template, request, send_file
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Resize feature
@app.route('/resize', methods=['GET', 'POST'])
def resize():
    if request.method == 'POST':
        image_file = request.files.get('image')
        if not image_file:
            return "No image uploaded", 400

        # Get resize dimensions
        width = request.form.get('width')
        height = request.form.get('height')
        
        if not width or not height:
            return "Width and height are required", 400

        # Process image
        img = Image.open(image_file.stream)
        img = img.resize((int(width), int(height)))
        
        # Save and return
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='resized.png')

    return render_template('resize.html')

# Crop feature
@app.route('/crop', methods=['GET', 'POST'])
def crop():
    if request.method == 'POST':
        image_file = request.files.get('image')
        if not image_file:
            return "No image uploaded", 400

        # Get crop coordinates
        x = int(request.form.get('x', 0))
        y = int(request.form.get('y', 0))
        width = int(request.form.get('width', 0))
        height = int(request.form.get('height', 0))

        # Process image
        img = Image.open(image_file.stream)
        img = img.crop((x, y, x + width, y + height))
        
        # Save and return
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='cropped.png')

    return render_template('crop.html')

# Rotate/Flip feature
@app.route('/rotate', methods=['GET', 'POST'])
def rotate():
    if request.method == 'POST':
        image_file = request.files.get('image')
        if not image_file:
            return "No image uploaded", 400

        # Get rotation angle and flip type
        angle = float(request.form.get('angle', 0))
        flip = request.form.get('flip', '')

        # Process image
        img = Image.open(image_file.stream)
        if angle:
            img = img.rotate(-angle, expand=True)
        if flip == 'horizontal':
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif flip == 'vertical':
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

        # Save and return
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='rotated.png')

    return render_template('rotate.html')

# Filters feature
@app.route('/filters', methods=['GET', 'POST'])
def filters():
    if request.method == 'POST':
        image_file = request.files.get('image')
        if not image_file:
            return "No image uploaded", 400

        filter_type = request.form.get('filter')
        img = Image.open(image_file.stream)

        if filter_type == 'grayscale':
            img = img.convert('L')
        elif filter_type == 'sepia':
            img = img.convert('RGB')
            width, height = img.size
            pixels = img.load()
            for py in range(height):
                for px in range(width):
                    r, g, b = img.getpixel((px, py))
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[px, py] = (min(tr,255), min(tg,255), min(tb,255))
        elif filter_type == 'blur':
            from PIL import ImageFilter
            img = img.filter(ImageFilter.BLUR)

        # Save and return
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='filtered.png')

    return render_template('filters.html')

# Compression feature
@app.route('/compress', methods=['GET', 'POST'])
def compress():
    if request.method == 'POST':
        image_file = request.files.get('image')
        if not image_file:
            return "No image uploaded", 400

        quality = int(request.form.get('quality', 95))
        img = Image.open(image_file.stream)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save with compression
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=quality)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='compressed.jpg')

    return render_template('compress.html')

# Original format conversion route
@app.route('/convert-page')
def convert_page():
    return render_template('convert.html')

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
    save_format = 'JPEG' if target_format == 'jpg' else target_format.upper()
    if save_format == 'JPEG' and img.mode != 'RGB':
        img = img.convert('RGB')
    img.save(img_io, save_format)
    img_io.seek(0)

    return send_file(
        img_io,
        mimetype=f'image/{target_format}',
        as_attachment=True,
        download_name=f'converted.{target_format}'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
