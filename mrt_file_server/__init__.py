from flask import Flask, flash, request, render_template, send_from_directory
from flask_uploads import UploadSet, configure_uploads

import os

def configure_instance_folders(app):
  instance_path = app.instance_path

  app.config['DOWNLOADS_DIR'] = downloads_dir = os.path.join(instance_path, "downloads")
  app.config['WORLD_DOWNLOADS_DIR'] = os.path.join(downloads_dir, "worlds")
  app.config['SCHEMATIC_DOWNLOADS_DIR'] = os.path.join(downloads_dir, "schematics")

  app.config['UPLOADS_DIR'] = uploads_dir = os.path.join(instance_path, "uploads")
  app.config['SCHEMATIC_UPLOADS_DIR'] = schematic_uploads_dir = os.path.join(uploads_dir, "schematics")

  # Used by Flask-Uploads to determine where to upload schematics
  app.config['UPLOADED_SCHEMATICS_DEST'] = schematic_uploads_dir

app = Flask(__name__)
app.config.from_pyfile("config.py")
configure_instance_folders(app)

schematics = UploadSet('schematics', extensions = ['schematic'])
configure_uploads(app, schematics)

@app.route("/")
def index():
  return render_template('index.html', footer = False)

@app.route("/schematic/upload", methods = ['GET', 'POST'])
def upload_schematics():
  if request.method == 'POST' and 'schematic' in request.files:
    files = request.files.getlist('schematic')
    for file in files:
      upload_single_schematic(file)

  return render_template('schematic/upload/index.html', footer = True)

def upload_single_schematic(file):
  filename = file.filename

  try:
    schematics.save(file)
    message = "Success!"
  except Exception as e:
    message = "Failed!"

  flash("{}: {}".format(filename, message))

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