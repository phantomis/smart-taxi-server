import datetime
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from geolocation.models import Location
from tastypie.models import ApiKey
from django.db import IntegrityError
from pprint import pprint

class LocationResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['admin_user.json']

    def runTest(self):
        super(LocationResourceTest, self).runTest()


    def setUp(self):
        super(LocationResourceTest, self).setUp()

        # Create a user.
        self.username1 = 'johndoe'
        self.email1 = 'johndoe@example.com'
        self.password1 = 'password'
        self.user1 = User.objects.create_user(username=self.username1,email=self.email1,password=self.password1)

        #Another user
        self.username2 = 'jperez'
        self.email2 = 'jperez@example.com'
        self.password2 = 'password'
        self.user2 = User.objects.create_user(username=self.username2,email=self.email2,password=self.password2)

        # Create an API key for the user:
        ApiKey.objects.get_or_create(user=self.user1)
        ApiKey.objects.get_or_create(user=self.user2)


        self.base_api_url = '/api/v1'
        self.locations_url = self.base_api_url+'/location/'
        self.user_login_url = self.base_api_url+'/account/login/'
        self.client_url = self.base_api_url+'/client/'

        self.post_location_data1 = {
            'latitude': '-33.046659',
            'longitude': '-71.417034',
            'speed': '65',
            }
        self.post_location_data2 = {
            'latitude': '-33',
            'longitude': '-71',
            'speed': '10',
            }
        self.post_location_data3 = {
            'latitude': '-34',
            'longitude': '-72',
            'speed': '20',
            }
        self.post_location_data4 = {
            'latitude': '-35',
            'longitude': '-73',
            'speed': '30',
            }
        self.post_location_data5 = {
            'latitude': '-36',
            'longitude': '-74',
            'speed': '40',
            }


        self.post_client_data  ={
            'name' : 'Nombre Cliente Taxis',
            'address_name': 'Alicante 116',
            'latitude': '-33.046567',
            'longitude': '-71.417089',
        }


    def get_credentials1(self):
        return self.create_apikey(username=self.user1.username, api_key=self.user1.api_key.key)

    def get_credentials2(self):
        return self.create_apikey(username=self.user2.username, api_key=self.user2.api_key.key)

    def test_do_login(self):
        resp = self.api_client.post(self.user_login_url,format='json',data={'username': self.username1 , 'password' : self.password1})
        self.assertValidJSONResponse(resp)
        self.assertKeys(self.deserialize(resp),['ApiKey','Success'])
        self.assertEqual(self.deserialize(resp)['Success'], True)
        self.assertEqual(self.deserialize(resp)['ApiKey'], self.user1.api_key.key)

    def test_do_login_fail(self):
        resp = self.api_client.post(self.user_login_url,format='json',data={'username': 'InvalidUsername' , 'password' : 'InvalidPassword'})
        self.assertHttpUnauthorized(resp)
        self.assertKeys(self.deserialize(resp),['Success', 'Reason'])
        self.assertEqual(self.deserialize(resp)['Success'], False)
        self.assertEqual(self.deserialize(resp)['Reason'],'incorrect')


    def test_post_location_by_userlocation_unauthenticated(self):
        resp = self.api_client.post(self.locations_url, format='json', data=self.post_location_data1)
        self.assertHttpUnauthorized(resp)

    def test_post_location_by_user(self):
        self.assertEqual(Location.objects.count(), 0)
        auth = self.get_credentials1()
        resp = self.api_client.post(self.locations_url, format='json', data=self.post_location_data1, authentication=auth)
        self.assertHttpCreated(resp)
        self.assertEqual(Location.objects.count(), 1)

    def test_get_taxis_all(self):
        print self.get_credentials1()
        print self.get_credentials2()
        self.assertHttpCreated(self.api_client.post(self.locations_url, format='json', data=self.post_location_data1, authentication=self.get_credentials1()))
        self.assertHttpCreated(self.api_client.post(self.locations_url, format='json', data=self.post_location_data2, authentication=self.get_credentials1()))
        self.assertHttpCreated(self.api_client.post(self.locations_url, format='json', data=self.post_location_data3, authentication=self.get_credentials2()))
        self.assertHttpCreated(self.api_client.post(self.locations_url, format='json', data=self.post_location_data4, authentication=self.get_credentials2()))
        self.assertValidJSONResponse(self.api_client.get(self.locations_url,format='json', authentication=self.get_credentials1()))
        self.assertValidJSONResponse(self.api_client.get(self.locations_url,format='json', authentication=self.get_credentials2()))

    #def test_get_taxis_last_position(self):
    #    self.assertHttpCreated(self.api_client.post(self.locations_url, format='json', data=self.post_location_data1, authentication=self.get_credentials1()))
    #    self.assertHttpCreated(self.api_client.post(self.locations_url, format='json', data=self.post_location_data2, authentication=self.get_credentials1()))
    #    self.assertHttpCreated(self.api_client.post(self.locations_url, format='json', data=self.post_location_data3, authentication=self.get_credentials2()))
    #    self.assertHttpCreated(self.api_client.post(self.locations_url, format='json', data=self.post_location_data4, authentication=self.get_credentials2()))
    #    resp = self.api_client.get(self.locations_url,format='json', authentication=self.get_credentials2())
    #    pprint(self.deserialize(resp)['objects'])
    #    pass

    #def test_can_add_client(self):

    #    resp = self.api_client.post(self.client_url,format='json', data=self.post_client_data)
    #    pprint(self.deserialize(resp))

# def test_get_locations(self):
#        # Try api key authentication using ResourceTestCase.create_apikey().
#        resp = self.api_client.get(self.locations_url,authentication=self.get_credentials(),format='json')
#        self.assertHttpOK(resp)
#
#    def test_get_locations_unauthorzied(self):
#        resp = self.api_client.get(self.locations_url)
#        self.assertHttpUnauthorized(resp)
#
#
#    def test_test_is_working(self):
#        self.assertGreater(2,1)
#
#    def test_put_location_unauthenticated(self):
#        self.assertHttpUnauthorized(self.api_client.put(self.locations_url, format='json', data={}))
