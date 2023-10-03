# Resemble Examples

<!--
TODO: include a frontend in this example.
-->

For the impatient:
1. Get a suitable environment:
    * [Use a GitHub Codespace](#use-a-github-codespace)
    * [Use VSCode](#use-vscode)
    * [Use a Docker container](#use-a-docker-container)
    * [Install prerequisites manually](#install-prerequisites-manually)
2. [Run an example](#run-an-example)

### Overview

This repository contains example applications written using Resemble. The
examples are structured in the style of a monorepo: all proto files can be found
in the `api/` directory, grouped into subdirectories by proto package, while application code is broken into top-level directories by
application name.

For example, the `hello-constructors` application uses code from `hello-constructors/` and
protos from `api/hello_constructors/`.

This README will walk you through the process of downloading and running
examples from this repository locally on your machine.

<a id="use-a-github-codespace"></a>
## Use a GitHub Codespace

GitHub's Codespaces are [Dev Containers](https://containers.dev/) that
get hosted for you in the cloud.

> [!NOTE]
> The Dev Container's configuration is found in
> [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json). You
> may expand on it to customize your development environment to your
> liking.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/reboot-dev/resemble-examples)
<br>
(Right-Click to open in new tab or window)

Now you're ready to [Run an example](#run-an-example)!

<a id="use-vscode"></a>
## Use VSCode

> [!IMPORTANT]
> Currently, our Dev Container at
> [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json)
> only works on x86 CPU architectures. <br>
> **Apple-silicon (M1/M2/...) Mac users**: we will be providing support for your machines soon!

VSCode has built-in support for Dev Containers.

Clone this repository:

<!-- TODO: fetch this snippet from a test. -->

```shell
git clone https://github.com/reboot-dev/resemble-examples.git
```

Open the Dev Container:

- In VSCode, open the `resemble-examples` folder you've cloned.
- Press: Ctrl+Shift+P (Linux / Windows) or Command+Shift+P (Mac)
- Type/Select: `Dev Containers: Reopen In Container`

VSCode will now start the Dev Container, and restart VSCode to be running
inside of that container.

Now you're ready to [Run an example](#run-an-example)!

<a id="use-a-docker-container"></a>
## Use a Docker container

COMING SOON!

<a id="install-prerequisites-manually"></a>
## Install prerequisites manually

> [!IMPORTANT]
> Currently, Resemble backends can only run on x86 Linux machines with
> `glibc>=2.35` (Ubuntu Jammy and other equivalent-generation Linux
> distributions). If you have a machine that doesn't fit this requirement, we
> suggest using one of the Dev Container approaches discussed above.

### Prerequisites

You must have the following tools installed:

- Python (including `pip` and `venv`) >= 3.10

### Clone Repository

Clone this repository:

<!-- TODO: fetch this snippet from a test. -->

```shell
git clone https://github.com/reboot-dev/resemble-examples.git
cd resemble-examples/
```

### Create and activate a virtual environment

Create a new Python virtual environment in which to install Resemble
requirements and run an application:

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=32-33) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
python -m venv ./.resemble-examples-venv
source ./.resemble-examples-venv/bin/activate
```
<!-- MARKDOWN-AUTO-DOCS:END -->

For extra environment isolation, you can make a virtual environment for each
application you want to run.

To learn more about why virtual environments are a best practice for Python
projects, see [the Python documentation for the `venv` module.](https://docs.python.org/3/library/venv.html)

### Install Resemble tooling

Install the Resemble command line tool (`rsm`) via `pip`. This package includes
the `rsm` CLI, the Resemble `protoc` plugin, the proto dependencies required for
Resemble definitions, and the `grpcio-tools` package that provides `protoc`.

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=39-39) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
pip install reboot-resemble-cli
```
<!-- MARKDOWN-AUTO-DOCS:END -->

Now you're ready to [Run an example](#run-an-example)!

<a id="run-an-example"></a>
## Run an Example

### Install Python Requirements

As with most Python applications, these examples have requirements that must be
installed before the application code can run successfully. These Python
requirements include the Resemble backend library, `reboot-resemble`.

Requirements are specific to a particular example application. The following
command will install requirements for the `hello-constructors` example.

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=52-52) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
pip install -r hello-constructors/backend/src/requirements.txt
```
<!-- MARKDOWN-AUTO-DOCS:END -->

### `rsm dev`

To run an example, use the `rsm` CLI. The following command starts the
`hello-constructors` example.

<!--
TODO: include this command in readme_test.sh.
-->

```shell
rsm dev --config=hello-constructors
```

Running `rsm dev` will watch for file modifications and restart the
running example if necessary. See the `.rsmrc` file for flags and
arguments that get expanded when running `rsm dev --config=hello-constructors`.

<!--
TODO: introduce an `rsm grpcurl` (or `rsm call` or ...) that lets us explore
our backend in another terminal by calling RPCs.
-->

### Tests

The example code comes with tests. Before you run the tests you'll
need to ensure you've run `rsm protoc`, which will have happened for
you if you've already run `rsm dev` without modifying `.rsmrc`,
otherwise, you can do it manually via:

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=55-55) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
rsm protoc
```
<!-- MARKDOWN-AUTO-DOCS:END -->

`rsm protoc` will automatically make required Resemble '.proto'
dependencies like `resemble/v1alpha1/options.proto` available on the
import path without you having to check them into your own repository.

<!-- TODO: link to the Resemble proto definitions once they are publicly available. -->

Now you can run the tests using `pytest`, for example, for the
`hello-constructors` example:

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=58-58) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
pytest hello-constructors/backend/
```
<!-- MARKDOWN-AUTO-DOCS:END -->
