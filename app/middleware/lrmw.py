import logging
from datetime import datetime, timedelta
from collections import defaultdict
from django.http import HttpResponseForbidden
from project.settings import GOLD, SILVER, BRONZE, UNAUTH
import threading


class LogRequestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)
        self.userlog = defaultdict(list)
        self.lock = threading.Lock()

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def time_refresh(self, time_now):
        timelimit = time_now - timedelta(minutes=1)
        ips_to_remove = []
        for ip in list(self.userlog.keys()):  # iterate over ips
            for time in self.userlog[ip]:  # iterate over times in one ip
                if time <= timelimit:
                    # if first login time is less than (time 1m ago)
                    ips_to_remove.append(ip)
                    # that ip is recorded in list to remove
                    break  # infinite loop is broken and next ip is observed
        for ip in ips_to_remove:
            del self.userlog[ip]  # recorded ip are removed

    def __call__(self, request):
        n = 0
        if hasattr(request, "user") and request.user.is_authenticated:
            print(request.user.count)
            loyalty = request.user.loyalty
            if loyalty == "gold":
                n = GOLD
            elif loyalty == "silver":
                n = SILVER
            elif loyalty == "bronze":
                n = BRONZE
        else:
            n = UNAUTH
        time_now = datetime.now()
        ip = self.get_client_ip(request)
        count = len(self.userlog[ip])
        self.logger.info(f"User IP: {ip} Request time: {time_now} count: {count}")
        self.time_refresh(time_now)  # calling above function

        self.userlog[ip].append(time_now)  # added new login time
        count = len(self.userlog[ip])
        request.user.count = count
        request.user.save()
        if count > n:
            timelimit = time_now - timedelta(minutes=1)  # added new login time
            if (self.userlog[ip][0] > timelimit):
                # if first login time is geater than (time 1m ago)
                # AND number of requests are more than 5 == response forbidden
                self.logger.warning(f"User IP {ip} Request limit exceeded")
                return HttpResponseForbidden("Request limit exceeded")

        response = self.get_response(request)
        return response
