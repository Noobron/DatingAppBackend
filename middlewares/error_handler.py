from django.http import HttpResponse
from django.conf import settings
import traceback
import logging

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """
    Middleware for handling API Exceptions
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):

        if settings.DEBUG:
            if exception:
                # error message to given in case of exception
                message = "**{url}**\n\n{error}\n\n````{tb}````".format(
                    url=request.build_absolute_uri(),
                    error=repr(exception),
                    tb=traceback.format_exc(chain=False))

                logger.error(message)

        return HttpResponse("Error processing the request.", status=500)