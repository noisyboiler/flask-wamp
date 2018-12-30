flask-wamp
~~~~~~~~~~

Flask apps with `WAMP`_ messaging.

For a background as to what WAMP is, please see `here`_.

Remember, The Web Application Messaging Protocl is not *just* for the Web. So, if you would like your Flask app to be a WAMP component in a larger architecture... then you can! flask-wamp gives you two options:

1. rRPC or PubSub messaging between Flask Apps, supporting a micro-service architecture for the backend
2. rRPC or PubSub messaging between your Browser and Flask Apps, supporting async, concurrent calls and real-time updates for the frontend users

For both you'll need a WAMP Router/Broker Peer, and for that I recommend `Crossbar.io`_.

Use Cases
---------

- Realtime updates between Browsers (I suggest `wampy.js`_) and Flask Apps
- Upgrading the power of existing Flask micro-services

Why Not Just WebSockets?
------------------------

WebSockets are of course a sound implementation for real-time client-server communication. You'll need some Flask Middleware for this, such as `Flask-SocketIO`_, or `flask-sockets`_. With WAMP, you do not.

You might then struggle to find a mature WebSocket RPC between your components, and even if you do, each component will need to know the other exists and exacrtly the host, port and path to find it on - with WAMP you do not.

With WAMP you also have consistency in technology between front end and back, and inter-communication between backend components.

The only real hurdle you'll face is getting Crossbar.io up and running with sensible configuration, but there are great support `docs`_ for this and the basic usecase for demos and early development is trivial. And this Router/Broker Peer is a compelling reason to choose WAMP as it has sophisticaed messaging patterns and advanced features such as authN/Z and meta events. Regarding the client Peers, `wampy.js`_ and flask-wamp make this incredibly straight forward.

Another reason you might want to consider flask-wamp for your Flask Messaging is that under the hood it uses *wampy*, and wampy can be configured to use either `eventlet`_ or `Gevent`_, so if your architecture is already tied to one of these, flask-wamp can use the async networking solution of your choice.

WAMP in general has desirable features that you'd get out-of-the-box, such as load balancing and a variety of auth patterns.

How It Works
------------

This is a standard Flask Extension.

Under the hood you have a single `wampy`_ client instance with a WAMP WebSocket connection to Crossbar. So for every instance of your Flask App you have, you also have a single instance of wampy. You must wrap your Flask App in the flask-wamp App to achieve this, providing the Router host and Realm name. This should come from your Flask Config object - see `test_flask_wamp.py`_ for an example.

Then, much like with `nameko-wamp`_, you can declare a Flask endpoint/view to fulfill the WAMP Callee or Subscriber Role. This is doesn't stop you also routing HTTP requests to these views - bargain!

Once you've done this it can be communicated with over the WAMP protocol by any other WAMP Caller or Publisher component, whether this is another Flask App or a Browser, and assuming they are all attached to the same Realm. Declarations are done with *decorators*. What these "views" then do under the decoration is entirelly up to you.

For a Flask Peer to fulfill a Caller or Publisher Role you need a handle on that **wampy** instance and the API it provides. Again, just like `nameko-wamp`_, we use Dependency Injection so all your views have access to wampy via the `g` object. For example,

.. code-block:: python

        from flask import g

        def my_view_function():
            wampy = g.wampy
            wampy.rpc.some_remote_procedure(*args, **kwargs)
            wampy.publish(topic="some topic", message="this is fun!")

            # maybe do other stuff and return something

Every view will have access to wampy, whether it is a decorated view or not. Wampy is already connected to Crossbar so you do *not* need to use it as a context manager as the `wampy`_ docs suggest. See `ReadTheDocs`_ for more on wampy's API.

Running the tests
~~~~~~~~~~~~~~~~~

The test runner uses the Crossbar test fixture provided by wampy.

::

    $ pip install --editable .[dev]
    $ py.test ./test -v


.. _Crossbar.io: http://crossbar.io/docs/Quick-Start/
.. _docs: https://crossbar.io/docs/
.. _nameko-wamp: https://github.com/noisyboiler/nameko-wamp
.. _Flask-SocketIO: https://github.com/miguelgrinberg/Flask-SocketIO/
.. _flask-sockets: https://github.com/heroku-python/flask-sockets
.. _wampy.js: https://github.com/KSDaemon/wampy.js/
.. _WAMP Protocol: http://wamp-proto.org/
.. _WAMP: http://wamp-proto.org/
.. _here: https://medium.com/@noisyboiler/the-web-application-messaging-protocol-d8efe95aeb67
.. _ReadTheDocs: http://wampy.readthedocs.io/en/latest/
.. _Gevent: http://www.gevent.org/
.. _eventlet: http://eventlet.net/
.. _wampy: https://github.com/noisyboiler/wampy
.. _test_flask_wamp.py: https://github.com/noisyboiler/flask-wamp/blob/master/tests/test_flask_wamp.py
