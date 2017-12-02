from logging import LoggerAdapter

class RequestLogAdapter(LoggerAdapter):
  def __init__(self, logger, request, extra = {}):
    LoggerAdapter.__init__(self, logger, extra)
    self.request = request

  def process(self, msg, kwargs):
    return '[%s] %s' % (self.request.remote_addr, msg), kwargs