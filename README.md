# Resemble Examples

<!--
TODO: include a frontend in this example.
-->

This repository contains example applications written using Resemble. The
examples are structured in the style of a monorepo: all proto files can be found
in the `api/` directory, grouped into subdirectories by proto package, while application code is broken into top-level directories by
application name.

For example, the `hello-world` application uses code from `hello-world/` and
protos from `api/hello-world/`.

## Setup

<!-- TODO: Update the Quick Start link below once the Resemble docs are published with a more official address. -->

Before running examples from this repository, follow the [Installation
section](https://vigilant-adventure-g31v411.pages.github.io/docs/quick-start#installation)
of the Resemble "Quick Start" guide to set up general Resemble requirements.

## Run an Example

These steps will walk you through the process of downloading and running
examples from this repository locally on your machine.

### Clone Repository

<!-- TODO: fetch this snippet from a test. -->

To get started with these examples, clone this repository:

```shell
git clone https://github.com/reboot-dev/resemble-examples.git
cd resemble-examples/
```

### Install Python Requirements

As with most Python applications, these examples have requirements that must be
installed before the application code can run successfully. These Python
requirements include the Resemble backend library, `reboot-resemble`.

Requirements are specific to a particular example application. The following
command will install requirements for the `HelloWorld` application.

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=52-52) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
pip install -r hello-world/backend/src/requirements.txt
```
<!-- MARKDOWN-AUTO-DOCS:END -->

### Compile Protocol Buffers

Run the Resemble `protoc` plugin to generate Resemble code based on the protobuf
definition of a service. The following command will generate code for the
`HelloWorld` application, whose sole service is defined in `greeter.proto`:

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=55-55) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
rsm protoc ./api/hello_world/v1/greeter.proto
```
<!-- MARKDOWN-AUTO-DOCS:END -->

The `rsm` tool will automatically pull in required Resemble proto dependencies
like `resemble/v1alpha1/options.proto`, even though they're not found in this
repository.

<!-- TODO: link to the Resemble proto definitions once they are publicly available. -->

## Test

The example code comes with example tests. To run the example tests, use  `pytest`:

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=58-58) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
pytest hello-world/backend/
```
<!-- MARKDOWN-AUTO-DOCS:END -->

## Run

To start an application, use the `rsm` CLI. The following command starts the
`HelloWorld` example.

<!--
TODO: include this command in readme_test.sh.
-->

<!--
TODO(benh,zakhar): auto-detect the PROTOPATH.
TODO(rjh): add appropriate `--watch`es. It seems they may not work as desired right now?
-->

```shell
rsm dev --env=PYTHONPATH=gen/ --working-directory=. --python hello-world/backend/src/main.py
```

The PYTHONPATH must be explicitly set to pick up both the generated Resemble
code and the application code.

`rsm dev` will then run the Python script specified by the
`--python` flag from the directory specified by the `--working-directory` flag.

The tool will automatically watch the given python script for changes. If there
are changes, it will restart the running application to reflect the update.

<!--
TODO: introduce an `rsm grpcurl` (or `rsm call` or ...) that lets us explore
our backend in another terminal by calling RPCs.
-->
