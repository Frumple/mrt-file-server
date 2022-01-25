from flask import Blueprint, abort, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from mrt_file_server import app, maps
from mrt_file_server.utils.file_utils import get_filesize, split_file_root_and_extension, file_exists_in_dir
from mrt_file_server.utils.flash_utils import flash_by_key
from mrt_file_server.utils.log_utils import log_info, log_warn, log_error
from mrt_file_server.utils.string_utils import str_contains_whitespace
from mrt_file_server.utils.nbt_utils import load_compressed_nbt_file, load_compressed_nbt_buffer, save_compressed_nbt_file, get_nbt_map_value, set_nbt_map_byte_value

import os
import re

map_blueprint = Blueprint("map", __name__, url_prefix="/map")

@app.route("/map/upload", methods = ["GET", "POST"])
def route_map_upload():
  if request.method == "POST":
    upload_maps()

  last_allowed_id_range = app.config["MAP_UPLOAD_LAST_ALLOWED_ID_RANGE"]
  last_map_id = get_last_map_id()

  return render_template("map/upload/index.html", home = False, last_allowed_id_range = last_allowed_id_range, last_map_id = last_map_id)

def upload_maps():
  username = request.form["userName"] if "userName" in request.form else None

  if username == None or username == "":
    flash_by_key(app, "MAP_UPLOAD_USERNAME_EMPTY")
    log_warn("MAP_UPLOAD_USERNAME_EMPTY")
  elif str_contains_whitespace(request.form["userName"]):
    flash_by_key(app, "MAP_UPLOAD_USERNAME_WHITESPACE")
    log_warn("MAP_UPLOAD_USERNAME_WHITESPACE", username)
  elif "map" not in request.files:
    flash_by_key(app, "MAP_UPLOAD_NO_FILES")
    log_warn("MAP_UPLOAD_NO_FILES", username)
  else:
    files = request.files.getlist("map")

    if len(files) > app.config["MAP_UPLOAD_MAX_NUMBER_OF_FILES"]:
      flash_by_key(app, "MAP_UPLOAD_TOO_MANY_FILES")
      log_warn("MAP_UPLOAD_TOO_MANY_FILES", username)
    else:
      for file in files:
        upload_single_map(username, file)

def upload_single_map(username, file):
  uploads_dir = app.config["MAP_UPLOADS_DIR"]
  last_allowed_map_id_range = app.config["MAP_UPLOAD_LAST_ALLOWED_ID_RANGE"]
  last_map_id = get_last_map_id()
  file_map_id = get_file_map_id(file.filename)

  if file_map_id is None:
    flash_by_key(app, "MAP_UPLOAD_FILENAME_INVALID", file.filename)
    log_warn("MAP_UPLOAD_FILENAME_INVALID", file.filename, username)
    return
  elif file_map_id <= (last_map_id - last_allowed_map_id_range) or file_map_id > last_map_id:
    flash_by_key(app, "MAP_UPLOAD_MAP_ID_OUT_OF_RANGE", file.filename)
    log_warn("MAP_UPLOAD_MAP_ID_OUT_OF_RANGE", file.filename, username)
    return

  file.filename = secure_filename(file.filename)
  file_size = get_filesize(file)

  if file_size > app.config["MAP_UPLOAD_MAX_FILE_SIZE"]:
    flash_by_key(app, "MAP_UPLOAD_FILE_TOO_LARGE", file.filename)
    log_warn("MAP_UPLOAD_FILE_TOO_LARGE", file.filename, username)
  elif is_invalid_map_format(file):
    flash_by_key(app, "MAP_UPLOAD_MAP_FORMAT_INVALID", file.filename)
    log_warn("MAP_UPLOAD_MAP_FORMAT_INVALID", file.filename, username)
  elif is_existing_map_file_locked(file.filename):
    flash_by_key(app, "MAP_UPLOAD_EXISTING_MAP_LOCKED", file.filename)
    log_warn("MAP_UPLOAD_EXISTING_MAP_LOCKED", file.filename, username)
  else:
    try:
      existing_file_path = os.path.join(uploads_dir, file.filename)

      # Delete the existing map file, if it exists
      if os.path.isfile(existing_file_path):
        os.remove(existing_file_path)

      # Upload the new map file
      maps.save(file)

      # Lock the new map file
      nbt_file = load_compressed_nbt_file(existing_file_path)
      set_nbt_map_byte_value(nbt_file, "locked", 1)
      save_compressed_nbt_file(nbt_file)

      message = flash_by_key(app, "MAP_UPLOAD_SUCCESS", file.filename)
      log_info("MAP_UPLOAD_SUCCESS", file.filename, username)
    except Exception as e:
      message = flash_by_key(app, "MAP_UPLOAD_FAILURE", file.filename)
      log_info("MAP_UPLOAD_FAILURE", file.filename, username, e)

@app.route("/map/download", methods = ["GET", "POST"])
def route_map_download():
  response = False

  if request.method == "POST":
    create_map_download_link()

  return render_template("map/download/index.html", home = False)

def create_map_download_link():
  map_id_as_str = request.form["mapId"]
  file_name = "map_{}.dat".format(map_id_as_str)
  downloads_dir = app.config["MAP_DOWNLOADS_DIR"]

  if map_id_as_str == "":
    flash_by_key(app, "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_EMPTY")
    log_warn("MAP_DOWNLOAD_LINK_CREATION_MAP_ID_EMPTY")
    return

  map_id_as_int = parse_map_id_as_integer(map_id_as_str)

  if map_id_as_int is None:
    flash_by_key(app, "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_INVALID", file_name)
    log_warn("MAP_DOWNLOAD_LINK_CREATION_MAP_ID_INVALID", file_name)
    return

  last_map_id = get_last_map_id()

  if map_id_as_int < 0 or map_id_as_int > last_map_id:
    flash_by_key(app, "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_OUT_OF_RANGE", file_name)
    log_warn("MAP_DOWNLOAD_LINK_CREATION_MAP_ID_OUT_OF_RANGE", file_name)
    return

  secure_file_name = secure_filename(file_name)

  if file_exists_in_dir(downloads_dir, secure_file_name):
    flash_by_key(app, "MAP_DOWNLOAD_LINK_CREATION_SUCCESS", secure_file_name)
    log_info("MAP_DOWNLOAD_LINK_CREATION_SUCCESS", secure_file_name)
  else:
    flash_by_key(app, "MAP_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND", secure_file_name)
    log_warn("MAP_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND", secure_file_name)

def parse_map_id_as_integer(map_id_as_str):
  try:
    return int(map_id_as_str)
  except ValueError:
    return None

@app.route("/map/download/<path:filename>")
def download_map(filename):
  downloads_dir = app.config["MAP_DOWNLOADS_DIR"]
  file_map_id = get_file_map_id(filename)

  if file_map_id is None:
    log_warn("MAP_DOWNLOAD_FORBIDDEN", filename)
    abort(403)

  response = send_from_directory(downloads_dir, filename, as_attachment = True)
  log_info("MAP_DOWNLOAD_SUCCESS", filename)
  return response

def get_last_map_id():
  uploads_dir = app.config["MAP_UPLOADS_DIR"]
  idcounts_file_path = os.path.join(uploads_dir, "idcounts.dat")
  idcounts_nbt = load_compressed_nbt_file(idcounts_file_path)
  return get_nbt_map_value(idcounts_nbt, "map")

def get_file_map_id(filename):
  match = re.search(r"(?<=^map_)\d+(?=\.dat$)", filename)
  if match:
    return int(match.group())
  return None

def is_invalid_map_format(file):
  try:
    # Check that all the required NBT map fields in the file exist
    compressed_buffer = file.getvalue()
    nbt_file = load_compressed_nbt_buffer(compressed_buffer)

    is_invalid = get_nbt_map_value(nbt_file, "dimension") is None or \
      get_nbt_map_value(nbt_file, "locked") is None or \
      get_nbt_map_value(nbt_file, "colors") is None or \
      get_nbt_map_value(nbt_file, "scale") is None or \
      get_nbt_map_value(nbt_file, "trackingPosition") is None or \
      get_nbt_map_value(nbt_file, "xCenter") is None or \
      get_nbt_map_value(nbt_file, "zCenter") is None

    return is_invalid

  # If there are any errors loading the file as an NBT, then the file is invalid
  except Exception as e:
    return True

def is_existing_map_file_locked(filename):
  uploads_dir = app.config["MAP_UPLOADS_DIR"]
  existing_file_path = os.path.join(uploads_dir, filename)

  if os.path.isfile(existing_file_path):
    existing_file_nbt = load_compressed_nbt_file(existing_file_path)
    locked_value = get_nbt_map_value(existing_file_nbt, "locked")
    return locked_value == 1

  return False
