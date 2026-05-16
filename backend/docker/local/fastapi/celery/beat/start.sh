#! /bin/bash

set -o errexit

set -o nounset

set -o pipefail

exex watchfiles --filter python celery.__main__.main --args '-A backend.app.core.celery_app beat -l INFO'