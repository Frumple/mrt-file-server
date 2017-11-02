from flask import Flask, flash, request, render_template, send_from_directory
from flask_uploads import UploadSet, configure_uploads

import os
import re

def configure_instance_folders(app):
  instance_path = app.instance_path

  app.config['DOWNLOADS_DIR'] = downloads_dir = os.path.join(instance_path, "downloads")
  app.config['WORLD_DOWNLOADS_DIR'] = os.path.join(downloads_dir, "worlds")
  app.config['SCHEMATIC_DOWNLOADS_DIR'] = os.path.join(downloads_dir, "schematics")

  app.config['UPLOADS_DIR'] = uploads_dir = os.path.join(instance_path, "uploads")
  app.config['SCHEMATIC_UPLOADS_DIR'] = schematic_uploads_dir = os.path.join(uploads_dir, "schematics")

  # Used by Flask-Uploads to determine where to upload schematics
  app.config['UPLOADED_SCHEMATICS_DEST'] = schematic_uploads_dir

def configure_flash_messages(app):
  messages = {
    "UPLOAD_SUCCESS":             "Upload Successful!",
    "UPLOAD_FAILURE":             "Upload Failed!",
    "UPLOAD_USERNAME_EMPTY":      "Upload Failed! Username must not be empty.",
    "UPLOAD_USERNAME_WHITESPACE": "Upload Failed! Username must not contain spaces.",
    "UPLOAD_NO_FILES":            "Upload Failed! No files selected.",
    "UPLOAD_TOO_MANY_FILES":      "Upload Failed! A maximum of {} files can be uploaded at one time.".format( \
                                  app.config['MAX_NUMBER_OF_UPLOAD_FILES']),
    "UPLOAD_FILE_TOO_LARGE":      "Upload Failed! File size is larger than allowed maximum of {} bytes".format( \
                                  app.config['MAX_CONTENT_LENGTH'])
  }

  app.config['FLASH_MESSAGES'] = messages

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

def str_contains_whitespace(str):
  return bool(re.search('\s', str))

app = Flask(__name__)
app.config.from_pyfile("config.py")

configure_instance_folders(app)
configure_flash_messages(app)

schematics = UploadSet('schematics', extensions = ['schematic'])
configure_uploads(app, schematics)

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
  filesize = get_filesize(file)

  if filesize > app.config['MAX_UPLOAD_FILE_SIZE']:
    flash_by_key(app, 'UPLOAD_FILE_TOO_LARGE', filename)
    return

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

if __name__ == "__main__":
  app.run()