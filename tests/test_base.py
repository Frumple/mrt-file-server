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

  def flash_message_html(self, message):
    return '<li name="flash_message">{}</li>'.format(message)

  def verify_flash_message(self, filename, expected_message, response_data):
    expected_message_html = self.flash_message_html("{}: {}".format(filename, expected_message))
    self.assertIn(bytes(expected_message_html, encoding = "utf-8"), response_data)

  def read_data_file(self, filepath):
    with open(filepath, "r+b") as file:
      return file.read()

  def remove_files(self, dir, extension):
    path = "{}/*.{}".format(dir, extension)
    for file in glob.glob(path):
      os.remove(file)

  def print_response(self, response):
    print(response.status_code)
    print(response.mimetype)
    print(response.headers)
    print(response.data)