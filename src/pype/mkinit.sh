#!/bin/sh

cat <<EOF
"""
**Python Environment for neuroPhysiology (pype -- version 3)**

Someday complete documentation for users will live here. Until
then, the two basic ways to invove pype. They are as follows:

* startup pype with full GUI; load task if specified:

    % pype [task]

* run python script with pype environment loaded/available:

    % pypenv [script]

"""
EOF

echo "__all__ = ["
ls -1 [a-zA-Z]*.py |\
    sort -f | awk '{printf("\t\"%s\",\n", $1)}'
echo "]"
