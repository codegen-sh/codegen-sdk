#!/bin/bash

# directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# directory of the git hooks
GITHOOKS_DIR="${SCRIPT_DIR}/../githooks"

# directory where the hooks should be installed
INSTALL_DIR="${SCRIPT_DIR}/../.git/hooks"

# loop through the files in the githooks directory
for HOOK in $(ls "${GITHOOKS_DIR}"); do
    # create a symbolic link in the .git/hooks directory
    ln -sf "${GITHOOKS_DIR}/${HOOK}" "${INSTALL_DIR}/${HOOK}"

    # change permissions to make the hook executable
    chmod +x "${INSTALL_DIR}/${HOOK}"
done
