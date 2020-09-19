from flask import Blueprint, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from mrt_file_server import app, schematics
from mrt_file_server.utils.file_utils import get_filesize, split_file_root_and_extension, file_exists_in_dir
from mrt_file_server.utils.flash_utils import flash_by_key
from mrt_file_server.utils.log_utils import log_info, log_warn, log_error
from mrt_file_server.utils.string_utils import str_contains_whitespace

map_blueprint = Blueprint("map", __name__, url_prefix="/map")

@app.route("/map/upload", methods = ["GET", "POST"])
def route_map_upload():
  if request.method == "POST":
    upload_maps()

  return render_template("map/upload/index.html", home = False)

def upload_maps():
  return

def upload_single_map():
  return

@app.route("/map/download", methods = ["GET", "POST"])
def route_map_download():
  response = False

  if request.method == "POST":
    response = create_map_download_link()

  if response:
    return response
  else:
    return render_template("map/download/index.html", home = False)

def create_map_download_link():
  return

@app.route("/map/download/<path:filename>")
def download_map(filename):
  return