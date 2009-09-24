from django.http import HttpResponse
from lib.http import JsonResponse

def login_required(response_type = 'text'):
  msg = 'Not authenticated.'
  responses = {
    'text': lambda: HttpResponse(msg, status=401, content_type='text/plain'),
    'json': lambda: JsonResponse({'error': msg})
  }

  def decorate(func):
    def decorated(*args, **kwargs):
      request = args[0]
      if not request.user.is_authenticated():
        return responses[response_type]()
      return func(*args, **kwargs)
    return decorated

  # Decorators with optional arguments are somewhat messy. In calling the
  # decorator:
  #   * If no argument is supplied (@login_required), then the decorator will be
  #     called with response_type set to the function to be decorated. I am
  #     expected to return the decorated function.
  #   * If an argument is supplied (@login_required(response_type = 'json')), I
  #     am expected to return a function that, in turn, returns the decorated
  #     function.
  # 
  # See http://coderazzi.net/tnotes/python/decoratorsWithoutArguments.html for
  # details.
  #
  # This all got sufficiently complicated that I now require calling the
  # decorator with empty parentheses to indicate you desire the default
  # response_type.
  return decorate
