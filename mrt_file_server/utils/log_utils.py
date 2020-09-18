from mrt_file_server import app, logger, log_adapter

def log_info(key, *args, **kwargs):
  log(log_adapter.info, key, *args, **kwargs)

def log_warn(key, *args, **kwargs):
  log(log_adapter.warn, key, *args, **kwargs)

def log_error(key, *args, **kwargs):
  log(log_adapter.error, key, *args, **kwargs)

def log(log_function, key, *args, **kwargs):
  log_function(get_log_message(key), *args, **kwargs)

def get_log_message(key):
  return app.config["LOG_MESSAGES"][key]