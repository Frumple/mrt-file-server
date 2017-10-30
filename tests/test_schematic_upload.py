from test_base import TestBase

from werkzeug import OrderedMultiDict
from io import BytesIO
import os

class TestSchematicUpload(TestBase):
  def setUp(self):
    TestBase.setUp(self)

    self.FLASH_MESSAGE_SUCCESS = "Success!"
 
  def tearDown(self):
    TestBase.tearDown(self)
    self.remove_files(self.app.config['SCHEMATIC_UPLOADS_DIR'], "schematic")

  def verify_uploaded_file_content(self, filename, original_file_content):
    uploaded_filepath = os.path.join(self.app.config['SCHEMATIC_UPLOADS_DIR'], filename)   
    uploaded_file_content = self.read_data_file(uploaded_filepath)
    self.assertEqual(uploaded_file_content, original_file_content)

  def test_single_file_upload(self):
    filename = "mrt_v5_final_elevated_centre_station.schematic"

    original_filepath = os.path.join(self.TEST_DATA_DIR, filename)
    original_file_content = self.read_data_file(original_filepath)

    data = OrderedMultiDict()
    data.add("userName", "Frumple")
    data.add("schematic", (BytesIO(original_file_content), filename))

    response = self.client.post(
      '/schematic/upload',
      content_type = 'multipart/form-data',
      data = data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype,"text/html")
    self.verify_flash_message(filename, self.FLASH_MESSAGE_SUCCESS, response.data)
    self.verify_uploaded_file_content(filename, original_file_content)

  def test_multiple_file_upload(self):
    filenames = [
      "mrt_v5_final_elevated_centre_station.schematic",
      "mrt_v5_final_elevated_side_station.schematic",
      "mrt_v5_final_elevated_single_track.schematic",
      "mrt_v5_final_elevated_double_track.schematic",
      "mrt_v5_final_elevated_double_curve.schematic"]

    data = OrderedMultiDict()
    data.add("userName", "Frumple")

    original_files = []  

    for filename in filenames:
      original_filepath = os.path.join(self.TEST_DATA_DIR, filename)
      original_file_content = self.read_data_file(original_filepath)
      
      data.add("schematic", (BytesIO(original_file_content), filename))

      original_files.append((filename, original_file_content))

    response = self.client.post(
      '/schematic/upload',
      content_type = 'multipart/form-data',
      data = data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype,"text/html")
      
    for file in original_files:
      filename = file[0]
      original_file_content = file[1]
      self.verify_flash_message(filename, self.FLASH_MESSAGE_SUCCESS, response.data)
      self.verify_uploaded_file_content(filename, original_file_content)