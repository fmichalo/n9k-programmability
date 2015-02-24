from django.db import models
import datetime


class FooStats(models.Model):
    '''Many-to-one relationship. e.i Many FooStats for one HostName
    # https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_one/
    
    This gets updated by task poll_foostats()
    '''
    hostname = models.ForeignKey('hostnames.HostNames')
    polling_timestamp = models.FloatField()
    stat1 = models.CharField(max_length=100)
    stat2 = models.CharField(max_length=100)
    
    def __unicode__(self):
        return str(datetime.datetime.fromtimestamp(self.polling_timestamp)) + '-' + self.hostname.hostname
    