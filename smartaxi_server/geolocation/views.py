# Create your views here.

from django.http import HttpResponse
from django.template import Context, loader

from geolocation.models import Location

def index(request):
    latest_poll_list = Location.objects.all()
    template = loader.get_template('map.html')
    context = Context({
        'latest_poll_list': latest_poll_list,
        })
    return HttpResponse(template.render(context))