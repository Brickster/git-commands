#! /bin/bash
set -ev

# upload coverage report for pushes to master only
# NOTE: secure environment variables aren't available for PRs from other repositories
if [[ ! -z "$CODACY_PROJECT_TOKEN" ]] && [ "$TRAVIS_PULL_REQUEST" == "false" ] && [ "$TRAVIS_BRANCH" == "master" ]; then
    coverage xml --include=bin/* --omit=*/__init__.py -o coverage.xml
    python-codacy-coverage -r coverage.xml
fi
