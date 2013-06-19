from django.db import IntegrityError

__author__ = 'phantomis'
from tastypie.models import ApiKey
from django.contrib.auth.models import User
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        self.setUp();

    def setUp(self):
    # Create a user.
        username1 = 'johndoe'
        email1 = 'johndoe@example.com'
        password1 = 'password'
        try:
            user1 = User.objects.create_user(username=username1,email=email1,password=password1)
        except IntegrityError:
            user1 = User.objects.get(username=username1,email=email1)
        #Another user
        username2 = 'jperez'
        email2 = 'jperez@example.com'
        password2 = 'password'
        try:
            user2 = User.objects.create_user(username=username2,email=email2,password=password2)
        except IntegrityError:
            user2 = User.objects.get(username=username2,email=email2)
        # Create an API key for the user:
        ApiKey.objects.get_or_create(user=user1)
        ApiKey.objects.get_or_create(user=user2)
        self.stdout.write(self.create_apikey(user1.username, user1.api_key.key))
        self.stdout.write(self.create_apikey(user2.username, user2.api_key.key))

    def create_apikey(self,username, api_key):
        """
        Creates & returns the HTTP ``Authorization`` header for use with
        ``ApiKeyAuthentication``.
        """
        return 'ApiKey %s:%s' % (username, api_key)

    def add_loc(self):
        pass