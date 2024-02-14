import logging
from datetime import datetime, timedelta

from django.http import HttpResponseForbidden

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
                loyalty = request.user.profile.loyalty
                if loyalty == "gold":
                    n = GOLD
                elif loyalty == "silver":
                    n = SILVER
                else:
                    n = BRONZE
            else:
                return HttpResponseForbidden("Only Authenticated users allowed")

            time_now = datetime.now()
            timelimit = time_now - timedelta(minutes=1)
            if request.user.profile.first_time:
                if request.user.profile.first_time <= timelimit:
                    request.user.profile.first_time = time_now
                    request.user.profile.count = 0
                    request.user.profile.save()
            else:
                request.user.profile.first_time = time_now

            ip = self.get_client_ip(request)
            request.user.profile.count += 1
            request.user.profile.save()
            self.logger.info(
                f"User IP: {ip} Request time: {time_now} count: {request.user.profile.count}"
            )
            if (
                request.user.profile.count > n
                and request.user.profile.first_time > timelimit
            ):
                self.logger.warning(f"User IP {ip} Request limit exceeded")
                return HttpResponseForbidden("Request limit exceeded")
        response = self.get_response(request)
        return response
