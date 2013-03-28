#!/bin/sh

for f in $*; do
  matlab -nojvm -r "affinecal_batch(jls('$1'));quit;"
done

exit 0
