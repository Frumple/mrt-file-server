from flask import Flask
from flask_uploads import UploadSet, configure_uploads

import os
import re

def configure_instance_folders(app):
  instance_path = app.instance_path

  app.config['DOWNLOADS_DIR'] = downloads_dir = os.path.join(instance_path, "downloads")
  app.config['WORLD_DOWNLOADS_DIR'] = os.path.join(downloads_dir, "worlds")
  app.config['SCHEMATIC_DOWNLOADS_DIR'] = os.path.join(downloads_dir, "schematics")

  app.config['UPLOADS_DIR'] = uploads_dir = os.path.join(instance_path, "uploads")
  app.config['SCHEMATIC_UPLOADS_DIR'] = schematic_uploads_dir = os.path.join(uploads_dir, "schematics")

  # Used by Flask-Uploads to determine where to upload schematics
  app.config['UPLOADED_SCHEMATICS_DEST'] = schematic_uploads_dir

def configure_flash_messages(app):
  messages = {
    "UPLOAD_SUCCESS":             "Upload Successful!",
    "UPLOAD_FAILURE":             "Upload Failed! Please contact the admins for assistance.",
    "UPLOAD_USERNAME_EMPTY":      "Upload Failed! Username must not be empty.",
    "UPLOAD_USERNAME_WHITESPACE": "Upload Failed! Username must not contain spaces.",
    "UPLOAD_NO_FILES":            "Upload Failed! No files selected.",
    "UPLOAD_TOO_MANY_FILES":      "Upload Failed! A maximum of {} files can be uploaded at one time.".format( \
                                  app.config['MAX_NUMBER_OF_UPLOAD_FILES']),
    "UPLOAD_FILE_TOO_LARGE":      "Upload Failed! File size is larger than allowed maximum of {} bytes.".format( \
                                  app.config['MAX_UPLOAD_FILE_SIZE']),
    "UPLOAD_FILE_EXISTS":         "Upload Failed! File with same name already exists on the server.",
    "UPLOAD_FILENAME_WHITESPACE": "Upload Failed! File name must not contain spaces.",
    "UPLOAD_FILENAME_EXTENSION":  "Upload Failed! File must end with the .schematic extension."
  }

  app.config['FLASH_MESSAGES'] = messages

app = Flask(__name__)
app.config.from_pyfile("config.py")

configure_instance_folders(app)
configure_flash_messages(app)

schematics = UploadSet('schematics', extensions = ['schematic'])
configure_uploads(app, schematics)

import mrt_file_server.views

if __name__ == "__main__":
  app.run()