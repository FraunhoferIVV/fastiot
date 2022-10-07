import os


FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT = "FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT"
FASTIOT_TIME_SERIES_REQUEST_SUBJECT = "FASTIOT_TIME_SERIES_REQUEST_SUBJECT"


class TimeSeriesConstants:

    @property
    def subscribe_subject(self) -> str:
        """
        .. envvar:: FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT

        Set the subject to listen to. It defaults to ``>`` meaning everything below ``Thing``.  For more details about
        how to specify (wildcard) subjects please refer to the nats.io documentation at
        https://docs.nats.io/nats-concepts/subjects
        If you want to listen to a specific topic you can change :envvar:`FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT`
        to your value, but you can only listen to subtopics of Things. So if you want to listen to Thing.machine_1 you
        change :envvar:`FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT` to "machine_1". It is not possible to listen to
        "not_Thing.machine1"
        """
        return os.environ.get(FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT, ">")

    @property
    def request_subject(self) -> str:
        """
        .. envvar:: FASTIOT_TIME_SERIES_REPLY_SUBJECT

        Sets the subject the time series module will listen on for requests with
        :class:`fastiot.msg.hist.HistObjectReq`. It defaults to ``things``.

        If you have only one time series storage this default should be fine for you. Using this is especially
        helpfully when running multiple time series storages listening on different subjects defined with
        :envvar:`FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT`.
        """
        return os.environ.get(FASTIOT_TIME_SERIES_REQUEST_SUBJECT, "things")


time_series_env = TimeSeriesConstants()
