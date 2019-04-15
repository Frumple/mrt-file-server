from flask import flash, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

from mrt_file_server import app, schematics, logger
from mrt_file_server.request_log_adapter import RequestLogAdapter

import os
import re

log_adapter = RequestLogAdapter(logger, request)

# Routes

@app.route("/")
def index():
  return render_template('index.html', home = True)

@app.route("/schematic/upload", methods = ['GET', 'POST'])
def upload_schematics():
  if request.method == 'POST':
    upload_schematics_post()

  return render_template('schematic/upload/index.html', home = False)

def upload_schematics_post():
  if 'userName' not in request.form or request.form['userName'] == "":
    flash_by_key(app, 'SCHEMATIC_UPLOAD_USERNAME_EMPTY')
    log_warn('SCHEMATIC_UPLOAD_USERNAME_EMPTY')
  elif str_contains_whitespace(request.form['userName']):
    flash_by_key(app, 'SCHEMATIC_UPLOAD_USERNAME_WHITESPACE')
    log_warn('SCHEMATIC_UPLOAD_USERNAME_WHITESPACE', request.form['userName'])
  elif 'schematic' not in request.files:
    flash_by_key(app, 'SCHEMATIC_UPLOAD_NO_FILES')
    log_warn('SCHEMATIC_UPLOAD_NO_FILES')
  else:
    files = request.files.getlist('schematic')

    if len(files) > app.config['MAX_NUMBER_OF_UPLOAD_FILES']:
      flash_by_key(app, 'SCHEMATIC_UPLOAD_TOO_MANY_FILES')
      log_warn('SCHEMATIC_UPLOAD_TOO_MANY_FILES')
    else:
      for file in files:
        upload_single_schematic(file)

def upload_single_schematic(file):
  username = request.form['userName']
  file.filename = "{}-{}".format(username, file.filename)
  uploads_dir = app.config['SCHEMATIC_UPLOADS_DIR']

  if str_contains_whitespace(file.filename):
    flash_by_key(app, 'SCHEMATIC_UPLOAD_FILENAME_WHITESPACE', file.filename)
    log_warn('SCHEMATIC_UPLOAD_FILENAME_WHITESPACE', file.filename)
    return

  file.filename = secure_filename(file.filename)
  filesize = get_filesize(file)
  
  if get_file_extension(file.filename) != '.schematic' and get_file_extension(file.filename) != '.schem':
    flash_by_key(app, 'SCHEMATIC_UPLOAD_FILENAME_EXTENSION', file.filename)
    log_warn('SCHEMATIC_UPLOAD_FILENAME_EXTENSION', file.filename)
  elif filesize > app.config['MAX_UPLOAD_FILE_SIZE']:
    flash_by_key(app, 'SCHEMATIC_UPLOAD_FILE_TOO_LARGE', file.filename)
    log_warn('SCHEMATIC_UPLOAD_FILE_TOO_LARGE', file.filename)
  elif file_exists_in_dir(uploads_dir, get_file_name(file.filename) + '.schematic') or file_exists_in_dir(uploads_dir, get_file_name(file.filename) + '.schem'):
    flash_by_key(app, 'SCHEMATIC_UPLOAD_FILE_EXISTS', file.filename)
    log_warn('SCHEMATIC_UPLOAD_FILE_EXISTS', file.filename)
  else:
    try:
      schematics.save(file)

      message = flash_by_key(app, 'SCHEMATIC_UPLOAD_SUCCESS', file.filename)
      log_info('SCHEMATIC_UPLOAD_SUCCESS', file.filename)
    except Exception as e:
      message = flash_by_key(app, 'SCHEMATIC_UPLOAD_FAILURE', file.filename)
      log_error('SCHEMATIC_UPLOAD_FAILURE', file.filename, e)

@app.route("/schematic/download", methods = ['GET', 'POST'])
def download_schematic():
  response = False

  if request.method == 'POST':
    response = download_schematic_post()

  if response:
    return response
  else:
    return render_template('schematic/download/index.html', home = False)

def download_schematic_post():
  filename = request.form['fileName']
  downloads_dir = app.config['SCHEMATIC_DOWNLOADS_DIR']

  if filename == "":
    flash_by_key(app, 'SCHEMATIC_DOWNLOAD_FILENAME_EMPTY')
    log_warn('SCHEMATIC_DOWNLOAD_FILENAME_EMPTY')
    return

  if str_contains_whitespace(filename):
    flash_by_key(app, 'SCHEMATIC_DOWNLOAD_FILENAME_WHITESPACE')
    log_warn('SCHEMATIC_DOWNLOAD_FILENAME_WHITESPACE', filename)
    return

  filename = "{}.schematic".format(secure_filename(filename))

  if file_exists_in_dir(downloads_dir, filename):
    log_info('SCHEMATIC_DOWNLOAD_SUCCESS', filename)
    return send_from_directory(downloads_dir, filename, as_attachment = True)
  else:
    flash_by_key(app, 'SCHEMATIC_DOWNLOAD_FILE_NOT_FOUND', filename)
    log_warn('SCHEMATIC_DOWNLOAD_FILE_NOT_FOUND', filename)
    return

@app.route("/world/download/terms")
def show_world_downloads_terms():
  return render_template('world/download/terms.html', home = False)

@app.route("/world/download")
def list_world_downloads():
  return render_template('world/download/index.html', home = False)

@app.route("/world/download/<path:filename>")
def download_world(filename):
  log_info('WORLD_DOWNLOAD_SUCCESS', filename)
  return send_from_directory(app.config['WORLD_DOWNLOADS_DIR'], filename, as_attachment = True)

# Helper Functions

def get_log_message(app, key):
  return app.config['LOG_MESSAGES'][key]

def log_info(key, *args, **kwargs):
  log(log_adapter.info, key, *args, **kwargs)

def log_warn(key, *args, **kwargs):
  log(log_adapter.warn, key, *args, **kwargs)

def log_error(key, *args, **kwargs):
  log(log_adapter.error, key, *args, **kwargs)

def log(log_function, key, *args, **kwargs):
  log_function(get_log_message(app, key), *args, **kwargs)

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

def get_file_name(filename):
  return os.path.splitext(filename)[0]

def file_exists_in_dir(dir, filename):
  filepath = os.path.join(dir, filename)
  return os.path.isfile(filepath)

def str_contains_whitespace(str):
  return bool(re.search(r"\s", str))  