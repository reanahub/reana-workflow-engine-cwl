Overview
===============

General description
----------------------------------

``reana-workflow-engine-cwl`` (referred to as ``"engine-cwl"``) acts like a wrapper around
reference CWL implementation `cwltool <https://github.com/common-workflow-language/cwltool>`_.

The implementation of ``engine-cwl`` is based on `cwl-tes <https://github.com/common-workflow-language/cwl-tes>`_ implementation.

The general execution model is the following:

1. A celery task activates the execution by passing the id of the workflow to be started.

2. ``engine-cwl`` extracts the [packed]() workflow description from the database, along with the inputs,
and dumps the information to ``workflow.json`` to contain CWL workflow and ``inputs.json`` with
information about inputs. It expects inputs to be already staged to a working directory

3. Engine-cwl makes call to cwltool's main function with the redefined executor.
It reassigns ``--tmpdir-prefix``, ``--tmp-outdir-prefix`` and later other default cwltool's path variables
( ``docker_outdir``, ``docker_tmpdir``, ``docker_stagedir``) so they are located on the mounted REANA's path (``/data``).
It also uses a default minimal docker image for all workflows because all the jobs have to be executed
in some docker container.

4. During the execution all the output from ``cwltool`` is recorded to a log database. Later these logs
can be parsed to retrieve the produced output (used in ``reana-cwl-runner``).

**Key differences from cwltool's execution model**:

1. All jobs must be executed in a Docker container, thus ``DockerCommandLineJob`` class is highly reused.

2. Only command line is used to create a job, no docker specific options (e.g. bind mounting) can be used.
``ReanaPipelineJob.create_task_msg()`` holds the main logic for adjusting command line for this kind of API.

3. Since jobs are executed on another machines, ``ReanaPipelinePoll`` handles a thread for polling remote job status.


File structure
------------------------

* *celeryapp.py*

registering Celery application - starting point to ``engine-cwl``

* *config.py*

configuration variables for ``engine-cwl``

* *cwl_reana.py*

``ReanaPipeline(Pipeline)`` and ``ReanaPipelinePoll(PollThread)`` classes

* *httpclient.py*

An http client for `reana-job-controller <http://reana-job-controller.readthedocs.io/>`_ API.

* *main.py*

Launching CWL workflow

* *pipeline.py*

Pipeline - adds a few pieces to the default ``cwltool`` executor

* *poll.py*

``PollThread`` - a class for polling job status from ``reana-job-controller``

* *tasks.py*

``run_cwl_workflow`` task is called by another application via Celery to start a CWL workflow - an entry point to ``engine-cwl``
