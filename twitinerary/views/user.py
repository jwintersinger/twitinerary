from django.http import HttpResponseRedirect

# Should be in its own separate application, perhaps, but this is the only user account-related view
# I have at the moment, and so its presence here is acceptable.
def logout(request):
  # If user unauthenticated, he will not be stored in the session.
  if request.user.is_authenticated():
    del request.session['user']
  return HttpResponseRedirect(reverse(home))
