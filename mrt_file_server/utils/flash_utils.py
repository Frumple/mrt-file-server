from flask import flash
from markupsafe import Markup

def get_flash_message(app, key):
  return app.config["FLASH_MESSAGES"][key]

def flash_by_key(app, key, filename = None):
  flash_message = get_flash_message(app, key)

  if filename:
    flash(Markup("{}: {}".format(filename, flash_message.message.format(filename))), flash_message.category)
  else:
    flash(Markup(flash_message.message), flash_message.category)