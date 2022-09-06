""" Decorator functions to add the basic functionality to FastIoT Services """
from fastiot.core.data_models import Subject


def subscribe(subject: Subject):
    """
    Decorator method for methods subscribing to a subject. The decorated method must have either one or two arguments:

      - subscribe_something(message: Type[FastIoTData])
      - subscribe_something(subject_name: str, message: Type[FastIoTData])

    See :ref:`publish-subscribe` for more details.

    :param subject: The subject (:class:`fastiot.core.data_models.Subject`) to subscribe.
    """
    if subject.reply_cls is not None:
        raise ValueError("Expected subject to have no reply_cls for subscription mode")

    def subscribe_wrapper_fn(fn):
        fn._fastiot_subject = subject
        return fn
    return subscribe_wrapper_fn


def reply(subject: Subject):
    """
    Decorator for methods replying on the specified subject. This works similiar to
    :meth:`fastiot.core.service_annotations.subscribe` but you have to return a ``Type[FastIoTData]`` as a reply
    message.

    Please be aware, that your subject is expected to have the parameter ``reply_cls`` set.

    :param subject: The subject to subscribe to for sending replies
    """
    if subject.reply_cls is None:
        raise ValueError("Expected subject to have a reply_cls for reply mode")
    if subject.stream_mode:
        raise ValueError("Expected subject to have stream mode disabled for reply mode")

    def subscribe_wrapper_fn(fn):
        fn._fastiot_subject = subject
        return fn
    return subscribe_wrapper_fn


def stream(subject: Subject):
    if subject.reply_cls is None:
        raise ValueError("Expected subject to have a reply_cls for stream mode")
    if subject.stream_mode is False:
        raise ValueError("Expected subject to have stream mode enabled for stream mode")

    def subscribe_wrapper_fn(fn):
        fn._fastiot_subject = subject
        return fn

    return subscribe_wrapper_fn


def loop(fn):
    """
    Decorator function for methods to run continuously. This will basically create a "while True loop" that is stopped
    once the service is stopped.

    Your method needs to return an awaitable function. This is usually done like ``return asyncio.sleep(1)`` resulting
    in waiting for one second after the loop. It is strongly recommended to return some wait time for other tasks within
    the asyncio event queue to be run.
    """
    fn._fastiot_is_loop = True
    return fn
