from test_map_base import TestMapBase
from unittest.mock import call, patch

from werkzeug.datastructures import OrderedMultiDict
from io import BytesIO
from mrt_file_server.utils.nbt_utils import load_compressed_nbt_file, get_nbt_map_value

import os
import pytest

class TestMapUpload(TestMapBase):
  def setup(self):
    TestMapBase.setup(self)
    self.uploads_dir = self.app.config["MAP_UPLOADS_DIR"]
    self.downloads_dir = self.app.config["MAP_DOWNLOADS_DIR"]
    self.reset_directories()

  def teardown(self):
    TestMapBase.teardown(self)
    self.reset_directories()

  # Tests

  def test_upload_page_should_show_valid_map_id_range(self):
    response = self.client.get("/map/upload")

    last_allowed_id_range = 1000
    last_map_id = 2000

    actual_html = response.data.decode('utf-8')

    expected_lower_map_id_html = "<span id=\"lower_map_id\" style=\"color: green;\">{}</span>".format(last_map_id - last_allowed_id_range + 1)
    expected_upper_map_id_html = "<span id=\"upper_map_id\" style=\"color: green;\">{}</span>".format(last_map_id)

    assert expected_lower_map_id_html in actual_html
    assert expected_upper_map_id_html in actual_html

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_single_file_should_be_successful(self, mock_logger):
    username = "Frumple"
    filename = "map_1500.dat"
    message_key = "MAP_UPLOAD_SUCCESS"

    original_file_content = self.load_test_data_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("map", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    # Verify that the new map file was uploaded and locked
    expected_nbt_file = self.load_test_data_nbt_file(filename)
    uploaded_nbt_file = self.load_uploaded_nbt_file(filename)
    self.verify_matching_nbt_values(expected_nbt_file, uploaded_nbt_file)

    assert get_nbt_map_value(uploaded_nbt_file, "locked") == 1

    self.verify_flash_message_by_key(message_key, response.data, filename)
    mock_logger.info.assert_called_with(self.get_log_message(message_key), filename, username)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_multiple_files_should_be_successful(self, mock_logger):
    username = "Frumple"
    message_key = "MAP_UPLOAD_SUCCESS"

    # Upload 7 files
    filenames = [
      "map_1500.dat",
      "map_2000.dat",
      "map_1501.dat",
      "map_1502.dat",
      "map_1001.dat",
      "map_1503.dat",
      "map_1504.dat"]

    original_files = self.load_test_data_files(filenames)

    data = OrderedMultiDict()
    data.add("userName", username)

    for filename in original_files:
      data.add("map", (BytesIO(original_files[filename]), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    logger_calls = []

    for filename in original_files:
      # Verify that the new map files were uploaded and locked
      expected_nbt_file = self.load_test_data_nbt_file(filename)
      uploaded_nbt_file = self.load_uploaded_nbt_file(filename)
      self.verify_matching_nbt_values(expected_nbt_file, uploaded_nbt_file)

      assert get_nbt_map_value(uploaded_nbt_file, "locked") == 1

      self.verify_flash_message_by_key(message_key, response.data, filename)
      logger_calls.append(call(self.get_log_message(message_key), filename, username))

    mock_logger.info.assert_has_calls(logger_calls, any_order = True)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("username, message_key", [
    ("",               "MAP_UPLOAD_USERNAME_EMPTY"),
    ("Eris The Eagle", "MAP_UPLOAD_USERNAME_WHITESPACE")
  ])
  def test_upload_with_invalid_username_should_fail(self, mock_logger, username, message_key):
    filename = "map_1500.dat"

    upload_file_content = self.load_test_data_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("map", (BytesIO(upload_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_file_does_not_exist(self.uploads_dir, filename)
    self.verify_flash_message_by_key(message_key, response.data)

    if username:
      mock_logger.warn.assert_called_with(self.get_log_message(message_key), username)
    else:
      mock_logger.warn.assert_called_with(self.get_log_message(message_key))

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_with_no_files_should_fail(self, mock_logger):
    username = "Frumple"
    message_key = "MAP_UPLOAD_NO_FILES"

    data = OrderedMultiDict()
    data.add("userName", username)

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_flash_message_by_key(message_key, response.data)
    mock_logger.warn.assert_called_with(self.get_log_message(message_key), username)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_with_too_many_files_should_fail(self, mock_logger):
    username = "Frumple"
    message_key = "MAP_UPLOAD_TOO_MANY_FILES"

    # Upload 11 files, over the limit of 10.
    filenames = [
      "map_1001.dat",
      "map_1500.dat",
      "map_1501.dat",
      "map_1502.dat",
      "map_1503.dat",
      "map_1504.dat",
      "map_1505.dat",
      "map_1506.dat",
      "map_1507.dat",
      "map_1508.dat",
      "map_2000.dat"]

    upload_files = self.load_test_data_files(filenames)

    data = OrderedMultiDict()
    data.add("userName", username)

    for filename in upload_files:
      data.add("map", (BytesIO(upload_files[filename]), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    for filename in filenames:
      self.verify_file_does_not_exist(self.uploads_dir, filename)

    self.verify_flash_message_by_key(message_key, response.data)
    mock_logger.warn.assert_called_with(self.get_log_message(message_key), username)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("filename", [
    ("1510.dat"),      # Does not start with map_
    ("map_.dat"),      # No Map ID
    ("map_-1.dat"),    # Negative Map ID
    ("map_1510a.dat"), # Invalid Map ID
    ("map_1510.png")   # Wrong extension
  ])
  def test_upload_with_invalid_filename_should_fail(self, mock_logger, filename):
    username = "Frumple"
    message_key = "MAP_UPLOAD_FILENAME_INVALID"

    upload_file_content = self.load_test_data_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("map", (BytesIO(upload_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    # Verify that the new map file was NOT uploaded
    uploaded_file_path = os.path.join(self.uploads_dir, filename)
    assert os.path.isfile(uploaded_file_path) == False

    self.verify_flash_message_by_key(message_key, response.data, filename)
    mock_logger.warn.assert_called_with(self.get_log_message(message_key), filename, username)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("filename", [
    ("idcounts.dat"),
    ("raids.dat"),
    ("scoreboard.dat"),
    ("villages.dat")
  ])
  def test_upload_with_invalid_filename_and_file_already_exists_should_fail(self, mock_logger, filename):
    username = "Frumple"
    message_key = "MAP_UPLOAD_FILENAME_INVALID"

    self.copy_test_data_file(filename, self.uploads_dir)
    existing_file_content = self.load_test_data_file(filename)

    # Upload a valid map file, but rename it to the existing filename
    upload_file_content = self.load_test_data_file("map_1500.dat")

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("map", (BytesIO(upload_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    # Verify that the existing map file was NOT overwritten
    self.verify_file_content(self.uploads_dir, filename, existing_file_content)

    self.verify_flash_message_by_key(message_key, response.data, filename)
    mock_logger.warn.assert_called_with(self.get_log_message(message_key), filename, username)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("filename, message_key", [
    ("map_1520.dat", "MAP_UPLOAD_FILE_TOO_LARGE"),      # File size too large
    ("map_1000.dat", "MAP_UPLOAD_MAP_ID_OUT_OF_RANGE"), # Map ID too low
    ("map_2001.dat", "MAP_UPLOAD_MAP_ID_OUT_OF_RANGE"), # Map ID too high
    ("map_1530.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID"),  # idcounts.dat
    ("map_1531.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID"),  # Player .dat file
    ("map_1532.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID"),  # Empty .dat file
    ("map_1533.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID"),  # Without dimension tag
    ("map_1534.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID"),  # Without locked tag
    ("map_1535.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID"),  # Without colors tag
    ("map_1536.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID"),  # Without scale tag
    ("map_1537.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID"),  # Without trackingPosition tag
    ("map_1538.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID"),  # Without xCenter tag
    ("map_1539.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID"),  # Without zCenter tag
    ("map_1540.dat", "MAP_UPLOAD_MAP_FORMAT_INVALID")   # PNG with extension renamed to .dat
  ])
  def test_upload_with_invalid_file_should_fail(self, mock_logger, filename, message_key):
    username = "Frumple"

    upload_file_content = self.load_test_data_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("map", (BytesIO(upload_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_file_does_not_exist(self.uploads_dir, filename)

    self.verify_flash_message_by_key(message_key, response.data, filename)
    mock_logger.warn.assert_called_with(self.get_log_message(message_key), filename, username)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_where_existing_file_is_already_locked_should_fail(self, mock_logger):
    username = "Frumple"
    filename = "map_1500.dat"
    existing_filename = "existing_locked.dat"
    message_key = "MAP_UPLOAD_EXISTING_MAP_LOCKED"

    # The existing file should be in the map downloads directory, which should map to the actual data directory on the Minecraft server.
    self.copy_test_data_file(existing_filename, self.downloads_dir, filename)
    existing_file_content = self.load_test_data_file(existing_filename)

    upload_file_content = self.load_test_data_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("map", (BytesIO(upload_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    # Verify that the existing map file was NOT overwritten
    self.verify_file_content(self.downloads_dir, filename, existing_file_content)

    self.verify_file_does_not_exist(self.uploads_dir, filename)
    self.verify_flash_message_by_key(message_key, response.data, filename)
    mock_logger.warn.assert_called_with(self.get_log_message(message_key), filename, username)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_same_file_twice_should_fail(self, mock_logger):
    username = "Frumple"
    filename = "map_1500.dat"
    message_key = "MAP_UPLOAD_MAP_ALREADY_UPLOADED"

    original_file_content = self.load_test_data_file(filename)

    first_data = OrderedMultiDict()
    first_data.add("userName", username)
    first_data.add("map", (BytesIO(original_file_content), filename))

    first_response = self.perform_upload(first_data)

    second_data = OrderedMultiDict()
    second_data.add("userName", username)
    second_data.add("map", (BytesIO(original_file_content), filename))

    second_response = self.perform_upload(second_data)

    assert second_response.status_code == 200
    assert second_response.mimetype == "text/html"

    # Verify that the new map file was uploaded and locked,
    # but the "map already uploaded" error message appears after second upload
    expected_nbt_file = self.load_test_data_nbt_file(filename)
    uploaded_nbt_file = self.load_uploaded_nbt_file(filename)

    self.verify_matching_nbt_values(expected_nbt_file, uploaded_nbt_file)

    assert get_nbt_map_value(uploaded_nbt_file, "locked") == 1

    self.verify_flash_message_by_key(message_key, second_response.data, filename)
    mock_logger.warn.assert_called_with(self.get_log_message(message_key), filename, username)

  # Helper Functions

  def perform_upload(self, data):
    return self.client.post("/map/upload", content_type = "multipart/form-data", data = data)

  def reset_directories(self):
    self.remove_files(self.uploads_dir, "dat")
    self.remove_files(self.downloads_dir, "dat")
    self.copy_test_data_file("idcounts.dat", self.downloads_dir)

  def load_test_data_nbt_file(self, filename):
    return load_compressed_nbt_file(os.path.join(self.TEST_DATA_DIR, filename))

  def load_uploaded_nbt_file(self, filename):
    return load_compressed_nbt_file(os.path.join(self.uploads_dir, filename))

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
