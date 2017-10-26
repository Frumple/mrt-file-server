import mrt_file_server
import os
import tempfile
import unittest

class TestWorldDownload(unittest.TestCase):
  def setUp(self):
    mrt_file_server.app.testing = True
    self.app = mrt_file_server.app.test_client()

    temp_file_dir = os.path.normpath(os.path.join( \
      mrt_file_server.app.root_path, \
      mrt_file_server.app.config['WORLD_DOWNLOADS_DIR']))
    self.file = tempfile.NamedTemporaryFile(dir = temp_file_dir, delete = False)

  def tearDown(self):
    self.file.close()
    os.remove(self.file.name)

  def test_world_download(self):
    filename = os.path.basename(self.file.name)
    route_to_file = "/world/download/{}".format(filename)

    with self.app as app:
      response = app.get(route_to_file)
      
      assert response.status_code == 200      
      assert response.headers.get("Content-Disposition") == "attachment; filename={}".format(filename)
      assert os.path.normpath(response.headers.get("X-Sendfile")) == self.file.name
      assert response.mimetype == "application/octet-stream"

if __name__ == '__main__':
  unittest.main()