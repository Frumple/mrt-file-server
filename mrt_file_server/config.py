# Directories for various downloads and uploads
DOWNLOADS_DIR = "downloads/"
WORLD_DOWNLOADS_DIR = DOWNLOADS_DIR + "worlds/"
SCHEMATIC_DOWNLOADS_DIR = DOWNLOADS_DIR + "schematics/"

UPLOADS_DIR = "uploads/"
SCHEMATICS_UPLOADS_DIR = UPLOADS_DIR + "schematics/"

# Used by Flask-Uploads to determine where to upload schematics
UPLOADED_SCHEMATICS_DEST = SCHEMATICS_UPLOADS_DIR

# Required by Flask to enable sessions and flash messages
SECRET_KEY = "\x97/\xb6\xecsc\x91\xd3r\xab\xcf\xc0\xd1aez\xc0>\xe2\xf0\xee\xe1\xd5F"

# Enable high-performance file transfer
USE_X_SENDFILE = True
