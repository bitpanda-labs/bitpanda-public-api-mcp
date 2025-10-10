#!/usr/bin/env bash
set -e

if [ "$1" = 'api' ] ; then
    exec python -m bp_mcp.bitpanda_mcp_server
fi

exec "$@"
