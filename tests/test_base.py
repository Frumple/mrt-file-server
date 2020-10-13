from collections import OrderedDict
from shutil import copyfile

import glob
import modes
import os

class TestBase:
  def setup(self):
    os.environ[modes.ENVIRONMENT_VARIABLE] = modes.TEST

    self.TEST_DATA_ROOT = os.path.dirname(os.path.realpath(__file__))

    import mrt_file_server
    self.app = mrt_file_server.app
    self.app.testing = True
    self.client = self.app.test_client()

  def teardown(self):
    pass

  def load_test_data_file(self, filename):
    filepath = os.path.join(self.TEST_DATA_DIR, filename)
    return self.read_file(filepath)

  def load_test_data_files(self, filenames):
    files = OrderedDict()
    for filename in filenames:
      file_content = self.load_test_data_file(filename)
      files[filename] = file_content
    return files

  def copy_test_data_file(self, src_filename, dest_dir, dest_filename = None):
    dest_filename = src_filename if dest_filename is None else dest_filename

    src_filepath = os.path.join(self.TEST_DATA_DIR, src_filename)
    dest_filepath = os.path.join(dest_dir, dest_filename)
    copyfile(src_filepath, dest_filepath)

  def read_file(self, filepath):
    with open(filepath, "r+b") as file:
      return file.read()

  def remove_files(self, dir, extension):
    path = "{}/*.{}".format(dir, extension)
    for file in glob.glob(path):
      os.remove(file)

  def verify_file_content(self, directory, filename, expected_file_content):
    filepath = os.path.join(directory, filename)
    actual_file_content = self.read_file(filepath)
    assert actual_file_content == expected_file_content

  def get_log_message(self, key):
    return self.app.config["LOG_MESSAGES"][key]

  def get_flash_message(self, key):
    return self.app.config["FLASH_MESSAGES"][key]

  def verify_flash_message_by_key(self, key, response_data, filename = None):
    flash_message = self.get_flash_message(key)
    self.verify_flash_message(flash_message.message, flash_message.category, response_data, filename)

  def verify_flash_message(self, expected_message, expected_category, response_data, filename = None):
    if filename:
      expected_message_html = self.flash_message_html("{}: {}".format(filename, expected_message.format(filename)), expected_category)
    else:
      expected_message_html = self.flash_message_html(expected_message, expected_category)
    assert bytes(expected_message_html, encoding = "utf-8") in response_data

  def flash_message_html(self, message, category):
    return "<li class=\"flash-{}\" name=\"flash_message\">{}</li>".format(category, message)
