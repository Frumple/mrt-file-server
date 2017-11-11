# Maximum number of files that can be uploaded at one time
MAX_NUMBER_OF_UPLOAD_FILES = 10

# Maximum number of bytes that can be uploaded per file
MAX_UPLOAD_FILE_SIZE = 100 * 1024 # 100 kilobytes

# Maximum number of bytes that can be uploaded at one time
MAX_CONTENT_LENGTH = MAX_NUMBER_OF_UPLOAD_FILES * MAX_UPLOAD_FILE_SIZE

# Required by Flask to enable sessions and flash messages
SECRET_KEY = "\x97/\xb6\xecsc\x91\xd3r\xab\xcf\xc0\xd1aez\xc0>\xe2\xf0\xee\xe1\xd5F"

# Enable or disable high-performance file transfer
# On a Flask development server, this should be set to False as it does not support X_SENDFILE
# On a test or production server, this should be set to True to ensure the best file transfer speeds
USE_X_SENDFILE = False