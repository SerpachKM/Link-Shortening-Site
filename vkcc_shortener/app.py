from flask import Flask, request, send_file, render_template, jsonify
from bs4 import BeautifulSoup
import pandas as pd
import requests
from io import BytesIO
import openpyxl
import zipfile

app = Flask(__name__)

# Ваш API токен ВК
VK_API_TOKEN = "vk1.a.cMyVTFqAmHn0dHpKzZhiol52nl2GyPDYrcr9EiTsSHrzP8HgZK3lWxOqFV4kDiPhtr7oLyonp-ueIPAOJk_bNhytGbnf2uAYdQnYXGv55Hiy9sFCqyn5X8Kp5BzdZNsbBfy5fvmZgM1pFtOkvO4RB34xVNSlQkwNEPyRtFkejJdFkXcnsxj8O9DUDYiNwoCs8t5cbiG71a6yOHI31yol9Q"
VK_CC_API_URL = 'https://api.vk.com/method/utils.getShortLink'

@app.route('/')
def index():
    return render_template('main_page.html')

def shorten_url(long_url):
    params = {
        'access_token': VK_API_TOKEN,
        'url': long_url,
        'v': '5.131'
    }
    response = requests.get(VK_CC_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'response' in data:
            return data['response']['short_url']
    return long_url

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'error': 'No selected file'}), 400

    # Создаем BytesIO для хранения ZIP-архива
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
                df['Short URL'] = df.iloc[:, 0].apply(shorten_url)
                
                # Сохраняем DataFrame в временный файл
                temp_output = BytesIO()
                with pd.ExcelWriter(temp_output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                temp_output.seek(0)
                
                # Добавляем временный файл в ZIP-архив
                zip_file.writestr(file.filename, temp_output.read())

    # Сбросим указатель на начало файла перед отправкой
    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        download_name='shortened_links.zip',
        as_attachment=True,
        mimetype='application/zip'
    )

if __name__ == '__main__':
    app.run(debug=True)



