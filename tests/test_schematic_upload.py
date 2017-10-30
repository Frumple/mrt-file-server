from test_base import TestBase

from io import BytesIO
import os

class TestSchematicUpload(TestBase):
  def setUp(self):
    TestBase.setUp(self)

    self.FLASH_MESSAGE_STATUS_SUCCESS = "Success!"
 
  def tearDown(self):
    TestBase.tearDown(self)
    self.remove_files(self.app.config['SCHEMATIC_UPLOADS_DIR'], "schematic")

  def test_single_file_upload(self):
    filename = "test.schematic"

    original_filepath = os.path.join(self.TEST_DATA_DIR, filename)
    original_file_content = self.read_data_file(original_filepath)

    data = { 
      "userName": "Frumple",
      "schematic": (BytesIO(original_file_content), filename)
    }

    response = self.client.post(
      '/schematic/upload',
      content_type = 'multipart/form-data',
      data = data)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype,"text/html")

    # Verify that a successful flash message is shown
    expected_flash_message = self.flash_message("{}: {}".format(filename, self.FLASH_MESSAGE_STATUS_SUCCESS))
    self.assertIn(bytes(expected_flash_message, encoding = "utf-8"), response.data)

    # Verify that the content of the uploaded file matches the original file
    uploaded_filepath = os.path.join(
      self.app.config['SCHEMATIC_UPLOADS_DIR'],
      filename)

    uploaded_file_content = self.read_data_file(uploaded_filepath)
    self.assertEqual(uploaded_file_content, original_file_content)