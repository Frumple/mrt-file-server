from flask import Flask
from flask_uploads import UploadSet, configure_uploads

import logging
import modes
import os
import re

def configure_logger(app, mode):
  logger = logging.getLogger(__name__)

  if mode is modes.PRODUCTION:
    logger.setLevel(logging.INFO)
  else:
    logger.setLevel(logging.DEBUG)

  formatter = logging.Formatter(
    fmt = '{asctime} {name:12} {levelname:8} {message}',
    datefmt = '%y-%m-%d %H:%M',
    style = '{')

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
    "SCHEMATIC_UPLOAD_SUCCESS":               "Schematic upload successful: '%s'",
    "SCHEMATIC_UPLOAD_FAILURE":               "Schematic upload failed: '%s', Exception: '%s'",
    "SCHEMATIC_UPLOAD_USERNAME_EMPTY":        "Schematic upload failed. Username is empty.",
    "SCHEMATIC_UPLOAD_USERNAME_WHITESPACE":   "Schematic upload failed. Username contains whitespace: '%s'",
    "SCHEMATIC_UPLOAD_NO_FILES":              "Schematic upload failed. No files specified.",
    "SCHEMATIC_UPLOAD_TOO_MANY_FILES":        "Schematic upload failed. Too many files.",
    "SCHEMATIC_UPLOAD_FILE_TOO_LARGE":        "Schematic upload failed. File too large: '%s'",
    "SCHEMATIC_UPLOAD_FILE_EXISTS":           "Schematic upload failed. File already exists: '%s'",
    "SCHEMATIC_UPLOAD_FILENAME_WHITESPACE":   "Schematic upload failed. Filename contains whitespace: '%s'",
    "SCHEMATIC_UPLOAD_FILENAME_EXTENSION":    "Schematic upload failed. Filename has invalid extension: '%s'",
    "SCHEMATIC_DOWNLOAD_SUCCESS":             "Schematic download initiated: '%s'",
    "SCHEMATIC_DOWNLOAD_FILENAME_EMPTY":      "Schematic download failed. Filename is empty.",
    "SCHEMATIC_DOWNLOAD_FILENAME_WHITESPACE": "Schematic download failed. Filename contains whitespace: '%s'",
    "SCHEMATIC_DOWNLOAD_FILE_NOT_FOUND":      "Schematic download failed. File does not exist: '%s'",
    "WORLD_DOWNLOAD_SUCCESS":                 "World download initiated: '%s'",
  }

  app.config['LOG_MESSAGES'] = messages
  logger.info("Log messages configured.")

def configure_flash_messages(app):
  messages = {
    "SCHEMATIC_UPLOAD_SUCCESS":               "Upload Successful!",
    "SCHEMATIC_UPLOAD_FAILURE":               "Upload Failed! Please contact the admins for assistance.",
    "SCHEMATIC_UPLOAD_USERNAME_EMPTY":        "Upload Failed! Username must not be empty.",
    "SCHEMATIC_UPLOAD_USERNAME_WHITESPACE":   "Upload Failed! Username must not contain spaces.",
    "SCHEMATIC_UPLOAD_NO_FILES":              "Upload Failed! No files selected.",
    "SCHEMATIC_UPLOAD_TOO_MANY_FILES":        "Upload Failed! A maximum of {} files can be uploaded at one time.".format( \
                                               app.config['MAX_NUMBER_OF_UPLOAD_FILES']),
    "SCHEMATIC_UPLOAD_FILE_TOO_LARGE":        "Upload Failed! File size is larger than allowed maximum of {} bytes.".format( \
                                               app.config['MAX_UPLOAD_FILE_SIZE']),
    "SCHEMATIC_UPLOAD_FILE_EXISTS":           "Upload Failed! File with same name already exists on the server.",
    "SCHEMATIC_UPLOAD_FILENAME_WHITESPACE":   "Upload Failed! File name must not contain spaces.",
    "SCHEMATIC_UPLOAD_FILENAME_EXTENSION":    "Upload Failed! File must end with the .schematic extension.",
    "SCHEMATIC_DOWNLOAD_FILENAME_EMPTY":      "Download Failed! Filename must not be empty.",
    "SCHEMATIC_DOWNLOAD_FILENAME_WHITESPACE": "Download Failed! Filename must not contain spaces.",
    "SCHEMATIC_DOWNLOAD_FILE_NOT_FOUND":      "Download Failed! File does not exist."
  }

  app.config['FLASH_MESSAGES'] = messages
  logger.info("Flash messages configured.")

def load_environment_config(app, mode):
  instance_path = app.instance_path
  config_file_path = os.path.join(instance_path, mode, "config.py")

  if os.path.isfile(config_file_path):
    app.config.from_pyfile(config_file_path)
    logger.info("Environment config loaded from: '%s'", config_file_path)
  else:
    logger.info("Environment config not found.")

def configure_instance_folders(app, mode):
  instance_path = app.instance_path
  mode_dir = os.path.join(instance_path, mode)

  downloads_dir = os.path.join(mode_dir, "downloads")
  world_downloads_dir = os.path.join(downloads_dir, "worlds")
  schematic_downloads_dir = os.path.join(downloads_dir, "schematics")

  uploads_dir = os.path.join(mode_dir, "uploads")
  schematic_uploads_dir = os.path.join(uploads_dir, "schematics")

  os.makedirs(world_downloads_dir, exist_ok = True)
  os.makedirs(schematic_downloads_dir, exist_ok = True)
  os.makedirs(schematic_uploads_dir, exist_ok = True)

  set_config_variable('DOWNLOADS_DIR', downloads_dir)
  set_config_variable('WORLD_DOWNLOADS_DIR', world_downloads_dir)
  set_config_variable('SCHEMATIC_DOWNLOADS_DIR', schematic_downloads_dir)
  set_config_variable('UPLOADS_DIR', uploads_dir)
  set_config_variable('SCHEMATIC_UPLOADS_DIR', schematic_uploads_dir)

  # Used by Flask-Uploads to determine where to upload schematics
  set_config_variable('UPLOADED_SCHEMATICS_DEST', schematic_uploads_dir)

def set_config_variable(name, value):
  app.config[name] = value
  logger.info("Config variable '%s' set to: '%s'", name, value)

def configure_schematic_uploads(app):
  schematics = UploadSet('schematics', extensions = ['schematic'])
  configure_uploads(app, schematics)
  logger.info("Schematic uploads configured.")
  return schematics

app = Flask(__name__, instance_relative_config = True)
app.config.from_object('mrt_file_server.default_config')

mode = os.environ.get(modes.ENVIRONMENT_VARIABLE, modes.DEVELOPMENT)

logger = configure_logger(app, mode)
configure_log_messages(app)
configure_flash_messages(app)
load_environment_config(app, mode)
configure_instance_folders(app, mode)
schematics = configure_schematic_uploads(app)

import mrt_file_server.views

if __name__ == "__main__":
  app.run()

logger.info("Application ready.")