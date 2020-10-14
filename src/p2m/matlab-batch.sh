#!/bin/bash
# run matlab and feed command line args

function cleanup { /bin/rm s$$.m; }

echo $* > s$$.m
trap cleanup EXIT
matlab -nodisplay -batch s$$

