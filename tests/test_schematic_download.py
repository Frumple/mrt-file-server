from test_schematic_base import TestSchematicBase
from unittest.mock import patch

from werkzeug.datastructures import OrderedMultiDict

import os
import pytest

class TestSchematicDownload(TestSchematicBase):
  def setup(self):
    TestSchematicBase.setup(self)
    self.downloads_dir = self.app.config["SCHEMATIC_DOWNLOADS_DIR"]
    self.clean_schematic_downloads_dir()

  def teardown(self):
    TestSchematicBase.teardown(self)
    self.clean_schematic_downloads_dir()

  # Tests

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("filename", [
    ("mrt_v5_final_elevated_centre_station.schem"),
    ("mrt_v5_final_elevated_centre_station.schematic")
  ])
  def test_create_download_link_should_be_successful(self, mock_logger, filename):
    message_key = "SCHEMATIC_DOWNLOAD_LINK_CREATION_SUCCESS"

    self.copy_test_data_file(filename, self.downloads_dir)

    data = self.create_request_data(filename)
    response = self.create_download_link(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_flash_message_by_key(message_key, response.data, filename)
    mock_logger.info.assert_called_with(self.get_log_message(message_key), filename)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("filename, message_key", [
    ("",                                               "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_EMPTY"),
    ("this file has spaces.schematic",                 "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILENAME_WHITESPACE"),
    ("mrt_v5_final_elevated_centre_station.schematic", "SCHEMATIC_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND"),
    ("mrt_v5_final_elevated_centre_station.txt",       "SCHEMATIC_DOWNLOAD_LINK_CREATION_INVALID_EXTENSION")
  ])
  def test_create_download_link_should_fail(self, mock_logger, filename, message_key):
    data = self.create_request_data(filename)
    response = self.create_download_link(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    if filename:
      self.verify_flash_message_by_key(message_key, response.data, filename)
      mock_logger.warn.assert_called_with(self.get_log_message(message_key), filename)
    else:
      self.verify_flash_message_by_key(message_key, response.data)
      mock_logger.warn.assert_called_with(self.get_log_message(message_key))

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("filename", [
    ("mrt_v5_final_elevated_centre_station.schem"),
    ("mrt_v5_final_elevated_centre_station.schematic")
  ])
  def test_download_should_be_successful(self, mock_logger, filename):
    original_file_content = self.load_test_data_file(filename)

    self.copy_test_data_file(filename, self.downloads_dir)

    response = self.start_download(filename)

    assert response.status_code == 200
    assert response.mimetype == "application/octet-stream"

    assert response.headers.get("Content-Disposition") == "attachment; filename={}".format(filename)
    assert int(response.headers.get("Content-Length")) == len(original_file_content)

    mock_logger.info.assert_called_with(self.get_log_message("SCHEMATIC_DOWNLOAD_SUCCESS"), filename)

  # Helper Functions

  def clean_schematic_downloads_dir(self):
    self.remove_files(self.downloads_dir, "schematic")
    self.remove_files(self.downloads_dir, "schem")

  def create_download_link(self, data):
    return self.client.post("/schematic/download", data = data)

  def start_download(self, filename):
    return self.client.get("/schematic/download/{}".format(filename))

  def create_request_data(self, filename):
    pair = os.path.splitext(filename)

    data = OrderedMultiDict()
    data.add("fileRoot", pair[0])
    data.add("fileExtension", pair[1][1:])

    return data