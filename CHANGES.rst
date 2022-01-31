Changes
=======

Version 0.8.1 (2022-02-07)
---------------------------

- Adds support for specifying ``kubernetes_job_timeout`` for Kubernetes compute backend jobs.

Version 0.8.0 (2021-11-22)
--------------------------

- Adds support for custom workspace paths.
- Adds supoort for ``cwltool`` version ``3.1.20210628163208``

Version 0.7.6 (2021-07-05)
--------------------------

- Changes internal dependencies to remove click.

Version 0.7.5 (2021-04-28)
--------------------------

- Adds support for specifying ``kubernetes_memory_limit`` for Kubernetes compute backend jobs.

Version 0.7.4 (2021-03-23)
--------------------------

- Changes job command serialisation using central REANA-Commons job command serialiser.

Version 0.7.3 (2021-03-17)
--------------------------

- Changes workflow engine instantiation to use central REANA-Commons factory.
- Changes status ``succeeded`` to ``finished`` to use central REANA nomenclature.

Version 0.7.2 (2021-02-03)
--------------------------

- Fixes minor code warnings.
- Changes CI system to include Python flake8 and Dockerfile hadolint checkers.

Version 0.7.1 (2020-11-10)
--------------------------

- Adds support for specifying ``htcondor_max_runtime`` and ``htcondor_accounting_group`` for HTCondor compute backend jobs.
- Fixes restarting of CWL workflows.

Version 0.7.0 (2020-10-20)
--------------------------

- Adds pinning of all Python dependencies allowing to easily rebuild component images at later times.
- Adds option to specify unpacked Docker images as workflow step requirement.
- Adds support for handling new workflow operational options.
- Adds support for VOMS proxy as a new authentication method.
- Changes base image to use Python 3.8.
- Changes code formatting to respect ``black`` coding style.
- Changes documentation to single-page layout.

Version 0.6.1 (2020-05-25)
--------------------------

- Upgrades REANA-Commons package using latest Kubernetes Python client version.

Version 0.6.0 (2019-12-20)
--------------------------

- Allows to specify compute backend (HTCondor, Kubernetes or Slurm) and
  Kerberos authentication requirement for CWL workflow jobs.
- Upgrades cwltool to 1.0.20191022103248.
- Moves workflow engine to the same Kubernetes pod with the REANA-Job-Controller
  (sidecar pattern).

Version 0.5.0 (2019-04-23)
--------------------------

- Makes workflow engine independent of Celery so that independent workflow
  instances are created on demand for each user.
- Replaces ``api_client`` module with centralised one from REANA-Commons.
- Introduces CVMFS mounts in job specifications.
- Sets default file mode creation mask to 002 so that workflows are able to
  write to shared directories for any user identity under which the workflow
  processes may be running.
- Makes docker image slimmer by using ``python:2.7-slim``.
- Centralises log level and log format configuration.
- Upgrades cwltool to 1.0.20181118133959.

Version 0.4.0 (2018-11-06)
--------------------------

- Improves AMQP re-connection handling. Switches from ``pika`` to ``kombu``.
- Utilises common openapi client for communication with REANA-Job-Controller.
- Changes license to MIT.

Version 0.3.2 (2018-09-25)
--------------------------

- Upgrades to latest ``cwltool`` (``1.0.20180912090223``).

Version 0.3.1 (2018-09-07)
--------------------------

- Pins REANA-Commons dependency.

Version 0.3.0 (2018-08-10)
--------------------------

- Tracks progress of workflow runs.

Version 0.2.0 (2018-04-19)
--------------------------

- Initial public release.

.. admonition:: Please beware

   Please note that REANA is in an early alpha stage of its development. The
   developer preview releases are meant for early adopters and testers. Please
   don't rely on released versions for any production purposes yet.
