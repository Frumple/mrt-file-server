import re

def str_contains_whitespace(str):
  return bool(re.search(r"\s", str))