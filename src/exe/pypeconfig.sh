#!/bin/sh

export PYPERC=$HOME/.pyperc
exec ${EDITOR:-vi} $PYPERC/Config.$(hostname -s)

