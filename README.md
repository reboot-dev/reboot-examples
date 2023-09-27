# Hello world example

<!--
TODO: include a frontend in this example.
-->

This repository contains example applications written using Resemble. The
examples are structured in the style of a monorepo: all proto files can be found
in the `api/` directory, while application code is broken into subdirectories by
application name.

For example, the `hello-world` application uses code from `hello-world/` and
protos from `api/hello-world/`.

## Setup

Before setting up this example, follow the [Resemble Quick Start
guide](../documentation/docs/quick-start.md) to set up general Resemble
requirements.

### Get this example

<!-- TODO: fetch this snippet from a test. -->

```shell
git clone https://github.com/reboot-dev/resemble-examples.git
cd resemble-examples/
```

### Install Python requirements

The Python requirements for this example include the Resemble backend library, `reboot-resemble`.

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=52-52) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
pip install -r hello-world/backend/src/requirements.txt
```
<!-- MARKDOWN-AUTO-DOCS:END -->

### Compile protocol buffers

Run the Resemble `protoc` plugin to generate Resemble code for the example
service:

<!--
TODO(benh,zakhar): change the default output directory from `gen/` to `api/`.
-->

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=55-55) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
rsm protoc ./api/hello_world/v1/greeter.proto
```
<!-- MARKDOWN-AUTO-DOCS:END -->

## Test

Run example tests with `pytest`:

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=58-58) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
pytest hello-world/backend/
```
<!-- MARKDOWN-AUTO-DOCS:END -->

## Run

Start the example using the `rsm` CLI:

<!--
TODO: include this command in readme_test.sh.
-->

<!--
TODO(benh,zakhar): auto-detect the PROTOPATH.
TODO(rjh): add appropriate `--watch`es. It seems they may not work as desired right now?
-->

<!-- TODO: what does the --working-directory flag do here? -->

```shell
PYTHONPATH="gen/:hello-world/backend/src" rsm dev --working-directory=. --python hello-world/backend/src/main.py
```

<!--
TODO: introduce an `rsm grpcurl` (or `rsm call` or ...) that lets us explore
our backend in another terminal by calling RPCs.
-->
