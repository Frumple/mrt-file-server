from nbt.nbt import *

import io
import gzip

def load_compressed_nbt_file(filename):
  return NBTFile(filename)

def load_compressed_nbt_buffer(compressed_buffer):
  uncompresssed_buffer = gzip.decompress(compressed_buffer)
  bytes_io = io.BytesIO(uncompresssed_buffer)
  return load_uncompressed_nbt_buffer(bytes_io)

def load_uncompressed_nbt_buffer(uncompresssed_buffer):
  return NBTFile(buffer=uncompresssed_buffer)

def save_compressed_nbt_file(nbt):
  nbt.write_file()

def get_nbt_map_value(nbt, tag_name):
  data = get_nbt_tag(nbt, "data")
  if data is None:
    return None
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
