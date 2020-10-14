from test_map_base import TestMapBase
from unittest.mock import call, patch

from werkzeug.datastructures import OrderedMultiDict
from io import BytesIO
from mrt_file_server.utils.nbt_utils import load_nbt_file, get_nbt_map_value

import os
import pytest

class TestMapUpload(TestMapBase):
  def setup(self):
    TestMapBase.setup(self)
    self.uploads_dir = self.app.config["MAP_UPLOADS_DIR"]
    self.reset_map_uploads_dir()

  def teardown(self):
    TestMapBase.teardown(self)
    self.reset_map_uploads_dir()

  # Tests

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_single_file_should_be_successful(self, mock_logger):
    username = "Frumple"
    filename = "map_1500.dat"

    self.copy_test_data_file("existing_unlocked.dat", self.uploads_dir, filename)

    original_file_content = self.load_test_data_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("map", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    expected_nbt_file = self.load_test_data_nbt_file(filename)
    uploaded_nbt_file = self.load_uploaded_nbt_file(filename)

    self.verify_matching_nbt_values(expected_nbt_file, uploaded_nbt_file)

    assert get_nbt_map_value(uploaded_nbt_file, "locked") == 1

    self.verify_flash_message_by_key("MAP_UPLOAD_SUCCESS", response.data, filename)
    mock_logger.info.assert_called_with(self.get_log_message("MAP_UPLOAD_SUCCESS"), filename, username)

  # Helper Functions

  def perform_upload(self, data):
    return self.client.post("/map/upload", content_type = "multipart/form-data", data = data)

  def reset_map_uploads_dir(self):
    self.remove_files(self.uploads_dir, "dat")
    self.copy_test_data_file("idcounts.dat", self.uploads_dir)

  def load_test_data_nbt_file(self, filename):
    return load_nbt_file(os.path.join(self.TEST_DATA_DIR, filename))

  def load_uploaded_nbt_file(self, filename):
    return load_nbt_file(os.path.join(self.uploads_dir, filename))

  def verify_matching_nbt_values(self, expected_nbt_file, actual_nbt_file):
    assert get_nbt_map_value(actual_nbt_file, "scale") == get_nbt_map_value(expected_nbt_file, "scale")
    assert get_nbt_map_value(actual_nbt_file, "dimension") == get_nbt_map_value(expected_nbt_file, "dimension")
    assert get_nbt_map_value(actual_nbt_file, "trackingPosition") == get_nbt_map_value(expected_nbt_file, "trackingPosition")
    assert get_nbt_map_value(actual_nbt_file, "unlimitedTracking") == get_nbt_map_value(expected_nbt_file, "unlimitedTracking")
    assert get_nbt_map_value(actual_nbt_file, "xCenter") == get_nbt_map_value(expected_nbt_file, "xCenter")
    assert get_nbt_map_value(actual_nbt_file, "zCenter") == get_nbt_map_value(expected_nbt_file, "zCenter")
    assert get_nbt_map_value(actual_nbt_file, "banners") == get_nbt_map_value(expected_nbt_file, "banners")
    assert get_nbt_map_value(actual_nbt_file, "frames") == get_nbt_map_value(expected_nbt_file, "frames")
    assert get_nbt_map_value(actual_nbt_file, "colors") == get_nbt_map_value(expected_nbt_file, "colors")
