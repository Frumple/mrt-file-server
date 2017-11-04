from collections import OrderedDict

import glob
import mrt_file_server
import os
import unittest

class TestBase(unittest.TestCase):
  def setUp(self):
    self.TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

    self.app = mrt_file_server.app
    self.app.testing = True    
    self.client = self.app.test_client()

    self.app.config['USE_X_SENDFILE'] = True

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

  def flash_message_html(self, message):
    return '<li name="flash_message">{}</li>'.format(message)

  def get_flash_message(self, key):
    return self.app.config['FLASH_MESSAGES'][key]

  def verify_flash_message_by_key(self, key, response_data, filename = None):
    self.verify_flash_message(self.get_flash_message(key), response_data, filename)  

  def verify_flash_message(self, expected_message, response_data, filename = None):
    if filename:
      expected_message_html = self.flash_message_html("{}: {}".format(filename, expected_message))      
    else:
      expected_message_html = self.flash_message_html(expected_message)
    self.assertIn(bytes(expected_message_html, encoding = "utf-8"), response_data)

  def read_data_file(self, filepath):
    with open(filepath, "r+b") as file:
      return file.read()

  def remove_files(self, dir, extension):
    path = "{}/*.{}".format(dir, extension)
    for file in glob.glob(path):
      os.remove(file)