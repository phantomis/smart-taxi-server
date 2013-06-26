# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from gcm.models import Device

from django.db import models

class Taxi(models.Model):
    STATUS_CHOICES = (
        ('1', 'Available'),
        ('2', 'Not Available'),
        ('3', 'Away'),
    )
    user = models.OneToOneField(User)
    license_plate = models.TextField(u'Licence Plate',max_length=6,blank=True,null=True)
    status = models.CharField(u'Status',max_length=2,choices=STATUS_CHOICES)
    device = models.OneToOneField(Device, blank=True, null=True)
    def __unicode__(self):
        return "Taxi %s for user %s" % (self.license_plate,self.user)


class Location(models.Model):
    user = models.ForeignKey(User)
    latitude = models.CharField(u'Latitude', max_length=25, blank=True, null=True)
    longitude = models.CharField(u'Longitude', max_length=25, blank=True, null=True)
    speed = models.CharField(u'Speed', max_length=25, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return " %s (%s,%s) for user %s" % (self.id, self.latitude, self.longitude,self.user)

class ClientLocation(models.Model):
    address_name = models.CharField(u'Full Adress', max_length=200, blank=True, null= True)
    latitude = models.CharField(u'Latitude', max_length=25, blank=True, null=True)
    longitude = models.CharField(u'Longitude', max_length=25, blank=True, null=True)

    def __unicode__(self):
        return "%s (%s, %s)" % (self.address_name, self.latitude, self.longitude)

class Client(models.Model):
    name = models.CharField(u'Full Name', max_length=60, blank=True, null= True)
    phone_number = models.CharField(u'Phone Number', max_length=10, blank=True, null= True)
    location = models.ForeignKey(ClientLocation)

    def __unicode__(self):
        return " %s: %s" % (self.name, self.location)


class Notification(models.Model):
    STATUS_CHOICES = (
        ('1', 'Created'),
        ('2', 'Sended'),
        ('3', 'Responded'),
        ('4', 'Rejected'),
    )
    client = models.ForeignKey(Client)
    taxi = models.ForeignKey(Taxi)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(u'Status',max_length=2,choices=STATUS_CHOICES, default='1')

    def __unicode__(self):
        return u"  %s in %s ( %s ) " % ( self.client.name, self.taxi, self.status)


from pprint import pprint
def send_notification(sender, **kwargs):
        """
        Señal que manda el mensaje automaticamente se guarda un item en el modelo Notification
        """
        if kwargs.get('created') is True:
            pprint(kwargs)
            notif = kwargs.get("instance")
            notif.taxi.device.send_message("mensaje")