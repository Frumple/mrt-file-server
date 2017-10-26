from flask import Flask, request, render_template, flash, send_from_directory
from flask_uploads import UploadSet, configure_uploads

app = Flask(__name__)
app.config.from_pyfile("config.py")

schematics = UploadSet('schematics', extensions = ['schematic'])
configure_uploads(app, schematics)

@app.route("/")
def index():
  return render_template('index.html', footer = False)

@app.route("/schematic/upload", methods = ['GET', 'POST'])
def upload_schematic():
  if request.method == 'POST' and 'schematic' in request.files:
    filename = schematics.save(request.files['schematic'])
    flash('Success!')
  return render_template('schematic/upload/index.html', footer = True)

@app.route("/schematic/download")
def download_schematic():
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