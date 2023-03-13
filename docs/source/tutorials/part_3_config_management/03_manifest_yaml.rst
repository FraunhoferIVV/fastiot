.. _tut-manifest:


################################
Service Manifest - manifest.yaml
################################

In the :file:`manifest.yaml` are information about dependencies of the module, ports to open, devices and mounts to bind, ….

This file has to be a valid yaml-file.

You can find the API documentation and thus the whole data model at :mod:`fastiot.cli.model.manifest.ServiceManifest`.

.. code-block:: yaml
   :caption: Example for the absolut minimum manifest.yaml

   fastiot_service:
     name: my_service
