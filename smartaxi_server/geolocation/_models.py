from django.db import models
from django.contrib.auth.models import User
from tastypie.utils import now
import uuid
import hmac
try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha


class Driver(models.Model):
    user = models.OneToOneField(User)
    license_class = models.CharField(max_length=1)
    class Meta:
        ordering = ["user"]
        verbose_name = "Conductor"
        verbose_name_plural = "Conductores"
    def __unicode__(self):
        #user_info = User.objects.get(id=self.user)
        return "%s clase %s" % (self.user,self.license_class)
    
    
class Taxi(models.Model):
    driver = models.OneToOneField(Driver)
    patent = models.CharField(blank=False,max_length=6)
    def __unicode__(self):
        return "%s" % self.patent

class Device(models.Model):
    taxi = models.OneToOneField(Taxi)
    ip_address = models.IPAddressField(blank=True)
    device_id = models.CharField(max_length = 64, unique = True)
    password = models.CharField(max_length=128)
#    device_c2dm = models.ForeignKey(DeviceC2DM)
    last_activity = models.DateTimeField(auto_now_add=True)
    description = models.CharField(blank=True, max_length=1024)
    def __unicode__(self):
        return "%s (%s)" % (self.device_id, self.description)
        

class ApiKey(models.Model):
    device = models.OneToOneField(Device, related_name='api_key')
    key = models.CharField(max_length=256, blank=True, default='')
    created = models.DateTimeField(default=now)
    
    def __unicode__(self):
        return u"%s for %s" % (self.key, self.device)
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ApiKey, self).save(*args, **kwargs)
    
    def generate_key(self):
        new_uuid = uuid.uuid4()
        return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()
    
def create_api_key(sender, **kwargs):
        """
        A signal for hooking up automatic ``ApiKey`` creation.
        """
        if kwargs.get('created') is True:
            ApiKey.objects.get_or_create(device=kwargs.get('instance'))
            
            
class Session(models.Model):
    device = models.ForeignKey(Device)
    key = models.CharField(max_length=256, blank=True, default='')
    is_active = models.BooleanField(default=True)
    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Session, self).save(*args, **kwargs)
    
    def generate_key(self):
        new_uuid = uuid.uuid4()
        return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()
    
    def __unicode__(self):
        if self.is_active:
            return "Session initiated %s : %s" % (self.start_time,self.key)
        else:
            if self.finish_time:
                return "Session finished at %s" % self.finish_time
            else:
                return "Session finished without time"
            
class Location(models.Model):
    session = models.ForeignKey(Session)
    latitude = models.CharField(u'Latitude', max_length=25, blank=True, null=True)
    longitude = models.CharField(u'Longitude', max_length=25, blank=True, null=True)
    speed = models.CharField(u'Speed', max_length=25, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return "(%s,%s) for session %s" % (self.latitude, self.longitude,self.session)

            
            
            
models.signals.post_save.connect(create_api_key, sender=Device)
