from flask import Blueprint, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from mrt_file_server import app, schematics
from mrt_file_server.utils.file_utils import get_filesize, split_file_root_and_extension, file_exists_in_dir
from mrt_file_server.utils.flash_utils import flash_by_key
from mrt_file_server.utils.log_utils import log_info, log_warn, log_error
from mrt_file_server.utils.string_utils import str_contains_whitespace

schematic_blueprint = Blueprint("schematic", __name__, url_prefix="/schematic")

@app.route("/schematic/upload", methods = ["GET", "POST"])
def route_schematic_upload():
  if request.method == "POST":
    upload_schematics()

  return render_template("schematic/upload/index.html", home = False)

def upload_schematics():
  if "userName" not in request.form or request.form["userName"] == "":
    flash_by_key(app, "SCHEMATIC_UPLOAD_USERNAME_EMPTY")
    log_warn("SCHEMATIC_UPLOAD_USERNAME_EMPTY")
  elif str_contains_whitespace(request.form["userName"]):
    flash_by_key(app, "SCHEMATIC_UPLOAD_USERNAME_WHITESPACE")
    log_warn("SCHEMATIC_UPLOAD_USERNAME_WHITESPACE", request.form["userName"])
  elif "schematic" not in request.files:
    flash_by_key(app, "SCHEMATIC_UPLOAD_NO_FILES")
    log_warn("SCHEMATIC_UPLOAD_NO_FILES")
  else:
    files = request.files.getlist("schematic")

    if len(files) > app.config["SCHEMATIC_UPLOAD_MAX_NUMBER_OF_FILES"]:
      flash_by_key(app, "SCHEMATIC_UPLOAD_TOO_MANY_FILES")
      log_warn("SCHEMATIC_UPLOAD_TOO_MANY_FILES")
    else:
      for file in files:
        upload_single_schematic(file)

def upload_single_schematic(file):
  username = request.form["userName"]
  file.filename = "{}-{}".format(username, file.filename)
  uploads_dir = app.config["SCHEMATIC_UPLOADS_DIR"]

  if str_contains_whitespace(file.filename):
    flash_by_key(app, "SCHEMATIC_UPLOAD_FILENAME_WHITESPACE", file.filename)
    log_warn("SCHEMATIC_UPLOAD_FILENAME_WHITESPACE", file.filename)
    return

  file.filename = secure_filename(file.filename)
  file_size = get_filesize(file)
  file_pair = split_file_root_and_extension(file.filename)
  file_root = file_pair[0]
  file_extension = file_pair[1]

  if file_extension != ".schematic" and file_extension != ".schem":
    flash_by_key(app, "SCHEMATIC_UPLOAD_FILENAME_EXTENSION", file.filename)
    log_warn("SCHEMATIC_UPLOAD_FILENAME_EXTENSION", file.filename)
  elif file_size > app.config["SCHEMATIC_UPLOAD_MAX_FILE_SIZE"]:
    flash_by_key(app, "SCHEMATIC_UPLOAD_FILE_TOO_LARGE", file.filename)
    log_warn("SCHEMATIC_UPLOAD_FILE_TOO_LARGE", file.filename)
  elif file_exists_in_dir(uploads_dir, file_root + ".schematic") or file_exists_in_dir(uploads_dir, file_root + ".schem"):
    flash_by_key(app, "SCHEMATIC_UPLOAD_FILE_EXISTS", file.filename)
    log_warn("SCHEMATIC_UPLOAD_FILE_EXISTS", file.filename)
  else:
    try:
      schematics.save(file)

      message = flash_by_key(app, "SCHEMATIC_UPLOAD_SUCCESS", file.filename)
      log_info("SCHEMATIC_UPLOAD_SUCCESS", file.filename)
    except Exception as e:
      message = flash_by_key(app, "SCHEMATIC_UPLOAD_FAILURE", file.filename)
      log_error("SCHEMATIC_UPLOAD_FAILURE", file.filename, e)

@app.route("/schematic/download", methods = ["GET", "POST"])
def route_schematic_download():
  response = False

  if request.method == "POST":
    response = create_schematic_download_link()

  if response:
    return response
  else:
    return render_template("schematic/download/index.html", home = False)

def create_schematic_download_link():
  file_root = request.form["fileRoot"]
  file_extension = request.form["fileExtension"]
  file_name = "{}.{}".format(file_root, file_extension)
  downloads_dir = app.config["SCHEMATIC_DOWNLOADS_DIR"]

  if file_root == "":
    flash_by_key(app, "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_EMPTY")
    log_warn("SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_EMPTY")
    return

  if file_extension not in ["schem", "schematic"]:
    flash_by_key(app, "SCHEMATIC_DOWNLOAD_LINK_CREATION_INVALID_EXTENSION", file_name)
    log_warn("SCHEMATIC_DOWNLOAD_LINK_CREATION_INVALID_EXTENSION", file_name)
    return

  if str_contains_whitespace(file_root):
    flash_by_key(app, "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_WHITESPACE", file_name)
    log_warn("SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_WHITESPACE", file_name)
    return

  secure_file_name = "{}.{}".format(secure_filename(file_root), file_extension)

  if file_exists_in_dir(downloads_dir, secure_file_name):
    flash_by_key(app, "SCHEMATIC_DOWNLOAD_LINK_CREATION_SUCCESS", secure_file_name)
    log_info("SCHEMATIC_DOWNLOAD_LINK_CREATION_SUCCESS", secure_file_name)
    return
  else:
    flash_by_key(app, "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND", secure_file_name)
    log_warn("SCHEMATIC_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND", secure_file_name)
    return

@app.route("/schematic/download/<path:filename>")
def download_schematic(filename):
  log_info("SCHEMATIC_DOWNLOAD_SUCCESS", filename)
  return send_from_directory(app.config["SCHEMATIC_DOWNLOADS_DIR"], filename, as_attachment = True)
