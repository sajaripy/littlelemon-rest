from rest_framework.throttling import UserRateThrottle

class TenCalllsPerMinute(UserRateThrottle):
    scope = 'ten'