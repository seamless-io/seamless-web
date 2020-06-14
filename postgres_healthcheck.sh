#!/bin/bash
set -eo pipefail

if select="$(echo 'SELECT 1' | PGPASSWORD=root psql -U postgres)" && echo $select && [[ "$select" =~ .*(1 row).* ]]; then
	exit 0
fi

exit 1