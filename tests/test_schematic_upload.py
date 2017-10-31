from test_base import TestBase

from collections import OrderedDict
from werkzeug import OrderedMultiDict
from io import BytesIO
import os

class TestSchematicUpload(TestBase):
  def setUp(self):
    TestBase.setUp(self)
    self.clean_schematic_uploads_dir()
 
  def tearDown(self):
    TestBase.tearDown(self)
    self.clean_schematic_uploads_dir()

  # Tests

  def test_upload_single_file_should_be_successful(self):
    filename = "mrt_v5_final_elevated_centre_station.schematic"
    original_file_content = self.load_file(filename)

    data = OrderedMultiDict()
    data.add("userName", "Frumple")
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('UPLOAD_SUCCESS', response.data, filename)
    self.verify_uploaded_file_content(original_file_content, filename)

  def test_upload_multiple_files_should_be_successful(self):
    # Upload 5 files
    filenames = [
      "mrt_v5_final_elevated_centre_station.schematic",
      "mrt_v5_final_elevated_side_station.schematic",
      "mrt_v5_final_elevated_single_track.schematic",
      "mrt_v5_final_elevated_double_track.schematic",
      "mrt_v5_final_elevated_double_curve.schematic"]

    original_files = self.load_files(filenames)

    data = OrderedMultiDict()
    data.add("userName", "Frumple")

    for filename in original_files:
      data.add("schematic", (BytesIO(original_files[filename]), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")
      
    for filename in original_files:
      self.verify_flash_message_by_key('UPLOAD_SUCCESS', response.data, filename)
      self.verify_uploaded_file_content(original_files[filename], filename)

  def test_upload_with_no_username_should_fail(self):
    filename = "mrt_v5_final_elevated_centre_station.schematic"
    original_file_content = self.load_file(filename)

    data = OrderedMultiDict()
    data.add("userName", "")
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('UPLOAD_USERNAME_EMPTY', response.data)
    self.verify_schematic_uploads_dir_is_empty()

  def test_upload_with_username_containing_whitespace_should_fail(self):
    filename = "mrt_v5_final_elevated_centre_station.schematic"
    original_file_content = self.load_file(filename)

    data = OrderedMultiDict()
    data.add("userName", "Eris The Eagle")
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('UPLOAD_USERNAME_WHITESPACE', response.data)
    self.verify_schematic_uploads_dir_is_empty()

  def test_upload_with_no_files_should_fail(self):
    data = OrderedMultiDict()
    data.add("userName", "Frumple")

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")
    
    self.verify_flash_message_by_key('UPLOAD_NO_FILES', response.data)
    self.verify_schematic_uploads_dir_is_empty()

  def test_upload_too_many_files_should_fail(self):
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
    data.add("userName", "Frumple")

    for filename in original_files:
      data.add("schematic", (BytesIO(original_files[filename]), filename))

    response = self.perform_upload(data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "text/html")

    self.verify_flash_message_by_key('UPLOAD_TOO_MANY_FILES', response.data)
    self.verify_schematic_uploads_dir_is_empty()

  # Helper Methods

  def load_file(self, filename):
    filepath = os.path.join(self.TEST_DATA_DIR, filename)
    return self.read_data_file(filepath)

  def load_files(self, filenames):
    files = OrderedDict()
    for filename in filenames:
      file_content = self.load_file(filename)
      files[filename] = file_content

    return files

  def perform_upload(self, data):
    return self.client.post('/schematic/upload', content_type = 'multipart/form-data', data = data)

  def clean_schematic_uploads_dir(self):
    self.remove_files(self.app.config['SCHEMATIC_UPLOADS_DIR'], "schematic")

  def verify_schematic_uploads_dir_is_empty(self):
    self.assertFalse(os.listdir(self.app.config['SCHEMATIC_UPLOADS_DIR']))  

  def verify_uploaded_file_content(self, original_file_content, filename):
    uploaded_filepath = os.path.join(self.app.config['SCHEMATIC_UPLOADS_DIR'], filename)
    uploaded_file_content = self.read_data_file(uploaded_filepath)
    self.assertEqual(uploaded_file_content, original_file_content)