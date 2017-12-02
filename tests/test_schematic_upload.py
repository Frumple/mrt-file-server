from test_base import TestBase
from unittest.mock import call, patch

from werkzeug import OrderedMultiDict
from io import BytesIO
from shutil import copyfile
import os

class TestSchematicUpload(TestBase):
  def setUp(self):
    TestBase.setUp(self)
    self.uploads_dir = self.app.config['SCHEMATIC_UPLOADS_DIR']
    self.clean_schematic_uploads_dir()
 
  def tearDown(self):
    TestBase.tearDown(self)
    self.clean_schematic_uploads_dir()

  # Tests

  @patch("mrt_file_server.views.log_adapter")
  def test_upload_single_file_should_be_successful(self, mock_logger):
    username = "Frumple"
    filename = "mrt_v5_final_elevated_centre_station.schematic"
    uploaded_filename = self.uploaded_filename(username, filename)
    original_file_content = self.load_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('SCHEMATIC_UPLOAD_SUCCESS', response.data, uploaded_filename)
    self.verify_uploaded_file_content(original_file_content, uploaded_filename)

    mock_logger.info.assert_called_with(self.get_log_message('SCHEMATIC_UPLOAD_SUCCESS'), uploaded_filename)

  @patch("mrt_file_server.views.log_adapter")
  def test_upload_multiple_files_should_be_successful(self, mock_logger):
    username = "Frumple"

    # Upload 5 files
    filenames = [
      "mrt_v5_final_elevated_centre_station.schematic",
      "mrt_v5_final_elevated_side_station.schematic",
      "mrt_v5_final_elevated_single_track.schematic",
      "mrt_v5_final_elevated_double_track.schematic",
      "mrt_v5_final_elevated_double_curve.schematic"]

    original_files = self.load_files(filenames)

    data = OrderedMultiDict()
    data.add("userName", username)

    for filename in original_files:
      data.add("schematic", (BytesIO(original_files[filename]), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    logger_calls = []
      
    for filename in original_files:
      uploaded_filename = self.uploaded_filename(username, filename)

      self.verify_flash_message_by_key('SCHEMATIC_UPLOAD_SUCCESS', response.data, uploaded_filename)
      self.verify_uploaded_file_content(original_files[filename], uploaded_filename)

      logger_calls.append(call(self.get_log_message('SCHEMATIC_UPLOAD_SUCCESS'), uploaded_filename))

    mock_logger.info.assert_has_calls(logger_calls, any_order = True)

  @patch("mrt_file_server.views.log_adapter")
  def test_upload_with_no_username_should_fail(self, mock_logger):
    filename = "mrt_v5_final_elevated_centre_station.schematic"
    original_file_content = self.load_file(filename)

    data = OrderedMultiDict()
    data.add("userName", "")
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('SCHEMATIC_UPLOAD_USERNAME_EMPTY', response.data)
    self.verify_schematic_uploads_dir_is_empty()

    mock_logger.warn.assert_called_with(self.get_log_message('SCHEMATIC_UPLOAD_USERNAME_EMPTY'))

  @patch("mrt_file_server.views.log_adapter")
  def test_upload_with_username_containing_whitespace_should_fail(self, mock_logger):
    username = "Eris The Eagle"
    filename = "mrt_v5_final_elevated_centre_station.schematic"
    original_file_content = self.load_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('SCHEMATIC_UPLOAD_USERNAME_WHITESPACE', response.data)
    self.verify_schematic_uploads_dir_is_empty()

    mock_logger.warn.assert_called_with(self.get_log_message('SCHEMATIC_UPLOAD_USERNAME_WHITESPACE'), username)

  @patch("mrt_file_server.views.log_adapter")
  def test_upload_with_no_files_should_fail(self, mock_logger):
    data = OrderedMultiDict()
    data.add("userName", "Frumple")

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")
    
    self.verify_flash_message_by_key('SCHEMATIC_UPLOAD_NO_FILES', response.data)
    self.verify_schematic_uploads_dir_is_empty()

    mock_logger.warn.assert_called_with(self.get_log_message('SCHEMATIC_UPLOAD_NO_FILES'))

  @patch("mrt_file_server.views.log_adapter")
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

    original_files = self.load_files(filenames)

    data = OrderedMultiDict()
    data.add("userName", username)

    for filename in original_files:
      data.add("schematic", (BytesIO(original_files[filename]), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('SCHEMATIC_UPLOAD_TOO_MANY_FILES', response.data)
    self.verify_schematic_uploads_dir_is_empty()

    mock_logger.warn.assert_called_with(self.get_log_message('SCHEMATIC_UPLOAD_TOO_MANY_FILES'))

  @patch("mrt_file_server.views.log_adapter")
  def test_upload_file_too_large_should_fail(self, mock_logger):
    username = "Frumple"
    filename = "admod.schematic"
    uploaded_filename = self.uploaded_filename(username, filename)
    original_file_content = self.load_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('SCHEMATIC_UPLOAD_FILE_TOO_LARGE', response.data, uploaded_filename)
    self.verify_schematic_uploads_dir_is_empty()

    mock_logger.warn.assert_called_with(self.get_log_message('SCHEMATIC_UPLOAD_FILE_TOO_LARGE'), uploaded_filename)

  @patch("mrt_file_server.views.log_adapter")
  def test_upload_file_that_already_exists_should_fail(self, mock_logger):
    username = "Frumple"
    filename = "mrt_v5_final_elevated_centre_station.schematic"
    uploaded_filename = self.uploaded_filename(username, filename)
    impostor_filename = "mrt_v5_final_underground_single_track.schematic"

    # Copy an impostor file with different content to the uploads directory with the same name as the file to upload
    src_filepath = os.path.join(self.TEST_DATA_DIR, impostor_filename)
    dest_filepath = os.path.join(self.uploads_dir, uploaded_filename)
    copyfile(src_filepath, dest_filepath)

    original_file_content = self.load_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('SCHEMATIC_UPLOAD_FILE_EXISTS', response.data, uploaded_filename)

    # Verify that the uploads directory has only the impostor file, and the file has not been modified
    files = os.listdir(self.uploads_dir)
    self.assertEqual(len(files), 1)

    impostor_file_content = self.load_file(impostor_filename)
    self.verify_uploaded_file_content(impostor_file_content, uploaded_filename)

    mock_logger.warn.assert_called_with(self.get_log_message('SCHEMATIC_UPLOAD_FILE_EXISTS'), uploaded_filename)

  @patch("mrt_file_server.views.log_adapter")
  def test_upload_file_with_filename_containing_whitespace_should_fail(self, mock_logger):
    username = "Frumple"
    filename = "this file has spaces.schematic"
    uploaded_filename = self.uploaded_filename(username, filename)
    original_file_content = self.load_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('SCHEMATIC_UPLOAD_FILENAME_WHITESPACE', response.data, uploaded_filename)
    self.verify_schematic_uploads_dir_is_empty()

    mock_logger.warn.assert_called_with(self.get_log_message('SCHEMATIC_UPLOAD_FILENAME_WHITESPACE'), uploaded_filename)

  @patch("mrt_file_server.views.log_adapter")  
  def test_upload_file_with_filename_ending_with_invalid_extension_should_fail(self, mock_logger):
    username = "Frumple"
    filename = "this_file_has_the_wrong_extension.dat"
    uploaded_filename = self.uploaded_filename(username, filename)
    original_file_content = self.load_file(filename)

    data = OrderedMultiDict()
    data.add("userName", username)
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('SCHEMATIC_UPLOAD_FILENAME_EXTENSION', response.data, uploaded_filename)
    self.verify_schematic_uploads_dir_is_empty()

    mock_logger.warn.assert_called_with(self.get_log_message('SCHEMATIC_UPLOAD_FILENAME_EXTENSION'), uploaded_filename)

  # Helper Functions

  def perform_upload(self, data):
    return self.client.post('/schematic/upload', content_type = 'multipart/form-data', data = data)

  def clean_schematic_uploads_dir(self):
    self.remove_files(self.uploads_dir, "schematic")

  def uploaded_filename(self, username, filename):
    return "{}-{}".format(username, filename)

  def verify_schematic_uploads_dir_is_empty(self):
    self.assertFalse(os.listdir(self.uploads_dir))

  def verify_uploaded_file_content(self, original_file_content, filename):
    uploaded_filepath = os.path.join(self.uploads_dir, filename)
    uploaded_file_content = self.read_data_file(uploaded_filepath)
    self.assertEqual(uploaded_file_content, original_file_content)