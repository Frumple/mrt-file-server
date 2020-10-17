# Maximum number of schematic files that can be uploaded at one time
SCHEMATIC_UPLOAD_MAX_NUMBER_OF_FILES = 10

# Maximum number of bytes that can be uploaded per schematic file
SCHEMATIC_UPLOAD_MAX_FILE_SIZE = 100 * 1024 # 100 kilobytes

# Maximum number of map files that can be uploaded at one time
MAP_UPLOAD_MAX_NUMBER_OF_FILES = 10

# Maximum number of bytes that can be uploaded per map file
MAP_UPLOAD_MAX_FILE_SIZE = 100 * 1024 # 100 kilobytes

# Maximum number of bytes that can be uploaded at one time
MAX_CONTENT_LENGTH = 10 * 100 * 1024 # 1 megabyte

# Number of last map IDs that are allowed to be uploaded
# Example:
# If last map ID in idcounts.dat is 2500, and MAP_UPLOAD_LAST_ALLOWED_ID_RANGE is 1000,
# then the range of allowed map IDs is 1501 to 2500.
MAP_UPLOAD_LAST_ALLOWED_ID_RANGE = 1000

# Disable basic authentication by default
BASIC_AUTH_FORCE = False