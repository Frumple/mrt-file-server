from test_schematic_base import TestSchematicBase
from unittest.mock import call, patch

from werkzeug.datastructures import OrderedMultiDict
from io import BytesIO

import os
import pytest

class TestSchematicUpload(TestSchematicBase):
  def setup(self):
    TestSchematicBase.setup(self)
    self.uploads_dir = self.app.config["SCHEMATIC_UPLOADS_DIR"]
    self.clean_schematic_uploads_dir()

  def teardown(self):
    TestSchematicBase.teardown(self)
    self.clean_schematic_uploads_dir()

  # Tests

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("filename", [
    ("mrt_v5_final_elevated_centre_station.schem"),
    ("mrt_v5_final_elevated_centre_station.schematic")
  ])
  def test_upload_single_file_should_be_successful(self, mock_logger, filename):
    username = "Frumple"
    uploaded_filename = self.uploaded_filename(username, filename)
    original_file_content = self.load_test_data_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_flash_message_by_key("SCHEMATIC_UPLOAD_SUCCESS", response.data, uploaded_filename)
    self.verify_file_content(self.uploads_dir, uploaded_filename, original_file_content)

    mock_logger.info.assert_called_with(self.get_log_message("SCHEMATIC_UPLOAD_SUCCESS"), uploaded_filename)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_multiple_files_should_be_successful(self, mock_logger):
    username = "Frumple"

    # Upload 5 files
    filenames = [
      "mrt_v5_final_elevated_centre_station.schem",
      "mrt_v5_final_elevated_side_station.schematic",
      "mrt_v5_final_elevated_single_track.schematic",
      "mrt_v5_final_elevated_double_track.schematic",
      "mrt_v5_final_elevated_double_curve.schematic"]

    original_files = self.load_test_data_files(filenames)

    data = OrderedMultiDict()
    data.add("userName", username)

    for filename in original_files:
      data.add("schematic", (BytesIO(original_files[filename]), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    logger_calls = []

    for filename in original_files:
      uploaded_filename = self.uploaded_filename(username, filename)

      self.verify_flash_message_by_key("SCHEMATIC_UPLOAD_SUCCESS", response.data, uploaded_filename)
      self.verify_file_content(self.uploads_dir, uploaded_filename, original_files[filename])

      logger_calls.append(call(self.get_log_message("SCHEMATIC_UPLOAD_SUCCESS"), uploaded_filename))

    mock_logger.info.assert_has_calls(logger_calls, any_order = True)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("username, message_key", [
    ("",               "SCHEMATIC_UPLOAD_USERNAME_EMPTY"),
    ("Eris The Eagle", "SCHEMATIC_UPLOAD_USERNAME_WHITESPACE")
  ])
  def test_upload_with_invalid_username_should_fail(self, mock_logger, username, message_key):
    filename = "mrt_v5_final_elevated_centre_station.schematic"
    original_file_content = self.load_test_data_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_flash_message_by_key(message_key, response.data)
    self.verify_schematic_uploads_dir_is_empty()

    if username:
      mock_logger.warn.assert_called_with(self.get_log_message(message_key), username)
    else:
      mock_logger.warn.assert_called_with(self.get_log_message(message_key))

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  @pytest.mark.parametrize("filename, message_key", [
    ("admod.schematic",                       "SCHEMATIC_UPLOAD_FILE_TOO_LARGE"),
    ("this file has spaces.schematic",        "SCHEMATIC_UPLOAD_FILENAME_WHITESPACE"),
    ("this_file_has_the_wrong_extension.dat", "SCHEMATIC_UPLOAD_FILENAME_EXTENSION")
  ])
  def test_upload_with_invalid_file_should_fail(self, mock_logger, filename, message_key):
    username = "Frumple"
    uploaded_filename = self.uploaded_filename(username, filename)
    original_file_content = self.load_test_data_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_flash_message_by_key(message_key, response.data, uploaded_filename)
    self.verify_schematic_uploads_dir_is_empty()

    mock_logger.warn.assert_called_with(self.get_log_message(message_key), uploaded_filename)

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_with_no_files_should_fail(self, mock_logger):
    data = OrderedMultiDict()
    data.add("userName", "Frumple")

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_flash_message_by_key("SCHEMATIC_UPLOAD_NO_FILES", response.data)
    self.verify_schematic_uploads_dir_is_empty()

    mock_logger.warn.assert_called_with(self.get_log_message("SCHEMATIC_UPLOAD_NO_FILES"))

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_with_too_many_files_should_fail(self, mock_logger):
    username = "Frumple"

    # Upload 12 files, over the limit of 10.
    filenames = [
      "mrt_v5_final_elevated_centre_station.schematic",
      "mrt_v5_final_elevated_side_station.schematic",
      "mrt_v5_final_elevated_single_track.schematic",
      "mrt_v5_final_elevated_double_track.schematic",
      "mrt_v5_final_elevated_double_curve.schematic",
      "mrt_v5_final_ground_centre_station.schematic",
      "mrt_v5_final_ground_side_station.schematic",
      "mrt_v5_final_ground_single_track.schematic",
      "mrt_v5_final_ground_double_track.schematic",
      "mrt_v5_final_ground_double_curve.schematic",
      "mrt_v5_final_subground_centre_station.schematic",
      "mrt_v5_final_subground_side_station.schematic"]

    original_files = self.load_test_data_files(filenames)

    data = OrderedMultiDict()
    data.add("userName", username)

    for filename in original_files:
      data.add("schematic", (BytesIO(original_files[filename]), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_flash_message_by_key("SCHEMATIC_UPLOAD_TOO_MANY_FILES", response.data)
    self.verify_schematic_uploads_dir_is_empty()

    mock_logger.warn.assert_called_with(self.get_log_message("SCHEMATIC_UPLOAD_TOO_MANY_FILES"))

  @patch("mrt_file_server.utils.log_utils.log_adapter")
  def test_upload_file_that_already_exists_should_fail(self, mock_logger):
    username = "Frumple"
    filename = "mrt_v5_final_elevated_centre_station.schematic"
    uploaded_filename = self.uploaded_filename(username, filename)
    impostor_filename = "mrt_v5_final_underground_single_track.schematic"

    # Copy an impostor file with different content to the uploads directory with the same name as the file to upload
    self.copy_test_data_file(impostor_filename, self.uploads_dir, uploaded_filename)

    original_file_content = self.load_test_data_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    assert response.status_code == 200
    assert response.mimetype == "text/html"

    self.verify_flash_message_by_key("SCHEMATIC_UPLOAD_FILE_EXISTS", response.data, uploaded_filename)

    # Verify that the uploads directory has only the impostor file, and the file has not been modified
    files = os.listdir(self.uploads_dir)
    assert len(files) == 1

    impostor_file_content = self.load_test_data_file(impostor_filename)
    self.verify_file_content(self.uploads_dir, uploaded_filename, impostor_file_content)

    mock_logger.warn.assert_called_with(self.get_log_message("SCHEMATIC_UPLOAD_FILE_EXISTS"), uploaded_filename)

  # Helper Functions

  def perform_upload(self, data):
    return self.client.post("/schematic/upload", content_type = "multipart/form-data", data = data)

  def clean_schematic_uploads_dir(self):
    self.remove_files(self.uploads_dir, "schematic")
    self.remove_files(self.uploads_dir, "schem")

  def uploaded_filename(self, username, filename):
    return "{}-{}".format(username, filename)

  def verify_schematic_uploads_dir_is_empty(self):
    assert os.listdir(self.uploads_dir) == []
