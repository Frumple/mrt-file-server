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
  filename = file.filename

  if str_contains_whitespace(filename):
    flash_by_key(app, 'UPLOAD_FILENAME_WHITESPACE', filename)
    return

  filename = secure_filename(filename)
  filesize = get_filesize(file)
  
  if get_file_extension(filename) != '.schematic':
    flash_by_key(app, 'UPLOAD_FILENAME_EXTENSION', filename)
  elif filesize > app.config['MAX_UPLOAD_FILE_SIZE']:
    flash_by_key(app, 'UPLOAD_FILE_TOO_LARGE', filename)
  elif file_exists_in_upload_dir(filename):
    flash_by_key(app, 'UPLOAD_FILE_EXISTS', filename)
  else:
    try:
      schematics.save(file)

      message = flash_by_key(app, 'UPLOAD_SUCCESS', filename)
    except Exception as e:
      message = flash_by_key(app, 'UPLOAD_FAILURE', filename)

@app.route("/schematic/download")
def download_schematics():
  return render_template('schematic/download/index.html', footer = True)

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

def file_exists_in_upload_dir(filename):
  filepath = os.path.join(app.config['SCHEMATIC_UPLOADS_DIR'], filename)
  return os.path.isfile(filepath)

def str_contains_whitespace(str):
  return bool(re.search('\s', str))  