#!/bin/bash
#
# This test mirrors, as closely as possible, the user experience of following
# the `README.md` through its "Test" step.

### Preamble: sanity checks and setup not found in the `README.md`. ###

# In case of any errors, this test has failed. Fail immediately.
set -e
# In case of undefined variables, there must be a bug. Fail immediately.
set -u
# Show us the commands we're executing, to aid in debugging.
set -x

# Check that this script has been invoked with the right working directory, by
# checking that the expected subdirectories exist.
ls -l api/ hello-world/backend/src/ 2> /dev/null > /dev/null || {
  echo "ERROR: this script must be invoked from the root of the 'resemble-examples' repository."
  echo "Current working directory is '$(pwd)'."
  exit 1
}

# Use the published Resemble pip packages by default, but allow the test system
# to override them with a different value.
REBOOT_RESEMBLE_CLI_PACKAGE=${REBOOT_RESEMBLE_CLI_PACKAGE:-"reboot-resemble-cli"}
REBOOT_RESEMBLE_PACKAGE=${REBOOT_RESEMBLE_PACKAGE:-"reboot-resemble"}


### Start of the README.md test ###
# From here on we follow the `README.md` instructions verbatim.

# Create and activate a virtual environment.
python -m venv ./.hello-world-venv
source ./.hello-world-venv/bin/activate

# Install Resemble tooling.
pip install ${REBOOT_RESEMBLE_CLI_PACKAGE}

# Install Python requirements.
#
# First an extra step to let local unit tests work: install the
# `reboot-resemble` package from the specified path explicitly, so that if we're
# testing with a local version of the package, its line in `requirements.txt` is
# skipped in favor of the version already installed.
pip install $REBOOT_RESEMBLE_PACKAGE
# Back to what's in the readme verbatim.
pip install -r hello-world/backend/src/requirements.txt

# Compile protocol buffers.
rsm protoc ./api/hello_world/v1/greeter.proto

# Test.
pytest hello-world/backend/
