from collections import OrderedDict

import glob
import modes
import os
import unittest

class TestBase(unittest.TestCase):
  def setUp(self):
    os.environ[modes.ENVIRONMENT_VARIABLE] = modes.TEST

    self.TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

    import mrt_file_server
    self.app = mrt_file_server.app
    self.app.testing = True
    self.client = self.app.test_client()

  def tearDown(self):
    pass

  def load_file(self, filename):
    filepath = os.path.join(self.TEST_DATA_DIR, filename)
    return self.read_data_file(filepath)

  def load_files(self, filenames):
    files = OrderedDict()
    for filename in filenames:
      file_content = self.load_file(filename)
      files[filename] = file_content

    return files

  def get_log_message(self, key):
    return self.app.config['LOG_MESSAGES'][key]

  def get_flash_message(self, key):
    return self.app.config['FLASH_MESSAGES'][key]

  def verify_flash_message_by_key(self, key, response_data, filename = None):
    flash_message = self.get_flash_message(key)
    self.verify_flash_message(flash_message.message, flash_message.category, response_data, filename)

  def verify_flash_message(self, expected_message, expected_category, response_data, filename = None):
    if filename:
      expected_message_html = self.flash_message_html("{}: {}".format(filename, expected_message), expected_category)
    else:
      expected_message_html = self.flash_message_html(expected_message, expected_category)
    self.assertIn(bytes(expected_message_html, encoding = "utf-8"), response_data)

  def flash_message_html(self, message, category):
    return '<li class="flash-{}" name="flash_message">{}</li>'.format(category, message)

  def read_data_file(self, filepath):
    with open(filepath, "r+b") as file:
      return file.read()

  def remove_files(self, dir, extension):
    path = "{}/*.{}".format(dir, extension)
    for file in glob.glob(path):
      os.remove(file)