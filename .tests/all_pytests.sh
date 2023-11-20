#!/bin/bash
#
# This script will run all of the tests in this repository.
# Here is the list of all the tests that it runs:
all_pytest_folders=(
  "hello-constructors/backend"
  "bank/backend"
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
  echo "ERROR: this script must be invoked from the root of the 'resemble-examples' repository."
  echo "Current working directory is '$(pwd)'."
  exit 1
}

# Require `REBOOT_RESEMBLE_PACKAGE` to have been passed; all tests should be
# explicit about what package they expect to use.
echo "Using Resemble package '$REBOOT_RESEMBLE_WHL_PACKAGE'"

# Run each of the tests, each in their own virtual environment, so that they
# can't influence each other.
function runPyTest () {
  pytest_folder=$1
  echo "######################### $pytest_folder #########################"

  # Create and activate a virtual environment.
  rm -rf ./.resemble-examples-venv
  python -m venv ./.resemble-examples-venv
  source ./.resemble-examples-venv/bin/activate

  # Install the `reboot-resemble` package from the specified path explicitly, so
  # that if we're testing with a local version of the package, its line in
  # `requirements.txt` is skipped in favor of the version already installed.
  pip install $REBOOT_RESEMBLE_WHL_PACKAGE

  # Install requirements.
  requirements_txt="$pytest_folder/src/requirements.txt"
  if [ ! -f "$requirements_txt" ]; then
    echo "ERROR: no requirements.txt file found at $requirements_txt"
    exit 1
  fi
  # Sanity check: is `reboot-resemble` in the requirements.txt? We need to
  # check this explicitly, since we've already installed it explicitly above, we
  # could miss that it's not in the requirements.txt.
  if ! grep -q "^reboot-resemble" "$requirements_txt"; then
    echo "ERROR: 'reboot-resemble' is not in '$requirements_txt'"
    exit 1
  fi
  pip install -r "$requirements_txt"

  # Compile protocol buffers.
  # TODO: how do we ensure that we're working with a clean slate here?
  rsm protoc

  # Test.
  pytest $pytest_folder

  # We're done with this virtual environment. Deactivate it. It will get deleted
  # when we start the next one.
  deactivate
}

for pytest_folder in "${all_pytest_folders[@]}"; do
  runPyTest $pytest_folder
done

# TODO: when relevant, add additional non-pytest tests here.
