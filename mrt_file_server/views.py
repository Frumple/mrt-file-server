from flask import flash, Markup, request, render_template, send_from_directory
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
def route_schematic_upload():
  if request.method == 'POST':
    upload_schematics()

  return render_template('schematic/upload/index.html', home = False)

def upload_schematics():
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
  file_extension = get_file_extension(file.filename)
  filename_without_extension = get_filename_without_extension(file.filename)

  if file_extension != '.schematic' and file_extension != '.schem':
    flash_by_key(app, 'SCHEMATIC_UPLOAD_FILENAME_EXTENSION', file.filename)
    log_warn('SCHEMATIC_UPLOAD_FILENAME_EXTENSION', file.filename)
  elif filesize > app.config['MAX_UPLOAD_FILE_SIZE']:
    flash_by_key(app, 'SCHEMATIC_UPLOAD_FILE_TOO_LARGE', file.filename)
    log_warn('SCHEMATIC_UPLOAD_FILE_TOO_LARGE', file.filename)
  elif file_exists_in_dir(uploads_dir, filename_without_extension + '.schematic') or file_exists_in_dir(uploads_dir, filename_without_extension + '.schem'):
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
def route_schematic_download():
  response = False

  if request.method == 'POST':
    response = create_schematic_download_link()

  if response:
    return response
  else:
    return render_template('schematic/download/index.html', home = False)

def create_schematic_download_link():
  file_root = request.form['fileRoot']
  file_extension = request.form['fileExtension']
  file_name = "{}.{}".format(file_root, file_extension)
  downloads_dir = app.config['SCHEMATIC_DOWNLOADS_DIR']

  if file_root == "":
    flash_by_key(app, 'SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_EMPTY')
    log_warn('SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_EMPTY')
    return

  if file_extension not in ["schem", "schematic"]:
    flash_by_key(app, 'SCHEMATIC_DOWNLOAD_LINK_CREATION_INVALID_EXTENSION', file_name)
    log_warn('SCHEMATIC_DOWNLOAD_LINK_CREATION_INVALID_EXTENSION', file_name)
    return

  if str_contains_whitespace(file_root):
    flash_by_key(app, 'SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_WHITESPACE', file_name)
    log_warn('SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_WHITESPACE', file_name)
    return

  secure_file_name = "{}.{}".format(secure_filename(file_root), file_extension)

  if file_exists_in_dir(downloads_dir, secure_file_name):
    flash_by_key(app, 'SCHEMATIC_DOWNLOAD_LINK_CREATION_SUCCESS', secure_file_name)
    log_info('SCHEMATIC_DOWNLOAD_LINK_CREATION_SUCCESS', secure_file_name)
    return
  else:
    flash_by_key(app, 'SCHEMATIC_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND', secure_file_name)
    log_warn('SCHEMATIC_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND', secure_file_name)
    return

@app.route("/schematic/download/<path:filename>")
def download_schematic(filename):
  log_info('SCHEMATIC_DOWNLOAD_SUCCESS', filename)
  return send_from_directory(app.config['SCHEMATIC_DOWNLOADS_DIR'], filename, as_attachment = True)

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
  flash_message = get_flash_message(app, key)

  if filename:
    flash(Markup("{}: {}".format(filename, flash_message.message.format(filename))), flash_message.category)
  else:
    flash(Markup(flash_message.message), flash_message.category)

def get_filesize(file):
  file.seek(0, os.SEEK_END)
  filesize = file.tell()
  file.seek(0)
  return filesize

def get_file_extension(filename):
  return os.path.splitext(filename)[1]

def get_filename_without_extension(filename):
  return os.path.splitext(filename)[0]

def file_exists_in_dir(dir, filename):
  filepath = os.path.join(dir, filename)
  return os.path.isfile(filepath)

def str_contains_whitespace(str):
  return bool(re.search(r"\s", str))