#!/bin/sh

# Miscellaneous
apt install net-tools
apt install moreutils
apt install xterm
apt install vim
apt install wine64
apt install ttf-mscorefonts-installer
apt install chrome-gnome-shell

# Plata theme for GNOME
add-apt-repository ppa:tista/plata-theme
apt update
apt install plata-theme

# Development tools (apt)
apt install build-essential
apt install git
apt install default-jre
apt install adb
apt install clang-format
apt install python-pip
apt install gitk
apt install cmake

# Dart
apt install apt-transport-https
sh -c 'wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -'
sh -c 'wget -qO- https://storage.googleapis.com/download.dartlang.org/linux/debian/dart_stable.list > /etc/apt/sources.list.d/dart_stable.list'
apt update
apt install dart
echo '# Add Dart to path variable' >> ~/.bashrc
echo 'export PATH="$PATH:/usr/lib/dart/bin"' >> ~/.bashrc

# Mono
apt install gnupg ca-certificates
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
echo "deb https://download.mono-project.com/repo/ubuntu stable-bionic main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list
apt update
apt install mono-complete

# Development tools (snap)
snap install code
snap install hugo
snap install postman
snap install clion
snap install android-studio

# Media/Productivity
snap install discord
snap install inkscape
snap install gimp
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
