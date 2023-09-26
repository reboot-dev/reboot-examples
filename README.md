# Hello world example

<!--
TODO: include a frontend in this example.

TODO: use Docusaurus tools to pull the `shell` snippets from
`tests/readme_test.sh`?

ATTENTION maintainers: for now, if you change the instructions in this file,
also change the matching steps in the CI test that mimics this document:
  `tests/readme_test.sh`.
-->

Goal of this example: demonstrate the simplest possible Resemble application,
without build system.

## Setup

### Prerequisites

You must have the following tools installed:

- Python (including `pip` and `venv`) >= 3.10

### Get this example

TODO: instructions for `git clone`.

```shell
cd resemble-examples/
```

### Create and activate a virtual environment

```shell
python -m venv ./.hello-world-venv
source ./.hello-world-venv/bin/activate
```

### Install Resemble tooling

```shell
pip install reboot-resemble-cli
```

This installs the `rsm` CLI, the Resemble `protoc` plugin, and the
`grpcio-tools` package that provides `protoc`.

## Build

### Install Python requirements

```shell
pip install -r hello-world/backend/src/requirements.txt
```

### Compile protocol buffers

<!--
TODO(benh,zakhar): change the default output directory from `gen/` to `api/`.
-->

```shell
rsm protoc ./api/greeter/greeter.proto
```

## Test

```shell
pytest hello-world/backend/
```

## Run

<!--
TODO(benh,zakhar): auto-detect the PROTOPATH.
TODO(rjh): add appropriate `--watch`es. It seems they may not work as desired right now?
-->

```shell
PYTHONPATH="gen/:hello-world/backend/src" rsm dev --working-directory=. --python hello-world/backend/src/main.py
```

<!--
TODO: introduce an `rsm grpcurl` (or `rsm call` or ...) that lets us explore
our backend in another terminal by calling RPCs.
-->
