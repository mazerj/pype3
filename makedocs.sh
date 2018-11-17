#!/bin/sh

sed "s^%%PYPEDIR%%^$PYPEDIR^g" <epydoc.conf >/tmp/$$.conf

epydoc -v --no-private --simple-term --config=/tmp/$$.conf \
	       --exclude=Pmw \
	       --exclude=pype.stats \
	       --exclude=pype.pstat \
	       --exclude=pype.dacq \
	       --exclude=pype.candy \
	       --exclude=pype.gificons \
	       --exclude=pype.candy \
	       --exclude=pype.dynconfig \
	       --exclude=pype.userparams \
	       --exclude=pype.config \
	       --exclude=pype.configvars \
	       --exclude=pype.PlexHeaders \
	       --exclude=pype.PlexNet \
	       --exclude=pype.pype2tdt \
	       --exclude=pype.tdt \
	       --exclude=pype.ttank \
	       --exclude=pype.labjack \
	       --exclude=pype.ttank \
	       --exclude=pype.griddata \
	       --exclude=pype.handmap \
	       --exclude=pype.importer \
	       --exclude=pype.libinfo \
	       --exclude=pype.n2n \
	       --exclude=pype.ikeyboard \
	       --exclude=pype.im_stop \
	       --exclude=pype.im_splash \
	       --exclude=pype.im_left \
	       --exclude=pype.im_right \
	       --exclude=pype.im_up \
	       --exclude=pype.im_down \
	       --exclude=pype.pypedata \
	       --exclude=pype.rootperm \
	       --exclude=pype.pypeversion\
	       --exclude=pype.HTML \
	       --exclude=pype.server \
	       --exclude=pype.pypehttpd \
	       --exclude=pype.gammacal \
	       --exclude=pype.guitools \
	       --exclude=pype.peyetribe \
	       --exclude=pype.style \
	       --exclude=pype.userdpy \
	       --exclude=pype.simpletimer

/bin/rm -f /tmp/$$.conf

echo "do \`build pushdocs\` to publish on github."
