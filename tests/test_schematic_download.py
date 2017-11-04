from test_base import TestBase

from werkzeug import OrderedMultiDict
from shutil import copyfile

import os

class TestSchematicDownload(TestBase):
  def setUp(self):
    TestBase.setUp(self)
    self.downloads_dir = self.app.config['SCHEMATIC_DOWNLOADS_DIR']
    self.clean_schematic_downloads_dir()

  def tearDown(self):
    TestBase.tearDown(self)
    self.clean_schematic_downloads_dir()

  def test_download_schematic_should_be_successful(self):
    filename = "mrt_v5_final_elevated_centre_station.schematic"
    original_file_content = self.load_file(filename)

    # Copy the schematic to the download folder
    src_filepath = os.path.join(self.TEST_DATA_DIR, filename)
    dest_filepath = os.path.join(self.downloads_dir, filename)
    copyfile(src_filepath, dest_filepath)

    data = OrderedMultiDict()
    data.add("fileName", self.filename_without_extension(filename))

    response = self.perform_download(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "application/octet-stream")

    self.assertEqual(response.headers.get("Content-Disposition"), "attachment; filename={}".format(filename))
    self.assertEqual(int(response.headers.get("Content-Length")), len(original_file_content))
    self.assertEqual(os.path.normpath(response.headers.get("X-Sendfile")), dest_filepath)

  def test_download_schematic_with_empty_filename_should_fail(self):
    data = OrderedMultiDict()
    data.add("fileName", "")

    response = self.perform_download(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('DOWNLOAD_FILENAME_EMPTY', response.data)

  def test_download_schematic_with_filename_containing_whitespace_should_fail(self):
    data = OrderedMultiDict()
    data.add("fileName", "this file has spaces")

    response = self.perform_download(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('DOWNLOAD_FILENAME_WHITESPACE', response.data)

  def test_download_schematic_that_does_not_exist_should_fail(self):
    filename = "mrt_v5_final_elevated_centre_station.schematic"

    data = OrderedMultiDict()
    data.add("fileName", self.filename_without_extension(filename))

    response = self.perform_download(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('DOWNLOAD_FILE_NOT_FOUND', response.data, filename)

  # Helper Functions

  def clean_schematic_downloads_dir(self):
    self.remove_files(self.downloads_dir, "schematic")

  def perform_download(self, data):
    return self.client.post('/schematic/download', data = data)

  def filename_without_extension(self, filename):
    return os.path.splitext(filename)[0]