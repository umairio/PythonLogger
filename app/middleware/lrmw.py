import logging
from datetime import datetime, timedelta
from collections import defaultdict
from django.http import HttpResponseForbidden


class LogRequestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)
        formatter = logging.Formatter("%(levelname)s - %(message)s")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        file_handler = logging.FileHandler("requests.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.userlog = defaultdict(list)

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
        for ip in list(self.userlog.keys()):                #iterate over ips
            for time in self.userlog[ip]:                   #iterate over times in one ip
                if time <= timelimit:                       #if first login time is less than (time 1m ago)
                    ips_to_remove.append(ip)                # that ip is recorded in list to remove
                    break                                   #infinite loop is broken and next ip is observed
        for ip in ips_to_remove:
            del self.userlog[ip]                            #recorded ip are removed

                      
    def __call__(self, request):
        time_now = datetime.now()
        ip = self.get_client_ip(request)
        self.logger.info(f"User IP: {ip} Request time: {time_now}")
        self.time_refresh(time_now)                         #calling above function
        
        self.userlog[ip].append(time_now)                   #added new login time 

        if len(self.userlog[ip]) > 5:
            timelimit = time_now - timedelta(minutes=1)    #added new login time 
            self.logger.info(f"Request times for {ip} within the last minute: {self.userlog[ip]}")
            if self.userlog[ip][0] > timelimit:             #if first login time is geater than (time 1m ago) AND number of requests are more than 5 == response forbidden
                self.logger.warning(f"IP {ip} exceeded rate limit")
                return HttpResponseForbidden("Rate limit exceeded")

        response = self.get_response(request)
        return response
