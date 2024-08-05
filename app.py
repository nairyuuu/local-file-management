from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Config.upload_folder

def get_files_and_folders(path, sort_by=None, order='asc', search_query=None):
    files_and_folders = []
    for entry in os.listdir(path):
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            files_and_folders.append({
                'name': entry,
                'type': 'folder',
                'size': 0,
                'date': datetime.fromtimestamp(os.path.getmtime(entry_path))
            })
        elif os.path.isfile(entry_path):
            stat = os.stat(entry_path)
            files_and_folders.append({
                'name': entry,
                'type': 'file',
                'size': stat.st_size,
                'date': datetime.fromtimestamp(stat.st_mtime)
            })

    if search_query:
        files_and_folders = [e for e in files_and_folders if search_query.lower() in e['name'].lower()]

    reverse = (order == 'desc')
    if sort_by == 'name':
        files_and_folders.sort(key=lambda x: x['name'], reverse=reverse)
    elif sort_by == 'size' and 'size' in files_and_folders[0]:
        files_and_folders.sort(key=lambda x: x['size'], reverse=reverse)
    elif sort_by == 'date':
        files_and_folders.sort(key=lambda x: x['date'], reverse=reverse)

    return files_and_folders

@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    sort_by = request.args.get('sort_by')
    order = request.args.get('order', 'asc')
    search_query = request.args.get('search')
    path = os.path.join(app.config['UPLOAD_FOLDER'], subpath) if subpath else app.config['UPLOAD_FOLDER']
    print(subpath)
    # Ensure path is within the allowed directory
    if not os.path.commonpath([path, app.config['UPLOAD_FOLDER']]) == app.config['UPLOAD_FOLDER']:
        return "Invalid directory path", 403

    files_and_folders = get_files_and_folders(path, sort_by, order, search_query)
    relative_path = subpath if subpath else ''
    return render_template('index.html', files_and_folders=files_and_folders, sort_by=sort_by, order=order, search_query=search_query, current_path=relative_path)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/preview/<path:filename>')
def preview_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return f'<pre>{content}</pre>'
    return 'File not found', 404

@app.route('/<path:subpath>')
def navigate(subpath):
    # Normalize the path to ensure it is valid
    safe_subpath = secure_filename(subpath)
    print(subpath)
    return redirect(url_for('index', subpath=safe_subpath))

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
