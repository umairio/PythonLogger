import logging
from datetime import datetime, timedelta

from django.http import HttpResponseForbidden

from project.settings import BRONZE, GOLD, SILVER, UNAUTH


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
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                if profile.times:
                    profile.times += f", {current_time}"
                else:
                    profile.times = current_time
                profile.count += 1
                profile.save()

                loyalty = profile.loyalty
                if loyalty == "gold":
                    n = GOLD
                elif loyalty == "silver":
                    n = SILVER
                elif loyalty == "bronze":
                    n = BRONZE
                else:
                    n = UNAUTH
            else:
                return HttpResponseForbidden("Only Authenticated users allowed")

            time_now = datetime.now()
            ip = self.get_client_ip(request)
            self.logger.info(
                f"User IP: {ip} Request time: {time_now} count: {profile.count}"
            )
            timelimit = time_now - timedelta(minutes=1)
            times = profile.times.split(", ")
            first_time = (
                datetime.strptime(times[0], "%Y-%m-%d %H:%M:%S.%f") if times else None
            )

            for time in times:  # iterate over times in one ip
                if datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f") <= timelimit:
                    profile.count = 1
                    profile.times = ""
                    profile.save()

            if profile.count > n:
                if first_time and first_time > timelimit:
                    self.logger.warning(f"User IP {ip} Request limit exceeded")
                    return HttpResponseForbidden("Request limit exceeded")

        response = self.get_response(request)
        return response
