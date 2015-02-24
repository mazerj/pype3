# install required packages (this may break for debian because of msfonts)
sudo sh dep-packages.sh

# need libez for serial port access
sudo sh ./ez-install.sh

# need eyelink libraries/header files -- install from repository
sudo sh ./eyelink-repo.sh


cat <<EOF

Now run 'cd ..; ./localinstall' to build and install.

EOF
