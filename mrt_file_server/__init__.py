from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads
from flask_basicauth import BasicAuth

from mrt_file_server.request_log_adapter import RequestLogAdapter

import logging
import modes
import os
import re

class FlashMessage:
  def __init__(self, message, category):
    self.message = message
    self.category = category

def configure_logger(app, mode):
  logger = logging.getLogger(__name__)

  if mode is modes.PRODUCTION:
    logger.setLevel(logging.INFO)
  else:
    logger.setLevel(logging.DEBUG)

  formatter = logging.Formatter(
    fmt = "{asctime} {name:12} {levelname:8} {message}",
    datefmt = "%y-%m-%d %H:%M",
    style = "{")

  log_file_path = prepare_log_file(app, mode)
  file_handler = logging.FileHandler(log_file_path)
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  if mode is not modes.TEST:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

  logger.info("Logging configured.")
  logger.info("Application mode is set to: '%s'", mode)

  return logger

def prepare_log_file(app, mode):
  instance_path = app.instance_path
  logs_dir = os.path.join(instance_path, mode, "logs")
  log_file_path = os.path.join(logs_dir, "server.log")
  os.makedirs(logs_dir, exist_ok = True)

  return log_file_path

def configure_log_messages(app):
  messages = {
    "SCHEMATIC_UPLOAD_SUCCESS":                             "Schematic upload successful: '%s' (Username: '%s')",
    "SCHEMATIC_UPLOAD_FAILURE":                             "Schematic upload failed: '%s' (Username: '%s', Exception: '%s')",
    "SCHEMATIC_UPLOAD_USERNAME_EMPTY":                      "Schematic upload failed. Username is empty.",
    "SCHEMATIC_UPLOAD_USERNAME_WHITESPACE":                 "Schematic upload failed. Username contains whitespace: '%s'",
    "SCHEMATIC_UPLOAD_NO_FILES":                            "Schematic upload failed. No files specified. (Username: '%s')",
    "SCHEMATIC_UPLOAD_TOO_MANY_FILES":                      "Schematic upload failed. Too many files. (Username: '%s')",
    "SCHEMATIC_UPLOAD_FILE_TOO_LARGE":                      "Schematic upload failed. File too large: '%s' (Username: '%s')",
    "SCHEMATIC_UPLOAD_FILE_EXISTS":                         "Schematic upload failed. File already exists: '%s' (Username: '%s')",
    "SCHEMATIC_UPLOAD_FILENAME_WHITESPACE":                 "Schematic upload failed. Filename contains whitespace: '%s' (Username: '%s')",
    "SCHEMATIC_UPLOAD_FILENAME_EXTENSION":                  "Schematic upload failed. Filename has invalid extension: '%s' (Username: '%s')",

    "SCHEMATIC_DOWNLOAD_SUCCESS":                           "Schematic download initiated: '%s'",
    "SCHEMATIC_DOWNLOAD_LINK_CREATION_SUCCESS":             "Schematic download link created: '%s'",
    "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_EMPTY":      "Schematic download link creation failed. Filename is empty.",
    "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_WHITESPACE": "Schematic download link creation failed. Filename contains whitespace: '%s'",
    "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND":      "Schematic download link creation failed. File does not exist: '%s'",
    "SCHEMATIC_DOWNLOAD_LINK_CREATION_INVALID_EXTENSION":   "Schematic download link creation failed. Invalid file extension: '%s'",

    "MAP_UPLOAD_SUCCESS":                                   "Map upload successful: '%s' (Username: '%s')",
    "MAP_UPLOAD_FAILURE":                                   "Map upload failed: '%s' (Username: '%s', Exception: '%s')",
    "MAP_UPLOAD_USERNAME_EMPTY":                            "Map upload failed. Username is empty.",
    "MAP_UPLOAD_USERNAME_WHITESPACE":                       "Map upload failed. Username contains whitespace: '%s'",
    "MAP_UPLOAD_NO_FILES":                                  "Map upload failed. No files specified. (Username: '%s')",
    "MAP_UPLOAD_TOO_MANY_FILES":                            "Map upload failed. Too many files. (Username: '%s')",
    "MAP_UPLOAD_FILE_TOO_LARGE":                            "Map upload failed. File too large: '%s' (Username: '%s')",
    "MAP_UPLOAD_FILENAME_INVALID":                          "Map upload failed. File name is not of the format 'map_#####.dat': '%s' (Username: '%s')",
    "MAP_UPLOAD_MAP_ID_OUT_OF_RANGE":                       "Map upload failed. Map ID is out of range: '%s' (Username: '%s')",
    "MAP_UPLOAD_MAP_FORMAT_INVALID":                        "Map upload failed. File is not a valid map format: '%s' (Username: '%s')",
    "MAP_UPLOAD_MAP_LOCKED":                                "Map upload failed. Existing map file is locked. Contact an admin for assistance: '%s' (Username: '%s')",

    "MAP_DOWNLOAD_SUCCESS":                                 "Map download initiated: '%s'",
    "MAP_DOWNLOAD_LINK_CREATION_SUCCESS":                   "Map download link created: '%s'",
    "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_EMPTY":              "Map download link creation failed. Map ID is empty.",
    "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_INVALID":            "Map download link creation failed. Map ID is invalid: '%s'",
    "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_OUT_OF_RANGE":       "Map download link creation failed. Map ID is out of range: '%s'",
    "MAP_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND":            "Map download link creation failed. File does not exist: '%s'",

    "WORLD_DOWNLOAD_SUCCESS":                               "World download initiated: '%s'",
  }

  app.config["LOG_MESSAGES"] = messages
  logger.info("Log messages configured.")

def configure_flash_messages(app):
  messages = {
    "SCHEMATIC_UPLOAD_SUCCESS":                             FlashMessage("Upload Successful!", "success"),
    "SCHEMATIC_UPLOAD_FAILURE":                             FlashMessage("Upload Failed! Please contact the admins for assistance.", "failure"),
    "SCHEMATIC_UPLOAD_USERNAME_EMPTY":                      FlashMessage("Upload Failed! Username must not be empty.", "failure"),
    "SCHEMATIC_UPLOAD_USERNAME_WHITESPACE":                 FlashMessage("Upload Failed! Username must not contain spaces.", "failure"),
    "SCHEMATIC_UPLOAD_NO_FILES":                            FlashMessage("Upload Failed! No files selected.", "failure"),
    "SCHEMATIC_UPLOAD_TOO_MANY_FILES":                      FlashMessage("Upload Failed! A maximum of {} files can be uploaded at one time.".format( \
                                                              app.config["SCHEMATIC_UPLOAD_MAX_NUMBER_OF_FILES"]), "failure"),
    "SCHEMATIC_UPLOAD_FILE_TOO_LARGE":                      FlashMessage("Upload Failed! File size is larger than the allowed maximum of {} kilobytes.".format( \
                                                              int(app.config["SCHEMATIC_UPLOAD_MAX_FILE_SIZE"] / 1024)), "failure"),
    "SCHEMATIC_UPLOAD_FILE_EXISTS":                         FlashMessage("Upload Failed! File with same name already exists on the server.", "failure"),
    "SCHEMATIC_UPLOAD_FILENAME_WHITESPACE":                 FlashMessage("Upload Failed! File name must not contain spaces.", "failure"),
    "SCHEMATIC_UPLOAD_FILENAME_EXTENSION":                  FlashMessage("Upload Failed! File must end with the .schematic or .schem extension.", "failure"),

    "SCHEMATIC_DOWNLOAD_LINK_CREATION_SUCCESS":             FlashMessage("Download Link Creation Successful! <a href=\"download/{}\">Click here to begin download.</a>", "success"),
    "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_EMPTY":      FlashMessage("Download Link Creation Failed! Filename must not be empty.", "failure"),
    "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_WHITESPACE": FlashMessage("Download Link Creation Failed! Filename must not contain spaces.", "failure"),
    "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND":      FlashMessage("Download Link Creation Failed! File does not exist.", "failure"),
    "SCHEMATIC_DOWNLOAD_LINK_CREATION_INVALID_EXTENSION":   FlashMessage("Download Link Creation Failed! Invalid file extension.", "failure"),

    "MAP_UPLOAD_SUCCESS":                                   FlashMessage("Upload Successful!", "success"),
    "MAP_UPLOAD_FAILURE":                                   FlashMessage("Upload Failed! Please contact the admins for assistance.", "failure"),
    "MAP_UPLOAD_USERNAME_EMPTY":                            FlashMessage("Upload Failed! Username must not be empty.", "failure"),
    "MAP_UPLOAD_USERNAME_WHITESPACE":                       FlashMessage("Upload Failed! Username must not contain spaces.", "failure"),
    "MAP_UPLOAD_NO_FILES":                                  FlashMessage("Upload Failed! No files selected.", "failure"),
    "MAP_UPLOAD_TOO_MANY_FILES":                            FlashMessage("Upload Failed! A maximum of {} files can be uploaded at one time.".format( \
                                                              app.config["MAP_UPLOAD_MAX_NUMBER_OF_FILES"]), "failure"),
    "MAP_UPLOAD_FILE_TOO_LARGE":                            FlashMessage("Upload Failed! File size is larger than the allowed maximum of {} kilobytes.".format( \
                                                              int(app.config["MAP_UPLOAD_MAX_FILE_SIZE"] / 1024)), "failure"),
    "MAP_UPLOAD_FILENAME_INVALID":                          FlashMessage("Upload Failed! File name is not of the format 'map_#####.dat'.", "failure"),
    "MAP_UPLOAD_MAP_ID_OUT_OF_RANGE":                       FlashMessage("Upload Failed! Map ID is out of range.", "failure"),

    "MAP_UPLOAD_MAP_FORMAT_INVALID":                        FlashMessage("Upload Failed! File is not a valid map format.", "failure"),
    "MAP_UPLOAD_MAP_LOCKED":                                FlashMessage("Upload Failed! Existing map file is locked. Contact an admin for assistance.", "failure"),

    "MAP_DOWNLOAD_LINK_CREATION_SUCCESS":                   FlashMessage("Download Link Creation Successful! <a href=\"download/{}\">Click here to begin download.</a>", "success"),
    "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_EMPTY":              FlashMessage("Download Link Creation Failed! Map ID is empty.", "failure"),
    "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_INVALID":            FlashMessage("Download Link Creation Failed! Map ID is invalid.", "failure"),
    "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_OUT_OF_RANGE":       FlashMessage("Download Link Creation Failed! Map ID is out of range.", "failure"),
    "MAP_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND":            FlashMessage("Download Link Creation Failed! File does not exist.", "failure")
  }

  app.config['FLASH_MESSAGES'] = messages
  logger.info("Flash messages configured.")

def load_environment_config(app, mode):
  Instance_relative_config_file_path = os.path.join(mode, "config.py")
  app.config.from_pyfile(Instance_relative_config_file_path)
  logger.info("Environment config loaded from: '%s'", Instance_relative_config_file_path)

def configure_instance_folders(app, mode):
  instance_path = os.path.realpath(app.instance_path)
  mode_dir = os.path.join(instance_path, mode)

  downloads_dir = os.path.join(mode_dir, "downloads")
  world_downloads_dir = os.path.join(downloads_dir, "worlds")
  schematic_downloads_dir = os.path.join(downloads_dir, "schematics")
  map_downloads_dir = os.path.join(downloads_dir, "maps")

  uploads_dir = os.path.join(mode_dir, "uploads")
  schematic_uploads_dir = os.path.join(uploads_dir, "schematics")
  map_uploads_dir = os.path.join(uploads_dir, "maps")

  os.makedirs(world_downloads_dir, exist_ok = True)
  os.makedirs(schematic_downloads_dir, exist_ok = True)
  os.makedirs(schematic_uploads_dir, exist_ok = True)

  set_config_variable("DOWNLOADS_DIR", downloads_dir)
  set_config_variable("WORLD_DOWNLOADS_DIR", world_downloads_dir)
  set_config_variable("SCHEMATIC_DOWNLOADS_DIR", schematic_downloads_dir)
  set_config_variable("MAP_DOWNLOADS_DIR", map_downloads_dir)

  set_config_variable("UPLOADS_DIR", uploads_dir)
  set_config_variable("SCHEMATIC_UPLOADS_DIR", schematic_uploads_dir)
  set_config_variable("MAP_UPLOADS_DIR", map_uploads_dir)

  # Used by Flask-Uploads to determine where to upload files
  set_config_variable("UPLOADED_SCHEMATICS_DEST", schematic_uploads_dir)
  set_config_variable("UPLOADED_MAPS_DEST", map_uploads_dir)

def set_config_variable(name, value):
  app.config[name] = value
  logger.info("Config variable '%s' set to: '%s'", name, value)

def configure_schematic_uploads(app):
  schematics = UploadSet("schematics", extensions = ["schematic", "schem"])
  configure_uploads(app, schematics)
  logger.info("Schematic uploads configured.")
  return schematics

def configure_map_uploads(app):
  maps = UploadSet("maps", extensions = ["dat"])
  configure_uploads(app, maps)
  logger.info("Map uploads configured.")
  return maps

app = Flask(__name__, instance_relative_config = True)
app.config.from_object("mrt_file_server.default_config")

mode = os.environ.get(modes.ENVIRONMENT_VARIABLE, modes.DEVELOPMENT)

logger = configure_logger(app, mode)
log_adapter = RequestLogAdapter(logger, request)
configure_log_messages(app)
configure_flash_messages(app)
load_environment_config(app, mode)
configure_instance_folders(app, mode)
schematics = configure_schematic_uploads(app)
maps = configure_map_uploads(app)

basic_auth = BasicAuth(app)

@app.route("/")
def index():
  return render_template("index.html", home = True)

from .blueprints import schematic
from .blueprints import map
from .blueprints import world

app.register_blueprint(schematic.schematic_blueprint)
app.register_blueprint(map.map_blueprint)
app.register_blueprint(world.world_blueprint)

if __name__ == "__main__":
  app.run()

logger.info("Application ready.")