from nbt.nbt import *

def load_nbt_file(filename):
  return NBTFile(filename, "rb")

def save_nbt_file(nbt):
  nbt.write_file()

def get_nbt_map_value(nbt, tag_name):
  data = get_nbt_tag(nbt, "data")
  tag = get_nbt_tag(data, tag_name)
  return tag.value if tag is not None else None

def get_nbt_tag(parent, name):
  try:
    return parent.__getitem__(name)
  except KeyError:
    return None

def set_nbt_map_byte_value(nbt, tag_name, value):
  data = get_nbt_tag(nbt, "data")
  set_nbt_byte_value(data, tag_name, value)

def set_nbt_byte_value(parent, name, value):
  tag = TAG_Byte(name)
  tag.name = name
  tag.value = int(value)
  parent.__setitem__(name, tag)
