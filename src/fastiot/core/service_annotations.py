""" Decorator functions to add the basic functionality to FastIoT Services """
import asyncio

from fastiot.core.data_models import Subject, ReplySubject


def subscribe(subject: Subject):
    """
    Decorator method for methods subscribing to a subject. The decorated method must have either one or two arguments:

      - subscribe_something(message: Type[FastIoTData])
      - subscribe_something(subject_name: str, message: Type[FastIoTData])

    See :ref:`publish-subscribe` for more details.

    :param subject: The subject (:class:`fastiot.core.data_models.Subject`) to subscribe.
    """
    def subscribe_wrapper_fn(fn):
        if not asyncio.iscoroutinefunction(fn):
            raise TypeError("Expected coroutine function for subscribe annotation")
        fn._fastiot_subject = subject
        return fn
    return subscribe_wrapper_fn


def reply(subject: ReplySubject):
    """
    Decorator for methods replying on the specified subject. This works similiar to
    :meth:`fastiot.core.service_annotations.subscribe` but you have to return a ``Msg`` as a reply
    message.

    :param subject: The subject to subscribe to for sending replies
    """
    def subscribe_wrapper_fn(fn):
        if not asyncio.iscoroutinefunction(fn):
            raise TypeError("Expected coroutine function for reply annotation")
        fn._fastiot_reply_subject = subject
        return fn
    return subscribe_wrapper_fn


def loop(fn):
    """
    Decorator function for methods to run continuously. This will basically create a "while True loop" wrapper around
    the provided function. This is purely syntactic suggar for run_task.

    Your method needs to return an awaitable that is awaited after each loop execution before the next iteration.
    However, the returned awaitable does not finish if a service shutdown is requested. It uses ``self.run_coro`` under
    the hood. But it is guaranteed, that the annotated loop function is awaited and not interrupted if a shutdown is
    requested.

    Example:
        @loop
        async def log_still_running(self):
            logging.info("Service is still running.")
            return asyncio.sleep(10.0)
    """
    if not asyncio.iscoroutinefunction(fn):
        raise TypeError("Expected coroutine function for loop annotation")
    fn._fastiot_is_loop = True
    return fn
