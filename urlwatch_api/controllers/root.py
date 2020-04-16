from pecan import expose, redirect
from webob.exc import status_map
from .api import APIController

class RootController(object):

    @expose()
    def index(self):
        redirect('/index.html')

    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)

    api = APIController()
