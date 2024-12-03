# Changelog

## [0.9.4](https://github.com/reanahub/reana-workflow-engine-cwl/compare/0.9.3...0.9.4) (2024-11-29)


### Build

* **docker:** pin setuptools 70 ([#287](https://github.com/reanahub/reana-workflow-engine-cwl/issues/287)) ([3c2cd8a](https://github.com/reanahub/reana-workflow-engine-cwl/commit/3c2cd8a474d167574bf8746b6430f4ae13a83e61))
* **python:** bump shared REANA packages as of 2024-11-28 ([#289](https://github.com/reanahub/reana-workflow-engine-cwl/issues/289)) ([f9d3688](https://github.com/reanahub/reana-workflow-engine-cwl/commit/f9d3688858e6f1ff52fa58fecd9ce233dd97b0e1))


### Features

* **task:** allow Compute4PUNCH backend options ([#277](https://github.com/reanahub/reana-workflow-engine-cwl/issues/277)) ([9b2a3d0](https://github.com/reanahub/reana-workflow-engine-cwl/commit/9b2a3d0872329e79d0b2d9a0972b0c09f08ff694))

## [0.9.3](https://github.com/reanahub/reana-workflow-engine-cwl/compare/0.9.2...0.9.3) (2024-03-04)


### Build

* **docker:** install correct extras of reana-commons submodule ([#261](https://github.com/reanahub/reana-workflow-engine-cwl/issues/261)) ([21957fe](https://github.com/reanahub/reana-workflow-engine-cwl/commit/21957fe41921d9c557067b2773205af6385f755b))
* **docker:** non-editable submodules in "latest" mode ([#255](https://github.com/reanahub/reana-workflow-engine-cwl/issues/255)) ([a6acc88](https://github.com/reanahub/reana-workflow-engine-cwl/commit/a6acc888a36694e3306993cfc3108752b60bd1f3))
* **python:** bump all required packages as of 2024-03-04 ([#267](https://github.com/reanahub/reana-workflow-engine-cwl/issues/267)) ([ed6a846](https://github.com/reanahub/reana-workflow-engine-cwl/commit/ed6a846eb1d8a0bf92f77906749b5853e5794114))
* **python:** bump shared REANA packages as of 2024-03-04 ([#267](https://github.com/reanahub/reana-workflow-engine-cwl/issues/267)) ([47155ef](https://github.com/reanahub/reana-workflow-engine-cwl/commit/47155ef95c4eb19642dd54a732402b2551973658))


### Bug fixes

* **progress:** handle stopped jobs ([#260](https://github.com/reanahub/reana-workflow-engine-cwl/issues/260)) ([bc36cb7](https://github.com/reanahub/reana-workflow-engine-cwl/commit/bc36cb7813a20fde685a40694af0732ded483d3a))


### Code refactoring

* **docs:** move from reST to Markdown ([#263](https://github.com/reanahub/reana-workflow-engine-cwl/issues/263)) ([3cf272f](https://github.com/reanahub/reana-workflow-engine-cwl/commit/3cf272f657cc3e0b329c6d159f5e476f06000f93))


### Continuous integration

* **commitlint:** addition of commit message linter ([#256](https://github.com/reanahub/reana-workflow-engine-cwl/issues/256)) ([021854e](https://github.com/reanahub/reana-workflow-engine-cwl/commit/021854e309999938cf01c31bda5ab095679e03b0))
* **commitlint:** allow release commit style ([#268](https://github.com/reanahub/reana-workflow-engine-cwl/issues/268)) ([ed7ad11](https://github.com/reanahub/reana-workflow-engine-cwl/commit/ed7ad114ccf09ab3182b4cdd49265761f44cd37b))
* **commitlint:** check for the presence of concrete PR number ([#262](https://github.com/reanahub/reana-workflow-engine-cwl/issues/262)) ([9a45817](https://github.com/reanahub/reana-workflow-engine-cwl/commit/9a45817075f98e04405845f0d49cbcd86ee95556))
* **release-please:** initial configuration ([#256](https://github.com/reanahub/reana-workflow-engine-cwl/issues/256)) ([bcd87d1](https://github.com/reanahub/reana-workflow-engine-cwl/commit/bcd87d1bbaa4c9b589e4025989ff880594af2b3d))
* **release-please:** update version in Dockerfile ([#259](https://github.com/reanahub/reana-workflow-engine-cwl/issues/259)) ([0961257](https://github.com/reanahub/reana-workflow-engine-cwl/commit/096125709172e6bea1510a9fd2fdcb90299fac8b))
* **shellcheck:** fix exit code propagation ([#262](https://github.com/reanahub/reana-workflow-engine-cwl/issues/262)) ([6568b9b](https://github.com/reanahub/reana-workflow-engine-cwl/commit/6568b9b229141dd8dd2a261a833057358143590f))


### Documentation

* **authors:** complete list of contributors ([#266](https://github.com/reanahub/reana-workflow-engine-cwl/issues/266)) ([2960cd9](https://github.com/reanahub/reana-workflow-engine-cwl/commit/2960cd9c06a8e12283822ec9fbf87aba7b9b9fb5))
* **conformance-tests:** update CWL conformance test badges ([#264](https://github.com/reanahub/reana-workflow-engine-cwl/issues/264)) ([45afa2e](https://github.com/reanahub/reana-workflow-engine-cwl/commit/45afa2efd984fd84bbae48fde6ca663f70dd86dc))

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
