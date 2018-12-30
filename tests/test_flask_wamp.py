import datetime

import pytest
import six
from flask import g, jsonify, Flask
from wampy.backends import async_adapter
from wampy.constants import DEFAULT_REALM
from wampy.peers.clients import Client
from wampy.roles.callee import callee
from wampy.roles.subscriber import subscribe
from wampy.testing.helpers import (
    assert_stops_raising,
    wait_for_registrations, wait_for_subscriptions
)


from flask_wamp import WAMP


class DateService(Client):

    @callee
    def get_todays_date(self):
        return datetime.date.today().isoformat()


class SpamService(Client):

    call_count = 0

    @subscribe(topic="spam")
    def foo_topic_handler(self, *args, **kwargs):
        self.call_count += 1


@pytest.fixture
def date_service(router):
    with DateService(url=router.url) as client:
        wait_for_registrations(client, 1)
        yield


@pytest.fixture
def spam_subscriber(router):
    client = SpamService(router=router)
    with client:
        wait_for_subscriptions(client, 1)
        yield client


@pytest.fixture
def collector():
    return []


def create_app(collector=None):
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        ROUTER_URL="ws://localhost:8080",
        REALM=DEFAULT_REALM,
    )

    wamp_app = WAMP(app)

    @app.route('/hello')
    @wamp_app.callee
    def hello():
        return 'Hello, World!'

    @app.route('/goodbye')
    @wamp_app.callee
    def goodbye():
        return 'Goodbye, World!'

    @wamp_app.consume(topic="foo")
    def foo_eater(message):
        collector.append(message)

    @app.route('/get_spam')
    def get_collected_spam():
        return jsonify(collector)

    @wamp_app.consume(topic="spam")
    def spam_eater(message):
        collector.append(message)

    @app.route('/todays_date')
    def get_date(*args, **kwargs):
        wampy = g.wampy
        return wampy.rpc.get_todays_date()

    @app.route('/publish_spam')
    def publish_spam(*args, **kwargs):
        wampy = g.wampy
        wampy.publish(topic="spam", message="tastes nice!")
        return ''

    return app


@pytest.fixture
def app(router, collector, date_service):
    app = create_app(collector=collector)
    wamp_app = app.extensions['flask_wamp']

    wait_for_subscriptions(wamp_app.client, 2)
    wait_for_registrations(wamp_app.client, 2)

    return app


def test_register_callees(app):
    with Client(url=app.config['CROSSBAR_URL']) as wampy:
        assert wampy.rpc.hello() == 'Hello, World!'
        assert wampy.rpc.goodbye() == 'Goodbye, World!'


def test_can_register_callees_as_flask_routes(app):
    client = app.test_client()

    assert client.get('/hello').data == b'Hello, World!'
    assert client.get('/goodbye').data == b'Goodbye, World!'


def test_register_topics(app, collector):
    assert collector == []

    with Client(url=app.config['CROSSBAR_URL']) as wampy:
        wampy.publish(topic="foo", message="foobar")
        wampy.publish(topic="spam", message="ham")

    assert "foobar" in collector
    assert "ham" in collector


def test_rpc_from_flask_app(app):
    client = app.test_client()

    date_str = client.get('/todays_date').data
    today = datetime.date.today().isoformat()

    assert date_str == six.b(today)


def test_publish_from_flask_app(app, spam_subscriber):
    client = app.test_client()
    client.get('/publish_spam')

    def test_call_count():
        assert spam_subscriber.call_count == 1

    assert_stops_raising(test_call_count)
