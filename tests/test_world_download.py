from test_base import TestBase
from unittest.mock import patch

import os

class TestWorldDownload(TestBase):
  def setup(self):
    TestBase.setup(self)

    self.FILE_NAME = "mrt-server-world-test.7z"
    self.FILE_SIZE_IN_BYTES = 1073741824

    self.FILE_PATH = os.path.join(
      self.app.config["WORLD_DOWNLOADS_DIR"],
      self.FILE_NAME)

    # Actual Minecraft world files are too large to use as test data.
    # Instead, we create an empty file and pretend that it is 1GB large.
    with open(self.FILE_PATH, "w+b") as self.file:
      self.file.seek(self.FILE_SIZE_IN_BYTES - 1)
      self.file.write(b'\0')
      self.file.flush()

  def teardown(self):
    TestBase.teardown(self)
    os.remove(self.file.name)

  @patch("mrt_file_server.views.log_adapter")
  def test_world_download(self, mock_logger):
    route_to_file = "/world/download/{}".format(self.FILE_NAME)

    response = self.client.get(route_to_file)

    assert response.status_code == 200
    assert response.mimetype == "application/octet-stream"

    assert response.headers.get("Content-Disposition") == "attachment; filename={}".format(self.FILE_NAME)
    assert int(response.headers.get("Content-Length")) == self.FILE_SIZE_IN_BYTES

    mock_logger.info.assert_called_with(self.get_log_message("WORLD_DOWNLOAD_SUCCESS"), self.FILE_NAME)