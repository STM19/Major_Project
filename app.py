from flask import Flask, render_template, request, redirect, make_response
import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pdfkit

app = Flask(__name__)


sample_data = {
    'name': 'John Doe',
    'date': '2023-10-01',
    'chlorophyll': 3.5,
    'turbidity': 10.2,
    'nitrogen': 25.8,
   
}


path_wkhtmltopdf = r'C:\Users\kadam\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'tif', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('final.html')

@app.route('/process', methods=['POST'])
def process():
    if 'ftif' not in request.files:
        return redirect(request.url)
    file = request.files['ftif']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        result = process_image(filename)
        result.to_excel('result.xlsx', index=False)

    return redirect('/report')


def process_image(image_path):
    with rasterio.open(image_path) as src:
        image_data = src.read()
    spectral_signature = np.mean(image_data, axis=(1, 2))
    wavelengths = [f'B {i}' for i in range(1, len(image_data) + 1)]
    result = pd.DataFrame({'Wavelength': wavelengths, 'Average Pixel Value': spectral_signature})
    return result

@app.route('/explore')
def explore():
    return render_template('explore.html')

@app.route('/report')
def report():
    return render_template('report.html', report_data=sample_data)

@app.route('/download')
def download():
    report_data = sample_data
    report_html = render_template('report.html', report_data=report_data)
    pdfkit.from_string(report_html, 'report.pdf', configuration=config)
    response = make_response(open('report.pdf', 'rb').read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
