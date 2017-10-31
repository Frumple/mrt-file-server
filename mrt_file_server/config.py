# Maximum number of schematic files that can be uploaded at time
MAX_SCHEMATIC_FILES_TO_UPLOAD = 10

# Required by Flask to enable sessions and flash messages
SECRET_KEY = "\x97/\xb6\xecsc\x91\xd3r\xab\xcf\xc0\xd1aez\xc0>\xe2\xf0\xee\xe1\xd5F"

# Enable or disable high-performance file transfer
# On a Flask development server, this should be set to False as it does not support X_SENDFILE
# On a production server, this should be set to True to ensure the best file transfer speeds
USE_X_SENDFILE = False