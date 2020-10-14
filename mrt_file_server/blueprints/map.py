from flask import Blueprint, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from mrt_file_server import app, maps
from mrt_file_server.utils.file_utils import get_filesize, split_file_root_and_extension, file_exists_in_dir
from mrt_file_server.utils.flash_utils import flash_by_key
from mrt_file_server.utils.log_utils import log_info, log_warn, log_error
from mrt_file_server.utils.string_utils import str_contains_whitespace
from mrt_file_server.utils.nbt_utils import load_nbt_file, save_nbt_file, set_nbt_map_byte_value

import os

map_blueprint = Blueprint("map", __name__, url_prefix="/map")

@app.route("/map/upload", methods = ["GET", "POST"])
def route_map_upload():
  if request.method == "POST":
    upload_maps()

  return render_template("map/upload/index.html", home = False)

def upload_maps():
  username = request.form["userName"] if "userName" in request.form else None

  if username == None or username == "":
    pass
    # TODO
    # flash_by_key(app, "MAP_UPLOAD_USERNAME_EMPTY")
    # log_warn("MAP_UPLOAD_USERNAME_EMPTY")
  elif str_contains_whitespace(request.form["userName"]):
    pass
    # TODO
    # flash_by_key(app, "MAP_UPLOAD_USERNAME_WHITESPACE")
    # log_warn("MAP_UPLOAD_USERNAME_WHITESPACE")
  elif "map" not in request.files:
    pass
    # TODO
    # flash_by_key(app, "MAP_UPLOAD_NO_FILES")
    # log_warn("MAP_UPLOAD_NO_FILES")
  else:
    files = request.files.getlist("map")

    if len(files) > app.config["MAP_UPLOAD_MAX_NUMBER_OF_FILES"]:
      pass
      # TODO
      # flash_by_key(app, "MAP_UPLOAD_TOO_MANY_FILES")
      # log_warn("MAP_UPLOAD_TOO_MANY_FILES")
    else:
      for file in files:
        upload_single_map(username, file)

def upload_single_map(username, file):
  uploads_dir = app.config["MAP_UPLOADS_DIR"]

  # TODO: Check for valid filename

  file.filename = secure_filename(file.filename)
  file_size = get_filesize(file)

  if file_size > app.config["MAP_UPLOAD_MAX_FILE_SIZE"]:
    pass
    # TODO
    # flash_by_key(app, "MAP_UPLOAD_FILE_TOO_LARGE", file.filename)
    # log_warn("MAP_UPLOAD_FILE_TOO_LARGE", file.filename)

  # TODO: Check if map ID is within range

  # TODO: Check if map format is invalid

  # TODO: Check if map is locked

  else:
    try:
      existing_file_path = os.path.join(uploads_dir, file.filename)

      # Delete the existing map file, if it exists
      if os.path.isfile(existing_file_path):
        os.remove(existing_file_path)

      # Upload the new map file
      maps.save(file)

      # Set the "locked" flag on the new map file to 1 (true)
      nbt_file = load_nbt_file(existing_file_path)
      set_nbt_map_byte_value(nbt_file, "locked", 1)
      save_nbt_file(nbt_file)

      message = flash_by_key(app, "MAP_UPLOAD_SUCCESS", file.filename)
      log_info("MAP_UPLOAD_SUCCESS", file.filename, username)
    except Exception as e:
      message = flash_by_key(app, "MAP_UPLOAD_FAILURE", file.filename)
      log_info("MAP_UPLOAD_FAILURE", file.filename, username, e)

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