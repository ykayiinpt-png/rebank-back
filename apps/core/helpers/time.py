from datetime import datetime
from django.utils import timezone

def timestamp_has_expired(expiry_timestamp=None, expiry_datetime=None):
    """
    Checks whether a timestamp has expired or not
    """
    if expiry_datetime is None:
        expiry_datetime = datetime.fromtimestamp(expiry_timestamp, tz=timezone.get_current_timezone())
    
    if timezone.now() < expiry_datetime:
        return False
    else:
        return True
    
def timestamp_add():
    pass