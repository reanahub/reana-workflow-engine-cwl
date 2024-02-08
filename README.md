# REANA-Workflow-Engine-CWL

[![image](https://github.com/reanahub/reana-workflow-engine-cwl/workflows/CI/badge.svg)](https://github.com/reanahub/reana-workflow-engine-cwl/actions)
[![image](https://readthedocs.org/projects/reana-workflow-engine-cwl/badge/?version=latest)](https://reana-workflow-engine-cwl.readthedocs.io/en/latest/?badge=latest)
[![image](https://codecov.io/gh/reanahub/reana-workflow-engine-cwl/branch/master/graph/badge.svg)](https://codecov.io/gh/reanahub/reana-workflow-engine-cwl)
[![image](https://img.shields.io/badge/discourse-forum-blue.svg)](https://forum.reana.io)
[![image](https://img.shields.io/github/license/reanahub/reana-workflow-engine-cwl.svg)](https://github.com/reanahub/reana-workflow-engine-cwl/blob/master/LICENSE)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## About

REANA-Workflow-Engine-CWL is a component of the [REANA](http://www.reana.io/) reusable
and reproducible research data analysis platform. It takes care of instantiating,
executing and managing [Common Workflow Language (CWL)](http://www.commonwl.org/) based
computational workflows.

## Features

- start Common Workflow Language (CWL) based workflows
- control workflow steps

## Usage

The detailed information on how to install and use REANA can be found in
[docs.reana.io](https://docs.reana.io).

## Useful links

- [REANA project home page](http://www.reana.io/)
- [REANA user documentation](https://docs.reana.io)
- [REANA user support forum](https://forum.reana.io)
- [REANA-Workflow-Engine-CWL releases](https://reana-workflow-engine-cwl.readthedocs.io/en/latest#changes)
- [REANA-Workflow-Engine-CWL docker images](https://hub.docker.com/r/reanahub/reana-workflow-engine-cwl)
- [REANA-Workflow-Engine-CWL developer documentation](https://reana-workflow-engine-cwl.readthedocs.io/)
- [REANA-Workflow-Engine-CWL known issues](https://github.com/reanahub/reana-workflow-engine-cwl/issues)
- [REANA-Workflow-Engine-CWL source code](https://github.com/reanahub/reana-workflow-engine-cwl)

## CWL conformance tests

REANA 0.9.2 tested on 2024-02-07

### CWL v1.0

[List of failed tests](https://docs.reana.io/running-workflows/supported-systems/cwl/#cwl-v10-specification-conformance-results)

#### Classes

[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/command_line_tool.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/expression_tool.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/workflow.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)

#### Required features

[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/required.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)

#### Optional features

[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/docker.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/env_var.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/initial_work_dir.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/inline_javascript.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/multiple_input.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/resource.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/scatter.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/schema_def.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/shell_command.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/step_input_expression.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/step_input.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.0/subworkflow.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)

### CWL v1.1

[List of failed tests](https://docs.reana.io/running-workflows/supported-systems/cwl/#cwl-v11-specification-conformance-results)

#### Classes

[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/command_line_tool.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/expression_tool.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/workflow.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)

#### Required features

[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/required.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)

#### Optional features

[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/docker.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/env_var.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/format_checking.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/initial_work_dir.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/inline_javascript.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/inplace_update.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/input_object_requirements.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/multiple_input.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/networkaccess.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/resource.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/scatter.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/schema_def.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/shell_command.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/step_input_expression.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/step_input.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/subworkflow.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.1/timelimit.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)

### CWL v1.2

[List of failed tests](https://docs.reana.io/running-workflows/supported-systems/cwl/#cwl-v12-specification-conformance-results)

#### Classes

[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/command_line_tool.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/expression_tool.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/workflow.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)

#### Required features

[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/required.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)

#### Optional features

[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/conditional.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/docker.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/env_var.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/format_checking.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/initial_work_dir.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/inline_javascript.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/inplace_update.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/input_object_requirements.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/multiple_input.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/multiple.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/networkaccess.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/resource.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/scatter.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/schema_def.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/secondary_files.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/shell_command.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/step_input_expression.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/step_input.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/subworkflow.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
[![image](https://badgen.net/https/raw.githubusercontent.com/reanahub/reana-workflow-engine-cwl/master/badges/v1.2/timelimit.json?icon=commonwl)](https://github.com/reanahub/reana-workflow-engine-cwl)
