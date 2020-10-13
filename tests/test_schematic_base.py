from test_base import TestBase

import os

class TestSchematicBase(TestBase):
  def setup(self):
    TestBase.setup(self)
    self.TEST_DATA_DIR = os.path.join(self.TEST_DATA_ROOT, "data", "schematics")

  def teardown(self):
    pass