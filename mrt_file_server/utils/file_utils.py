import os

def get_filesize(file):
  file.seek(0, os.SEEK_END)
  filesize = file.tell()
  file.seek(0)
  return filesize

def split_file_root_and_extension(filename):
  return os.path.splitext(filename)

def file_exists_in_dir(dir, filename):
  filepath = os.path.join(dir, filename)
  return os.path.isfile(filepath)