import os


FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT = ">"
FASTIOT_TIME_SERIES_REPLY_SUBJECT = "things"


class TimeSeriesConstants:

    @property
    def subscribe_subject(self) -> str:
        """
        .. envvar:: FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT

        Set the subject to listen to. It defaults to ``>`` meaning everything below ``Thing``.  For more details about
        how to specify (wildcard) subjects please refer to the nats.io documentation at
        https://docs.nats.io/nats-concepts/subjects
        If you want to listen to a specific topic you can change envvar:: FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT
        to you value, but you can only listen to subtopics of Things. So if you want to listen to Thing.machine_1 you
        change envvar:: FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT to "machine_1". It is not possible to listen to "not_Thing.machine1"

        """
        return FASTIOT_TIME_SERIES_SUBSCRIBE_SUBJECT

    @property
    def reply_subject(self) -> str:
        """
        .. envvar:: FASTIOT_TIME_SERIES_REPLY_SUBJECT

        Sets the subject for the reply. It defaults to ``thing``.
        """
        return FASTIOT_TIME_SERIES_REPLY_SUBJECT

time_series_env = TimeSeriesConstants()