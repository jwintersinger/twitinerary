from twitinerary.models import AuthenticatedUser, UnauthenticatedUser

class UserMiddleware():
  def process_request(self, request):
    user_key = request.session.get('user_key')
    if user_key:
      request.user = AuthenticatedUser.get(user_key)
    else:
      request.user = UnauthenticatedUser()
