from django.contrib.auth.models import User
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.db import models
from django.contrib import admin
from tastypie.models import create_api_key,ApiKey
from tastypie.api import Api
from geolocation.api import AccountResource, LocationResource, ClientResource, NotificationResource,TaxiResource, ApiTokenResource
from geolocation import views
from geolocation.models import Location, Client, Taxi, ClientLocation,Notification, send_notification
from gcm.models import Device
from django.contrib.auth.models import User

admin.site.register(ApiKey)
admin.site.register(Location)
admin.site.register(Client)
admin.site.register(Taxi)
admin.site.register(User)
admin.site.register(ClientLocation)
admin.site.register(Notification)
admin.site.register(Device)

models.signals.post_save.connect(create_api_key, sender=User)
models.signals.post_save.connect(send_notification, sender=Notification)

v1_api = Api(api_name='v1')
v1_api.register(AccountResource())
v1_api.register(LocationResource())
v1_api.register(ClientResource())
v1_api.register(NotificationResource())
v1_api.register(TaxiResource())
v1_api.register(ApiTokenResource())

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
    url(r'^$', views.index, name='index'),
    url(r'', include('gcm.urls')),
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.contrib.staticfiles.views', {'document_root': settings.STATIC_ROOT}),
    (r'^media/(?P<path>.*)$', 'django.contrib.staticfiles.views', {'document_root': settings.MEDIA_ROOT}),
)

