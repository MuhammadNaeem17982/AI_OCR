from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from mrctxtr import process_file as process_mrct, remove_personal_info as remove_mrct_info, generate_explanation as explain_mrct
from labextr import process_file_lab, remove_personal_info_lab, generate_explanation_lab  # Уникальные функции для lab

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png', 'docx'}

# Ensure upload and processed folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'file_type' not in request.form:
        return redirect(request.url)
    
    file = request.files['file']
    file_type = request.form['file_type']  # Получаем выбранный тип файла
    
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Выбор скрипта на основе типа файла
        if file_type == 'mrct':
            extracted_text = process_mrct(filepath)
            cleaned_text = remove_mrct_info(extracted_text)
            explanation = explain_mrct(cleaned_text)
        elif file_type == 'lab':
            extracted_text = process_file_lab(filepath)  # Уникальная функция для lab
            cleaned_text = remove_personal_info_lab(extracted_text)  # Уникальная функция для lab
            explanation = generate_explanation_lab(cleaned_text)  # Уникальная функция для lab
        else:
            return redirect(url_for('index'))

        # Save processed result
        processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], f"processed_{filename}.txt")
        with open(processed_filepath, 'w', encoding='utf-8') as f:
            f.write(explanation)

        # Передача всех данных в шаблон
        return render_template(
            'result.html',
            filename=filename,
            extracted_text=extracted_text,
            cleaned_text=cleaned_text,
            explanation=explanation
        )
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=8080)