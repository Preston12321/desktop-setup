#!/bin/sh

APT="apt install -y"

# Miscellaneous
$APT unzip net-tools moreutils xterm vim wine64 ttf-mscorefonts-installer chrome-gnome-shell

# Plata theme for GNOME
add-apt-repository ppa:tista/plata-theme
apt update
$APT plata-theme

# Development tools (apt)
$APT build-essential git default-jre adb clang-format python-pip gitk cmake

# Dart
$APT apt-transport-https
wget -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
wget -O - https://storage.googleapis.com/download.dartlang.org/linux/debian/dart_stable.list > /etc/apt/sources.list.d/dart_stable.list
apt update
$APT dart
echo '# Add Dart to path variable' >> ~/.bashrc
echo 'export PATH="$PATH:/usr/lib/dart/bin"' >> ~/.bashrc

# Flutter
git clone https://github.com/flutter/flutter.git -b stable ~/.flutter-manual-install
echo '# Add Flutter to path variable' >> ~/.bashrc
echo 'export PATH="$PATH:~/.flutter-manual-install/bin"' >> ~/.bashrc

# Godot
wget -O ./godot.zip https://downloads.tuxfamily.org/godotengine/3.2.1/Godot_v3.2.1-stable_x11.64.zip
mkdir ~/.godot-manual-install
unzip -d ~/.godot-manual-install ./godot.zip
rm ./godot.zip
echo '# Add Godot to path variable' >> ~/.bashrc
echo 'export PATH="$PATH:~/.godot-manual-install"' >> ~/.bashrc

# Mono
$APT gnupg ca-certificates
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
echo "deb https://download.mono-project.com/repo/ubuntu stable-bionic main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list
apt update
$APT mono-complete

# Development tools (snap)
snap install code hugo postman clion android-studio

# Media/Productivity
snap install discord inkscape gimp onlyoffice-desktopeditors slack spotify vlc zotero-snap

# Google Chrome
wget -O ./chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
$APT ./chrome.deb
rm ./chrome.deb

# Enpass
echo "deb https://apt.enpass.io/ stable main" > /etc/apt/sources.list.d/enpass.list
wget -O - https://apt.enpass.io/keys/enpass-linux.key | apt-key add -
apt update
$APT enpass

# Keybase
wget -O ./keybase.deb https://prerelease.keybase.io/keybase_amd64.deb
$APT ./keybase.deb
rm ./keybase.deb
run_keybase &
