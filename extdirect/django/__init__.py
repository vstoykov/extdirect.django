from django.utils.importlib import import_module

from providers import ExtRemotingProvider, ExtPollingProvider
from store import ExtDirectStore
from crud import ExtDirectCRUD
from decorators import remoting, polling, crud
from router import DjangoDirectRouter as DirectRouter
from router import register_router

LOADING = False

def autodiscover(name='direct'):
    """
    Autodiscover direct modules of django app
    """
    global LOADING
    if LOADING:
        return
    LOADING = True
    import imp
    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue
        try:
            imp.find_module(name, app_path)
        except ImportError:
            continue
        import_module("%s.%s" % (app, name))
    LOADING = False

