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
  echo "ERROR: this script must be invoked from the root of the 'resemble-examples' repository."
  echo "Current working directory is '$(pwd)'."
  exit 1
}

# Require `REBOOT_RESEMBLE_WHL_FILE` to have been passed; all tests calling this
# file should be explicit about a specific Resemble wheel file they've built.
echo "Using Resemble package '$REBOOT_RESEMBLE_WHL_FILE'"

# Run each of the tests, each in their own virtual environment, so that they
# can't influence each other.
function runPyTest () {
  application_folder=$1
  echo "######################### $application_folder #########################"

  # Create and activate a virtual environment.
  rm -rf ./.resemble-examples-venv
  python -m venv ./.resemble-examples-venv
  source ./.resemble-examples-venv/bin/activate

  # Install the `reboot-resemble` package from the specified path explicitly, so
  # that if we're testing with a local version of the package, its line in
  # `requirements.txt` is skipped in favor of the version already installed.
  pip install $REBOOT_RESEMBLE_WHL_FILE

  # Save the pip show info on the package so that we can compare it after
  # installing the rest of the requirements, to check that our custom whl hasn't
  # been overwritten.
  resemble_info=$(pip show reboot-resemble)

  # Install requirements.
  requirements_txt="$application_folder/backend/src/requirements.txt"
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

  # Double check that we haven't reinstalled another version of the
  # reboot-resemble package.
  if [ "$resemble_info" != "$(pip show reboot-resemble)" ]; then
    echo "ERROR: reboot-resemble whl overwritten by pip install. Are the package versions out of sync?"
    exit 1
  fi

  pushd $application_folder

  # Compile protocol buffers.
  # TODO: how do we ensure that we're working with a clean slate here?
  rsm protoc

  # Test.
  pytest backend/

  popd

  # We're done with this virtual environment. Deactivate it. It will get deleted
  # when we start the next one.
  deactivate
}

for application_folder in "${all_application_folders[@]}"; do
  runPyTest $application_folder
done

# TODO: when relevant, add additional non-pytest tests here.
