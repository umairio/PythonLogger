from django.shortcuts import render
import logging


def index(request):
    return render(request, "index.html")


logger = logging.getLogger("app.views")


def my_view(request):
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
