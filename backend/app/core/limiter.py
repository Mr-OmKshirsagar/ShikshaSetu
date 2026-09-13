from slowapi import Limiter
from slowapi.util import get_remote_address

# Default limits are empty; specific endpoints declare explicit limits
limiter = Limiter(key_func=get_remote_address, default_limits=[])
