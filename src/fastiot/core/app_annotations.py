from fastiot.core.subject import Subject


def subscribe(subject: Subject):
    if subject.reply_cls is not None:
        raise ValueError("Expected subject to have no reply_cls for subscription mode")

    def subscribe_wrapper_fn(fn):
        fn._fastiot_subject = subject
        return fn
    return subscribe_wrapper_fn


def reply(subject: Subject):
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
    fn._fastiot_is_loop = True
    return fn
