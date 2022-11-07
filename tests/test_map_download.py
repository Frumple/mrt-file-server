from test_map_base import TestMapBase
from unittest.mock import patch

from werkzeug.datastructures import OrderedMultiDict

import pytest

class TestMapDownload(TestMapBase):
  def setup(self):
    TestMapBase.setup(self)
    self.downloads_dir = self.app.config["MAP_DOWNLOADS_DIR"]
    self.clean_map_downloads_dir()

  def teardown(self):
    TestMapBase.setup(self)
    self.clean_map_downloads_dir()

  # Tests

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("map_id", [
    ("0"),
    ("289"),
    ("1000"),
    ("1772"),
    ("2000")
  ])
  def test_create_download_link_should_be_successful(self, mock_logger, map_id):
    message_key = "MAP_DOWNLOAD_LINK_CREATION_SUCCESS"
    filename = "map_{}.dat".format(map_id)

    self.copy_test_data_file("map_1500.dat", self.downloads_dir, filename)

    data = self.create_request_data(map_id)
    response = self.create_download_link(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_flash_message_by_key(message_key, response.data, filename)
    mock_logger.info.assert_called_with(self.get_log_message(message_key), filename)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("map_id, message_key", [
    ("",      "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_EMPTY"),
    ("1500a", "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_INVALID"),
    ("asdf",  "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_INVALID"),
    ("-1",    "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_OUT_OF_RANGE"),
    ("2001",  "MAP_DOWNLOAD_LINK_CREATION_MAP_ID_OUT_OF_RANGE"),
    ("1500",  "MAP_DOWNLOAD_LINK_CREATION_FILE_NOT_FOUND")
  ])
  def test_create_download_link_should_fail(self, mock_logger, map_id, message_key):
    data = self.create_request_data(map_id)
    response = self.create_download_link(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    if map_id:
      filename = "map_{}.dat".format(map_id)
      self.verify_flash_message_by_key(message_key, response.data, filename)
      mock_logger.warn.assert_called_with(self.get_log_message(message_key), filename)
    else:
      self.verify_flash_message_by_key(message_key, response.data)
      mock_logger.warn.assert_called_with(self.get_log_message(message_key))

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("filename", [
    ("map_0.dat"),
    ("map_289.dat"),
    ("map_1000.dat"),
    ("map_1772.dat"),
    ("map_2000.dat")
  ])
  def test_download_should_be_successful(self, mock_logger, filename):
    test_data_file_name = "map_1500.dat"
    file_content = self.load_test_data_file(test_data_file_name)

    self.copy_test_data_file(test_data_file_name, self.downloads_dir, filename)

    response = self.start_download(filename)

    assert response.status_code == 200
    assert response.mimetype == "application/octet-stream"

    assert response.headers.get("Content-Disposition") == "attachment; filename={}".format(filename)
    assert int(response.headers.get("Content-Length")) == len(file_content)

    mock_logger.info.assert_called_with(self.get_log_message("MAP_DOWNLOAD_SUCCESS"), filename)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("filename", [
    ("idcounts.dat"),
    ("raids.dat"),
    ("scoreboard.dat"),
    ("villages.dat")
  ])
  def test_download_should_be_forbidden(self, mock_logger, filename):
    self.copy_test_data_file(filename, self.downloads_dir)

    response = self.start_download(filename)

    assert response.status_code == 403
    assert response.mimetype == "text/html"

    assert response.headers.get("Content-Disposition") == None

    mock_logger.warn.assert_called_with(self.get_log_message("MAP_DOWNLOAD_FORBIDDEN"), filename)

  # Helper Functions

  def clean_map_downloads_dir(self):
    self.remove_files(self.downloads_dir, "dat")
    self.copy_test_data_file("idcounts.dat", self.downloads_dir)

  def create_download_link(self, data):
    return self.client.post("/map/download", data = data)

  def start_download(self, filename):
    return self.client.get("/map/download/{}".format(filename))

  def create_request_data(self, map_id):
    data = OrderedMultiDict()
    data.add("mapId", map_id)

    return data