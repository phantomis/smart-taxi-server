"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from tastypie.models import ApiKey
from pprint import pprint

class LoginTest(TestCase):

    fixtures = ['admin_user.json']

    def test_create_superuser(self):
    # store the password to login later

        user = User.objects.create_user('testUser', 'no@email.com', 'mypassword')
        user.save()

        all_users_in_database = User.objects.all()
        #pprint(vars(all_users_in_database))
        self.assertEquals(len(all_users_in_database), 2)
        first_user = all_users_in_database[1 ]
        self.assertEquals(first_user, user)

        # and check that it's saved its two attributes: question and pub_date
        self.assertEquals(first_user.username, user.username)
        self.assertEquals(first_user.email, user.email)
        self.assertEquals(first_user.password, user.password)

        #pprint(vars(ApiKey.objects.all()))

    pass

    def test_login_into_system(self):
        pass
