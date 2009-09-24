from django.http import HttpResponse
from django.utils import simplejson as json

def JsonResponse(data):
  return HttpResponse(json.dumps(data), content_type='application/json')
