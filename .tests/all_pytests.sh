#!/bin/bash
#
# This script will run all of the tests in the following directories:
all_application_folders=(
  "hello-constructors"
  "bank"
  "hello-legacy-grpc"
  "hello-tasks"
)

# In case of any errors, this test has failed. Fail immediately.
set -e
# In case of undefined variables, there must be a bug. Fail immediately.
set -u
# Show us the commands we're executing, to aid in debugging.
set -x

# Check that this script has been invoked with the right working directory, by
# checking that the expected subdirectories exist.
ls -l api/ hello-constructors/backend/src/ 2> /dev/null > /dev/null || {
  echo "ERROR: this script must be invoked from the root of the 'reboot-examples' repository."
  echo "Current working directory is '$(pwd)'."
  exit 1
}

# Require `REBOOT_WHL_FILE` to have been passed; all tests calling this
# file should be explicit about a specific Reboot wheel file they've built.
echo "Using Reboot package '$REBOOT_WHL_FILE'"

# Run each of the tests, each in their own virtual environment, so that they
# can't influence each other.
function runPyTest () {
  application_folder=$1
  echo "######################### $application_folder #########################"

  pushd $application_folder

  # Compile protocol buffers.
  # TODO: how do we ensure that we're working with a clean slate here?
  rbt protoc

  # Test.
  pytest backend/

  popd
}

# Convert symlinks to files that we need to mutate into copies.
for file in "requirements.lock" "requirements-dev.lock" "pyproject.toml"; do
  cp "$file" "${file}.tmp"
  rm "$file"
  mv "${file}.tmp" "$file"
done

# Install the `reboot` package from the specified path explicitly, over-
# writing the version from `pyproject.toml`.
rye remove --no-sync reboot
rye remove --no-sync --dev reboot
rye add --dev reboot --absolute --path=$REBOOT_WHL_FILE

# Create and activate a virtual environment.
rye sync --no-lock
source .venv/bin/activate

for application_folder in "${all_application_folders[@]}"; do
  runPyTest $application_folder
done

# Deactivate the virtual environment, since we can run a test which may require
# another virtual environment (currently we do that only in `all_tests.sh`).
deactivate

# TODO: when relevant, add additional non-pytest tests here.
