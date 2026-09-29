#!/bin/zsh
set -e
cd -- "${0:A:h}"
npm test
read '?Archipiélago: tests complete. Press Return to close.'
