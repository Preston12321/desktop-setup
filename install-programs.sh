#!/bin/sh

# Miscellaneous
apt install apt-transport-https
apt install net-tools
apt install moreutils
apt install wine64
apt install xterm
apt install vim
apt install ttf-mscorefonts-installer

# GNOME customization
apt install chrome-gnome-shell
apt install plata-theme

# Development tools
apt install git
apt install default-jre
apt install adb
apt install clang-format
apt install python-pip
apt install dart
apt install gitk
apt install mono-complete
apt install cmake
snap install android-studio
snap install clion
snap install code
snap install hugo
snap install postman
snap install pycharm-professional

# Media/Productivity
snap install discord
snap install inkscape
snap install onlyoffice-desktopeditors
snap install slack
snap install spotify
snap install vlc

# Enpass password manager
echo "deb https://apt.enpass.io/ stable main" > /etc/apt/sources.list.d/enpass.list
wget -O - https://apt.enpass.io/keys/enpass-linux.key | apt-key add -
apt update
apt install enpass

# Nord VPN
wget -O ./nordvpn.deb https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn-release_1.0.0_all.deb
apt install ./nordvpn.deb
rm ./nordvpn.deb
apt install nordvpn

# Keybase
wget -O ./keybase.deb https://prerelease.keybase.io/keybase_amd64.deb
apt install ./keybase.deb
rm ./keybase.deb
run_keybase &
