.. _developerguide:

Developer guide
===============

Running locally
---------------

1. Create Python virtual environment and install ``reana-workflow-engine-cwl``

.. code-block:: console

   $ git clone https://github.com/reanahub/reana-workflow-engine-cwl.git
   $ virtualenv ~/.virtualenvs/engine-cwl
   $ source ~/.virtualenvs/engine-cwl/bin/activate
   $ cd reana-workflow-engine-cwl
   $ pip install .


2. Install `RabbitMQ <https://www.rabbitmq.com/download.html>`_

3. Create RabbitMQ user, group and host and start RabbitMQ:

.. code-block:: console

   $ rabbitmqctl add_user reana reana
   $ rabbitmqctl add_vhost reanahost
   $ rabbitmqctl set_permissions -p reanahost reana “.*” “.*” “.*”
   $ rabbitmq-server start -detached


3. Get ``reana-job-controller`` URL with `reana-cluster <http://reana-cluster.readthedocs.io/en/latest/cliapi.html>`_ component.

.. code-block:: console

   $ source /path/to/reana-cluster-virtual-environment
   $ reana-cluster get reana-job-controller
   internal_ip: None
   ports: ['31060']
   external_ip_s: ['192.168.99.100']
   external_name: None

and set environmental variables (use your own values for ``SHARED_VOLUME_PATH`` and ``JOB_CONTROLLER_HOST``).

.. code-block:: console

   $ export JOB_CONTROLLER_HOST=http://192.168.99.100:31060
   $ export SHARED_VOLUME_PATH=/reana/default
   $ export RABBIT_MQ=amqp://reana:reana@localhost:5672/reanahost

4. Start ``reana-workflow-engine-cwl``

.. code-block:: console

   $ run-cwl-workflow --workflow-uuid [id]
                      --workflow-workspace [workspace]
                      --workflow-json [workflow_json]
                      --workflow-parameters [parameters]
                      --operational-options [options]


Running CWL conformance tests
-----------------------------

To run CWL conformance tests on a locally-installed REANA cluster:

1. Install REANA cluster (version v0.2.0 or later) on Minikube. See
   `REANA-Cluster's Getting started guide
   <http://reana-cluster.readthedocs.io/en/latest/gettingstarted.html>`_ for
   more information.

2. Install REANA client (version v0.2.0 or later) locally. See `REANA-Client's
   Getting started guide
   <https://reana-client.readthedocs.io/en/latest/gettingstarted.html>`_ for
   more information.

3. Set your environment variables:

.. code-block:: console

   $ eval $(reana-cluster env)

4. Download and run the CWL conformance tests:

.. code-block:: console

   $ git clone https://github.com/common-workflow-language/common-workflow-language
   $ cd common-workflow-language
   $ pip install cwltest
   $ ./run_test.sh RUNNER=reana-cwl-runner
