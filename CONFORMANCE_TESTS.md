DISCLAIMER: CWL conformance testing on REANA is in progress, please ask for clarifications if things go wrong.

## Instructions


To run CWL conformance tests on REANA follow the next steps:

1) Install and launch REANA according to [instructions](http://reana.readthedocs.io/en/latest/gettingstarted.html)

2) Replace the following REANA components with latest images that support CWL execution:




```
# reana-server
git clone https://github.com/reanahub/reana-server -b reana-cwl-runner
cd reana-cwl-runner
eval $(minikube docker-env)
docker build . -t reana-server:v0.0.1
kubectl get pods
kubectl delete pods <reana-server-container-id>
cd ..
```

```
# reana-workflow-controller
git clone https://github.com/anton-khodak/reana-workflow-controller -b reana-cwl-runner
cd reana-workflow-controller 
eval $(minikube docker-env)
docker build . -t reana-workflow-controller:v0.0.1
minikube ssh
cd /reana/default
curl https://transfer.sh/x0OfE/reana.db --output reana.db
<ctrl-d>
kubectl get pods
kubectl delete pods <reana-workflow-controller-container-id
cd ..
```

```
# reana-workflow-engine-cwl
git clone https://github.com/anton-khodak/reana-workflow-engine-cwl -b reana-cwl-runner
cd reana-workflow-engine-cwl
eval $(minikube docker-env)
docker build . -t reana-workflow-engine-cwl:v0.0.1
cd ..
```

```
# reana-resources-k8s
git clone https://github.com/anton-khodak/reana-resources-k8s -b cwl-support
rm -r configuration-manifests
cp -r reana-resources-k8s/configuration-manifests ./
kubectl create -Rf configuration-manifest
```

 After these steps cwl-default-worker must be visible in `kubectl get pods`


3) Checkout reana-client with reana-cwl-runner interface and start tests




```
# reana-client
git clone https://github.com/anton-khodak/reana-client -b reana-cwl-runner
source reana-virtualenv/bin/activate
cd reana-client
reana get reana-server // here you get reana-server URL
export REANA_SERVER_URL=server_url_from_previous_step
pip install .
cd /path/to/cwltool/cwltool/schemas
./run_test.sh RUNNER=reana-cwl-runner
```

## Warnings:

* currently, sometimes reana-cwl-runner might not process exceptions from the server right, and tests fall in the infinite loop. If the tool takes a suspiciously long time to execute, terminate the execution and relaunch ./run_test.sh with -n option, specifying the order number of a test following to the failing one. However, if a tool runs first the first time, it will always take time to pull the necessary docker images.

* if reana-cwl-runner cannot reach http host of reana-server, check whether you ran `eval $(minikube docker-env)` in
the shell where minikube was launched


## Useful links:

* [development instructions for REANA components](https://github.com/reanahub/reana/issues/16)
