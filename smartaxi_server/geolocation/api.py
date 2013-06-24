from django.contrib.auth.models import User
from tastypie.authentication import ApiKeyAuthentication, BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS, ALL
from tastypie.models import ApiKey
from django.conf.urls import url
from tastypie.utils import trailing_slash
from django.contrib.auth import authenticate, login
from tastypie.http import HttpUnauthorized, HttpForbidden
from django.db import models
from gcm.models import Device
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from pprint import pprint
from tastypie import http

from geolocation.models import Location, Client, ClientLocation, Taxi, Notification


#Login example : http://stackoverflow.com/questions/11770501/how-can-i-login-to-django-using-tastypie
#Doc login: curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"username": "a", "password": "b"}' http://127.0.0.1:8080/api/v1/account/login/



class ApiTokenResource(ModelResource):
    class Meta:
        queryset = ApiKey.objects.all()
        resource_name = "token"
        include_resource_uri = False
        fields = ["key"]
        list_allowed_methods = []
        detail_allowed_methods = ["get"]
        authentication = BasicAuthentication()

    def get_detail(self, request, **kwargs):
        if kwargs["pk"] != "auth":
            raise NotImplementedError("Resource not found")

        obj = ApiKey.objects.get(user=request.user)
        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)
        return self.create_response(request, bundle)


class AccountResource(ModelResource):
    taxi = fields.ToOneField('geolocation.api.TaxiResource', 'taxi', full=True, null=True)

    class Meta:
        queryset = User.objects.all()
        resource_name = 'account'
        excludes = ['email', 'password', 'is_superuser']
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        list_allowed_methods = ['get']
        filtering = {"username": ALL}

class PushAuthorization(Authorization):

    def create_list(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user


    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user


class PushResource(ModelResource):
    class Meta:
        queryset = Device.objects.all()
        authorization = PushAuthorization()
        authentication = ApiKeyAuthentication()
        list_allowed_methods = ["post", "get"]
        detail_allowed_methods = ["put"]


class TaxiAuthorization(Authorization):
    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user


class TaxiResource(ModelResource):
    #device = fields.ToOneField('geolocation.api.PushResource', 'device', full=True, null=True)
    class Meta:
        queryset = Taxi.objects.all()
        authorization = TaxiAuthorization()
        authentication = ApiKeyAuthentication()
        allowed_methods = ['post', 'put', 'get']

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/device%s$' % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_device'),
                name='api_taxi_device'),
        ]

    def dispatch_device(self, request, **kwargs):
        self.method_check(request, allowed=['post','put'])
        print request.body
        data = self.deserialize(request, request.body,format=request.META.get('CONTENT_TYPE', 'application/json'))
        print data
        dev_id = data.get('dev_id', '')
        reg_id = data.get('reg_id', '')
        if dev_id and reg_id:
            device, created = Device.objects.get_or_create(dev_id=dev_id, reg_id=reg_id, is_active=True)
            try:
                taxi = Taxi.objects.get(user=request.user)
                print taxi
                taxi.device = device
                device.save()
                taxi.save()
            except ObjectDoesNotExist:
                pass
            return self.create_response(request, {}, http.HttpCreated)

        return self.error_response(request, data, response_class=http.HttpBadRequest)



"""
    Recurso que requiere ApiKey para ingresar una ubicacion al usuario autenticado

    Custom parameters : &only_lasts
"""


class LocationResource(ModelResource):
    user = fields.ForeignKey(AccountResource, 'user', full=True)

    class Meta:
        queryset = Location.objects.all().order_by('-id')
        resource_name = 'location'
        #excludes = ['id',]
        list_allowed_methods = ['post', 'get']
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        filtering = {'user': ALL_WITH_RELATIONS}

    def obj_create(self, bundle, **kwargs):
        if bundle.request.method == 'POST':
            return super(LocationResource, self).obj_create(bundle, user=bundle.request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

    def dehydrate(self, bundle):
        return bundle

    def build_filters(self, filters=None):
        if filters is None: #if you don't pass any filters at all
            filters = {}

        orm_filters = super(LocationResource, self).build_filters(filters)

        if ('only_lasts' in filters):
            query = filters['only_lasts']

            sqs = Location.objects.values('user_id').annotate(max_id=models.Max('id')).values('max_id')

            orm_filters["pk__in"] = sqs

        return orm_filters

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('do_search'), name="api_search"),
        ]

    #Example: http://127.0.0.1:8080/api/v1/location/search/?format=json&lat=-33.0465667&long=-71.417089&r=5
    def do_search(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        #self.is_authenticated(request)
        self.throttle_check(request)

        lat = float(request.GET.get('lat', '0'))
        long = float(request.GET.get('long', '0'))
        r = float(request.GET.get('r', '0'))

        #The filtered search!

        filtered_positions = Location.objects.filter(
            pk__in=Location.objects.values('user_id').annotate(max_id=models.Max('id')).values('max_id'))

        #Elimino los items que no cumplen el radio dado
        excluded = []
        for position in filtered_positions:
            radious = haversine(float(position.longitude), float(position.latitude), long, lat)
            print radious
            print r
            if radious > r:
                excluded.append(position.id)
                #position.delete()
                pass

        pprint(excluded)
        filtered_positions = filtered_positions.exclude(id__in=excluded)
        #pprint(filtered_positions)
        #filtered_positions.filter(~Q(id__in=excluded))
        pprint(filtered_positions)
        #Pagino con los resultados seleccionados
        paginator = Paginator(filtered_positions, 20)

        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")

        objects = []
        for result in page.object_list:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)


class ClientLocationResource(ModelResource):
    class Meta:
        queryset = ClientLocation.objects.all()
        list_allowed_methods = ['post', 'get']
        authorization = Authorization()
        #excludes = ['id','resource_uri']


class ClientResource(ModelResource):
    location = fields.OneToOneField(ClientLocationResource, 'location', full=True)

    class Meta:
        queryset = Client.objects.all()
        list_allowed_methods = ['post', 'get']
        authorization = Authorization()
        always_return_data = True


class NotificationResource(ModelResource):
    taxi = fields.ToOneField(TaxiResource, 'taxi', full=False)
    client = fields.ToOneField(ClientResource, 'client', full=False)

    class Meta:
        queryset = Notification.objects.all()
        authorization = Authorization()
        allowed_methods = ['post', 'get']
        #list_allowed_methods = ['post']


from math import radians, cos, sin, asin, sqrt


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km