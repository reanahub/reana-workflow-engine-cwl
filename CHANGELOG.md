# Changelog

## 0.9.2 (2023-12-12)

- Adds automated multi-platform container image building for amd64 and arm64 architectures.
- Adds metadata labels to Dockerfile.
- Fixes container image building on the arm64 architecture.

## 0.9.1 (2023-09-27)

- Fixes container image names to be Podman-compatible.

## 0.9.0 (2023-01-19)

- Adds support for specifying `slurm_partition` and `slurm_time` for Slurm compute backend jobs.
- Adds support for Kerberos authentication for workflow orchestration.
- Adds support for Rucio authentication for workflow jobs.
- Changes the base image of the component to Ubuntu 20.04 LTS and reduces final Docker image size by removing build-time dependencies.
- Fixes status reporting for failed jobs that were incorrectly considered successful.

## 0.8.1 (2022-02-07)

- Adds support for specifying `kubernetes_job_timeout` for Kubernetes compute backend jobs.

## 0.8.0 (2021-11-22)

- Adds support for custom workspace paths.
- Adds supoort for `cwltool` version `3.1.20210628163208`

## 0.7.6 (2021-07-05)

- Changes internal dependencies to remove click.

## 0.7.5 (2021-04-28)

- Adds support for specifying `kubernetes_memory_limit` for Kubernetes compute backend jobs.

## 0.7.4 (2021-03-23)

- Changes job command serialisation using central REANA-Commons job command serialiser.

## 0.7.3 (2021-03-17)

- Changes workflow engine instantiation to use central REANA-Commons factory.
- Changes status `succeeded` to `finished` to use central REANA nomenclature.

## 0.7.2 (2021-02-03)

- Fixes minor code warnings.
- Changes CI system to include Python flake8 and Dockerfile hadolint checkers.

## 0.7.1 (2020-11-10)

- Adds support for specifying `htcondor_max_runtime` and `htcondor_accounting_group` for HTCondor compute backend jobs.
- Fixes restarting of CWL workflows.

## 0.7.0 (2020-10-20)

- Adds pinning of all Python dependencies allowing to easily rebuild component images at later times.
- Adds option to specify unpacked Docker images as workflow step requirement.
- Adds support for handling new workflow operational options.
- Adds support for VOMS proxy as a new authentication method.
- Changes base image to use Python 3.8.
- Changes code formatting to respect `black` coding style.
- Changes documentation to single-page layout.

## 0.6.1 (2020-05-25)

- Upgrades REANA-Commons package using latest Kubernetes Python client version.

## 0.6.0 (2019-12-20)

- Allows to specify compute backend (HTCondor, Kubernetes or Slurm) and
  Kerberos authentication requirement for CWL workflow jobs.
- Upgrades cwltool to 1.0.20191022103248.
- Moves workflow engine to the same Kubernetes pod with the REANA-Job-Controller
  (sidecar pattern).

## 0.5.0 (2019-04-23)

- Makes workflow engine independent of Celery so that independent workflow
  instances are created on demand for each user.
- Replaces `api_client` module with centralised one from REANA-Commons.
- Introduces CVMFS mounts in job specifications.
- Sets default file mode creation mask to 002 so that workflows are able to
  write to shared directories for any user identity under which the workflow
  processes may be running.
- Makes docker image slimmer by using `python:2.7-slim`.
- Centralises log level and log format configuration.
- Upgrades cwltool to 1.0.20181118133959.

## 0.4.0 (2018-11-06)

- Improves AMQP re-connection handling. Switches from `pika` to `kombu`.
- Utilises common openapi client for communication with REANA-Job-Controller.
- Changes license to MIT.

## 0.3.2 (2018-09-25)

- Upgrades to latest `cwltool` (`1.0.20180912090223`).

## 0.3.1 (2018-09-07)

- Pins REANA-Commons dependency.

## 0.3.0 (2018-08-10)

- Tracks progress of workflow runs.

## 0.2.0 (2018-04-19)

- Initial public release.

