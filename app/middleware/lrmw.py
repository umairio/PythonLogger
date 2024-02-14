import logging
from datetime import timedelta

from django.http import HttpResponseForbidden
from django.utils import timezone

from project.settings import BRONZE, GOLD, SILVER


class LogRequestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def __call__(self, request):
        if request.path == "/home":
            if hasattr(request, "user") and request.user.is_authenticated:
                profile = request.user.profile
                loyalty = profile.loyalty
                if loyalty == "gold":
                    n = GOLD
                elif loyalty == "silver":
                    n = SILVER
                else:
                    n = BRONZE
            else:
                return HttpResponseForbidden("Only Authenticated users allowed")

            time_now = timezone.now()
            timelimit = time_now - timedelta(minutes=1)
            if profile.first_time:
                if profile.first_time <= timelimit:
                    profile.first_time = time_now
                    profile.count = 0
                    profile.save()
            else:
                profile.first_time = time_now

            ip = self.get_client_ip(request)
            if (
                profile.count == n
                and profile.first_time > timelimit
            ):
                self.logger.warning(f"User IP {ip} Request limit exceeded")
                return HttpResponseForbidden("Request limit exceeded")
            profile.count += 1
            profile.save()
            self.logger.info(
                f"User IP: {ip} Request time: {time_now} count: {profile.count}"
            )
        response = self.get_response(request)
        return response
