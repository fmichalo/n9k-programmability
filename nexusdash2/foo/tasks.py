from __future__ import absolute_import

from celery import shared_task
from .models import FooStats
from utils.fetchcliout import fetchcli_wrapper
import time
 
@shared_task
def poll_foostats(hostname):
    '''
    Create new entry for every poll
    '''
    hostname_obj, fetcho = fetchcli_wrapper(hostname)
    hostname_obj.save()
    foo_stats = fetcho.get_foostats()
    timestamp = time.time()         # Using one common timestamp for one query to device
    for d in foo_stats:
        o = FooStats(hostname=hostname_obj, polling_timestamp=timestamp, **d)
        o.save()
        