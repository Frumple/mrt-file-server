from flask import safe_join
from io import BytesIO

import glob
import mrt_file_server
import os
import tempfile
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

  def flash_message(self, message):
    return '<li name="flash_message">{}</li>'.format(message)

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

class TestSchematicUpload(TestBase):
  def setUp(self):
    TestBase.setUp(self)

    self.FLASH_MESSAGE_STATUS_SUCCESS = "Success!"
 
  def tearDown(self):
    TestBase.tearDown(self)
    self.remove_files(self.app.config['SCHEMATIC_UPLOADS_DIR'], "schematic")

  def test_single_file_upload(self):
    filename = "test.schematic"

    original_filepath = os.path.join(self.TEST_DATA_DIR, filename)
    original_file_content = self.read_data_file(original_filepath)

    data = { 
      "userName": "Frumple",
      "schematic": (BytesIO(original_file_content), filename)
    }

    response = self.client.post(
      '/schematic/upload',
      content_type = 'multipart/form-data',
      data = data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype,"text/html")

    # Verify that a successful flash message is shown
    expected_flash_message = self.flash_message("{}: {}".format(filename, self.FLASH_MESSAGE_STATUS_SUCCESS))
    self.assertIn(bytes(expected_flash_message, encoding = "utf-8"), response.data)

    # Verify that the content of the uploaded file matches the original file
    uploaded_filepath = os.path.join(
      self.app.config['SCHEMATIC_UPLOADS_DIR'],
      filename)

    uploaded_file_content = self.read_data_file(uploaded_filepath)
    self.assertEqual(uploaded_file_content, original_file_content)

class TestWorldDownload(TestBase):
  def setUp(self):
    TestBase.setUp(self)

    self.FILE_NAME = "mrt-server-world-test.7z"
    self.FILE_SIZE_IN_BYTES = 1073741824

    self.FILE_PATH = os.path.join(
      self.app.config['WORLD_DOWNLOADS_DIR'],
      self.FILE_NAME)

    # Actual Minecraft world files are too large to use as test data.
    # Instead, we create an empty file and pretend that it is 1GB large.
    with open(self.FILE_PATH, "w+b") as self.file:
      self.file.seek(self.FILE_SIZE_IN_BYTES-1)
      self.file.write(b'\0')
      self.file.flush()

  def tearDown(self):
    TestBase.tearDown(self)
    os.remove(self.file.name)

  def test_world_download(self):
    route_to_file = "/world/download/{}".format(self.FILE_NAME)

    response = self.client.get(route_to_file)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "application/octet-stream")

    self.assertEqual(response.headers.get("Content-Disposition"), "attachment; filename={}".format(self.FILE_NAME))
    self.assertEqual(int(response.headers.get("Content-Length")), self.FILE_SIZE_IN_BYTES)
    self.assertEqual(os.path.normpath(response.headers.get("X-Sendfile")), self.FILE_PATH)

if __name__ == '__main__':
  unittest.main(warnings = 'ignore')