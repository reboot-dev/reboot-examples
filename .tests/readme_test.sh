#!/bin/bash
#
# This test mirrors, as closely as possible, the user experience of following
# the `README.md` through its "Test" step.

### Preamble: sanity checks and setup not found in the `README.md`. ###

# In case of any errors, this test has failed. Fail immediately.
set -e
# Show us the commands we're executing, to aid in debugging.
set -x

# Check that this script has been invoked with the right working directory, by
# checking that the expected subdirectories exist.
ls -l api/ hello-constructors/backend/src/ 2> /dev/null > /dev/null || {
  echo "ERROR: this script must be invoked from the root of the 'resemble-examples' repository."
  echo "Current working directory is '$(pwd)'."
  exit 1
}

# Convert symlinks to files that we need to mutate into copies.
for file in "requirements.lock" "requirements-dev.lock" "pyproject.toml"; do
  cp "$file" "${file}.tmp"
  rm "$file"
  mv "${file}.tmp" "$file"
done

# Use the published Resemble pip package by default, but allow the test system
# to override them with a different value.
if [ -n "$REBOOT_RESEMBLE_WHL_FILE" ]; then
  # Install the `reboot-resemble` package from the specified path explicitly, over-
  # writing the version from `pyproject.toml`.
  rye remove --no-sync reboot-resemble
  rye remove --no-sync --dev reboot-resemble
  rye add --dev reboot-resemble --absolute --path=$REBOOT_RESEMBLE_WHL_FILE
fi

### Start of the README.md test ###
# From here on we follow the `README.md` instructions verbatim.

# Create and activate a virtual environment.
rye sync --no-lock
source .venv/bin/activate

cd hello-constructors

# Compile protocol buffers.
rsm protoc

# Test.
pytest backend/
