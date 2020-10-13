from test_base import TestBase

import os

class TestMapBase(TestBase):
  def setup(self):
    TestBase.setup(self)
    self.TEST_DATA_DIR = os.path.join(self.TEST_DATA_ROOT, "data", "maps")

  def teardown(self):
    pass