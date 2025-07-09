#!/bin/sh

# exits immediately if a command exists with a non-zero status
set -e

# Run uvicorn
if [ "$ENVIRONMENT" = "dev" ]; then
    poetry run uvicorn app.main:app --host 0.0.0.0 --port 4460 --reload
else
    poetry run uvicorn app.main:app --host 0.0.0.0 --port 4460
fi