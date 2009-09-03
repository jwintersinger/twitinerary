from twitinerary.models import UnauthenticatedUser

class UserMiddleware():
  def process_request(self, request):
    request.user = request.session.get('user') or UnauthenticatedUser()
