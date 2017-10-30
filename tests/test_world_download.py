from test_base import TestBase

import os

class TestWorldDownload(TestBase):
  def setUp(self):
    TestBase.setUp(self)

    self.FILE_NAME = "mrt-server-world-test.7z"
    self.FILE_SIZE_IN_BYTES = 1073741824

    self.FILE_PATH = os.path.join(
      self.app.config['WORLD_DOWNLOADS_DIR'],
      self.FILE_NAME)

    # Actual Minecraft world files are too large to use as test data.
    # Instead, we create an empty file and pretend that it is 1GB large.
    with open(self.FILE_PATH, "w+b") as self.file:
      self.file.seek(self.FILE_SIZE_IN_BYTES-1)
      self.file.write(b'\0')
      self.file.flush()

  def tearDown(self):
    TestBase.tearDown(self)
    os.remove(self.file.name)

  def test_world_download(self):
    route_to_file = "/world/download/{}".format(self.FILE_NAME)

    response = self.client.get(route_to_file)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.mimetype, "application/octet-stream")

    self.assertEqual(response.headers.get("Content-Disposition"), "attachment; filename={}".format(self.FILE_NAME))
    self.assertEqual(int(response.headers.get("Content-Length")), self.FILE_SIZE_IN_BYTES)
    self.assertEqual(os.path.normpath(response.headers.get("X-Sendfile")), self.FILE_PATH)