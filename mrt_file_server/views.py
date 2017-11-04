from flask import flash, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

from mrt_file_server import app, schematics

import os
import re

@app.route("/")
def index():
  return render_template('index.html', footer = False)

@app.route("/schematic/upload", methods = ['GET', 'POST'])
def upload_schematics():
  if request.method == 'POST':
    upload_schematics_post()

  return render_template('schematic/upload/index.html', footer = True)

def upload_schematics_post():
  if 'userName' not in request.form or request.form['userName'] == "":
    flash_by_key(app, 'UPLOAD_USERNAME_EMPTY')
  elif str_contains_whitespace(request.form['userName']):
    flash_by_key(app, 'UPLOAD_USERNAME_WHITESPACE')
  elif 'schematic' not in request.files:
    flash_by_key(app, 'UPLOAD_NO_FILES')
  else:
    files = request.files.getlist('schematic')

    if len(files) > app.config['MAX_NUMBER_OF_UPLOAD_FILES']:
      flash_by_key(app, 'UPLOAD_TOO_MANY_FILES')
    else:
      for file in files:
        upload_single_schematic(file)

def upload_single_schematic(file):
  username = request.form['userName']
  file.filename = "{}-{}".format(username, file.filename)
  uploads_dir = app.config['SCHEMATIC_UPLOADS_DIR']

  if str_contains_whitespace(file.filename):
    flash_by_key(app, 'UPLOAD_FILENAME_WHITESPACE', file.filename)
    return

  file.filename = secure_filename(file.filename)
  filesize = get_filesize(file)
  
  if get_file_extension(file.filename) != '.schematic':
    flash_by_key(app, 'UPLOAD_FILENAME_EXTENSION', file.filename)
  elif filesize > app.config['MAX_UPLOAD_FILE_SIZE']:
    flash_by_key(app, 'UPLOAD_FILE_TOO_LARGE', file.filename)
  elif file_exists_in_dir(uploads_dir, file.filename):
    flash_by_key(app, 'UPLOAD_FILE_EXISTS', file.filename)
  else:
    try:
      schematics.save(file)

      message = flash_by_key(app, 'UPLOAD_SUCCESS', file.filename)
    except Exception as e:
      message = flash_by_key(app, 'UPLOAD_FAILURE', file.filename)

@app.route("/schematic/download", methods = ['GET', 'POST'])
def download_schematic():
  response = False

  if request.method == 'POST':
    response = download_schematic_post()

  if response:
    return response
  else:
    return render_template('schematic/download/index.html', footer = True)

def download_schematic_post():
  filename = request.form['fileName']
  downloads_dir = app.config['SCHEMATIC_DOWNLOADS_DIR']

  if filename == "":
    flash_by_key(app, 'DOWNLOAD_FILENAME_EMPTY')
    return

  if str_contains_whitespace(filename):
    flash_by_key(app, 'DOWNLOAD_FILENAME_WHITESPACE')
    return

  filename = "{}.schematic".format(secure_filename(filename))

  if file_exists_in_dir(downloads_dir, filename):
    return send_from_directory(downloads_dir, filename, as_attachment = True)
  else:
    flash_by_key(app, 'DOWNLOAD_FILE_NOT_FOUND', filename)
    return

@app.route("/world/download/terms")
def show_world_downloads_terms():
  return render_template('world/download/terms.html', footer = True)

@app.route("/world/download")
def list_world_downloads():
  return render_template('world/download/index.html', footer = True)

@app.route("/world/download/<path:filename>")
def download_world(filename):
  return send_from_directory(app.config['WORLD_DOWNLOADS_DIR'], filename, as_attachment = True)

def get_flash_message(app, key):
  return app.config['FLASH_MESSAGES'][key]

def flash_by_key(app, key, filename = None):
  message = get_flash_message(app, key)

  if filename:
    flash("{}: {}".format(filename, message))
  else:
    flash(message)

def get_filesize(file):
  file.seek(0, os.SEEK_END)
  filesize = file.tell()
  file.seek(0)
  return filesize

def get_file_extension(filename):
  return os.path.splitext(filename)[1]

def file_exists_in_dir(dir, filename):
  filepath = os.path.join(dir, filename)
  return os.path.isfile(filepath)

def str_contains_whitespace(str):
  return bool(re.search('\s', str))  