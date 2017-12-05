DISCLAIMER: CWL conformance testing on REANA is in progress, please ask for clarifications if things go wrong.

## Instructions


To run CWL conformance tests on REANA follow the next steps:

1) Install and launch REANA according to [instructions](http://reana.readthedocs.io/en/latest/gettingstarted.html)

2) Replace the following REANA components with latest images that support CWL execution:




* reana-server

```
    1. git clone https://github.com/reanahub/reana-server
    2. git checkout reana-cwl-runner
    3. eval $(minikube docker-env)
    4. docker build . -t reana-server:v0.0.1
    5. kubectl get pods
    6. kubectl delete pods <reana-server-container-id>

 ```

* reana-workflow-controller

```

    1. git clone https://github.com/anton-khodak/reana-workflow-controller
    2. git checkout reana-cwl-runner
    3. eval $(minikube docker-env)
    4. docker build . -t reana-workflow-controller:v0.0.1
    5. minikube ssh
    6. cd /reana/default
    7. curl https://transfer.sh/x0OfE/reana.db --output reana.db
    8. kubectl get pods
    9. kubectl delete pods <reana-workflow-controller-container-id

```

* reana-workflow-engine-cwl

```
    1. git clone https://github.com/anton-khodak/reana-workflow-engine-cwl
    2. git checkout reana-cwl-runner
    3. eval $(minikube docker-env)
    4. docker build . -t reana-workflow-engine-cwl:v0.0.1
```


* reana-resources-k8s

   ```
    1. git clone https://github.com/anton-khodak/reana-resources-k8s
    2. git checkout cwl-support
    3. cd /path/to/reana-installation
    4. rm -r configuration-manifests
    5. cp /path/to/anton-khodak/reana-resources-k8s/configuration-manifests .
    6. kubectl create -Rf configuration-manifests
    ```

 After these steps cwl-default-worker must be visible in `kubectl get pods`


3) Checkout reana-client with reana-cwl-runner interface and start tests


    * reana-client

```
    1. git clone https://github.com/anton-khodak/reana-client
    2. git checkout reana-cwl-runner
    3. source /path/to/reana-virtualenv/bin/activate
    4. reana get reana-server // here you get reana-server URL
    5. export REANA_SERVER_URL=server_url_from_previous_step
    6. python setup.py install
    7. cd /path/to/cwltool/cwltool/schemas
    8. ./run_test.sh RUNNER=reana-cwl-runner
```

## Warnings:

* currently, sometimes reana-cwl-runner might not process exceptions from the server right, and tests fall in the infinite loop. If the tool takes a suspiciously long time to execute, terminate the execution and relaunch ./run_test.sh with -n option, specifying the order number of a test following to the failing one. However, if a tool runs first the first time, it will always take time to pull the necessary docker images.

* if reana-cwl-runner cannot reach http host of reana-server, check whether you ran `eval $(minikube docker-env)` in
the shell where minikube was launched


## Useful links:

* [development instructions for REANA components](https://github.com/reanahub/reana/issues/16)
