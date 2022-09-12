"""
This module provides the core functionality for FastIoT Services:
 * Creation of services based on :class:`fastiot.core.service.FastIoTService`
 * Handling of Subjects (Topics) for the broker (:class:`fastiot.core.data_models.Subject`)
 * Adding annotations to subscribe topics on your methods (:meth:`fastiot.core.service_annotations.subscribe`),
   handling requests with a reply (:meth:`fastiot.core.service_annotations.reply`) and run background-tasks
   (:meth:`fastiot.core.service_annotations.loop`)
"""
from fastiot.core.subjects import FastIoTData, Subject, ReplySubject
from fastiot.core.service import FastIoTService
from fastiot.core.service_annotations import subscribe, reply, loop

