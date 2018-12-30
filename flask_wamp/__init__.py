import logging
from functools import partial

from flask import g
from wampy.peers.clients import Client
from wampy.constants import CROSSBAR_DEFAULT, DEFAULT_REALM

logger = logging.getLogger(__name__)


class FlaskWAMPClient(Client):

    def __init__(self, url, realm):
        super(FlaskWAMPClient, self).__init__(url=url, realm=realm)

        self._procedures = {}
        self._topics = {}

    def __getattr__(self, name):
        # implemented to intercept calls to entrypoints which are not
        # found on the wamp Client (as ususal) but instead on the Flask
        # app
        if name in self._procedures:
            return self._procedures[name]

        try:
            return getattr(self.flask_app, name)
        except AttributeError:
            return getattr(self, name)

    def _topic_callback(self, *args, **kwargs):
        message = kwargs['message']
        topic = kwargs['meta']['topic']
        for recognised_topic in self._topics:
            # alternatively could mark providers with subscription IDs?
            if recognised_topic == topic:
                self._topics[recognised_topic](message=message)


class WAMP(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('CROSSBAR_URL', CROSSBAR_DEFAULT)
        app.config.setdefault('WAMP_REALM', DEFAULT_REALM)
        app.teardown_appcontext(self.teardown)
        self.client = FlaskWAMPClient(
            url=app.config['CROSSBAR_URL'],
            realm=app.config['REALM'],
        )

        logger.info('connecting to Crossbar')
        self.client.start()

        app.before_request(self._inject_wampy)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['flask_wamp'] = self
        logger.info('Flask-WAMP initialised for %s', app)

    def _inject_wampy(self):
        if not hasattr(g, 'wanmpy'):
            g.wampy = self.client

    def teardown(self, exception):
        if hasattr(g, 'wampy'):
            logger.warning('tearing down Crossbar connection')
            self.client.stop()
            del g.wampy

    def callee(self, *args, **kwargs):
        def registering_decorator(fn, args, kwargs):
            self.client.session._register_procedure(fn.__name__)
            self.client._procedures[fn.__name__] = fn
            return fn

        return registering_decorator(args[0], args=(), kwargs={})

    def consume(self, *args, **kwargs):
        # whilst i decide on something better
        assert 'topic' in kwargs

        def registering_decorator(fn, args, kwargs):
            self.client.session._subscribe_to_topic(
                self.client._topic_callback, kwargs['topic'],
            )
            self.client._topics[kwargs['topic']] = fn
            return fn

        return partial(registering_decorator, args=args, kwargs=kwargs)
