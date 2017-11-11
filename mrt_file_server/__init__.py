from flask import Flask
from flask_uploads import UploadSet, configure_uploads

import modes
import os
import re

def load_environment_config(app, mode):
  instance_path = app.instance_path
  config_file_path = os.path.join(instance_path, mode, "config.py")

  if os.path.isfile(config_file_path):
    app.config.from_pyfile(config_file_path)

def configure_instance_folders(app, mode):
  instance_path = app.instance_path
  mode_dir = os.path.join(instance_path, mode)

  app.config['DOWNLOADS_DIR'] = downloads_dir = os.path.join(mode_dir, "downloads")
  app.config['WORLD_DOWNLOADS_DIR'] = world_downloads_dir = os.path.join(downloads_dir, "worlds")
  app.config['SCHEMATIC_DOWNLOADS_DIR'] = schematics_downloads_dir = os.path.join(downloads_dir, "schematics")

  app.config['UPLOADS_DIR'] = uploads_dir = os.path.join(mode_dir, "uploads")
  app.config['SCHEMATIC_UPLOADS_DIR'] = schematic_uploads_dir = os.path.join(uploads_dir, "schematics")

  # Used by Flask-Uploads to determine where to upload schematics
  app.config['UPLOADED_SCHEMATICS_DEST'] = schematic_uploads_dir

  os.makedirs(world_downloads_dir, exist_ok = True)
  os.makedirs(schematics_downloads_dir, exist_ok = True)
  os.makedirs(schematic_uploads_dir, exist_ok = True)

def configure_flash_messages(app):
  messages = {
    "UPLOAD_SUCCESS":               "Upload Successful!",
    "UPLOAD_FAILURE":               "Upload Failed! Please contact the admins for assistance.",
    "UPLOAD_USERNAME_EMPTY":        "Upload Failed! Username must not be empty.",
    "UPLOAD_USERNAME_WHITESPACE":   "Upload Failed! Username must not contain spaces.",
    "UPLOAD_NO_FILES":              "Upload Failed! No files selected.",
    "UPLOAD_TOO_MANY_FILES":        "Upload Failed! A maximum of {} files can be uploaded at one time.".format( \
                                    app.config['MAX_NUMBER_OF_UPLOAD_FILES']),
    "UPLOAD_FILE_TOO_LARGE":        "Upload Failed! File size is larger than allowed maximum of {} bytes.".format( \
                                    app.config['MAX_UPLOAD_FILE_SIZE']),
    "UPLOAD_FILE_EXISTS":           "Upload Failed! File with same name already exists on the server.",
    "UPLOAD_FILENAME_WHITESPACE":   "Upload Failed! File name must not contain spaces.",
    "UPLOAD_FILENAME_EXTENSION":    "Upload Failed! File must end with the .schematic extension.",
    "DOWNLOAD_FILENAME_EMPTY":      "Download Failed! Filename must not be empty.",
    "DOWNLOAD_FILENAME_WHITESPACE": "Download Failed! Filename must not contain spaces.",
    "DOWNLOAD_FILE_NOT_FOUND":      "Download Failed! File does not exist."
  }

  app.config['FLASH_MESSAGES'] = messages

mode = os.environ.get(modes.ENVIRONMENT_VARIABLE, modes.DEVELOPMENT)

app = Flask(__name__, instance_relative_config = True)
app.config.from_object('mrt_file_server.default_config')

load_environment_config(app, mode)
configure_instance_folders(app, mode)
configure_flash_messages(app)

schematics = UploadSet('schematics', extensions = ['schematic'])
configure_uploads(app, schematics)

import mrt_file_server.views

if __name__ == "__main__":
  app.run()