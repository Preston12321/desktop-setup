#!/bin/sh

APT="apt install -y"

# Miscellaneous
$APT unzip net-tools moreutils neovim wine64 ttf-mscorefonts-installer apt-transport-https curl fonts-powerline pass neofetch

# Plata theme for GNOME
add-apt-repository ppa:tista/plata-theme
apt update
$APT plata-theme

# Development tools (apt)
$APT build-essential git default-jre adb clang-format gitk golang

# Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup override set stable
rustup update stable

# Go-lang programs
go get -u github.com/justjanne/powerline-go

# Alacritty
$APT cmake pkg-config libfreetype6-dev libfontconfig1-dev libxcb-xfixes0-dev python3 gzip
git clone https://github.com/alacritty/alacritty.git
cd alacritty
cargo build --release
infocmp alacritty || tic -xe alacritty,alacritty-direct extra/alacritty.info # Install terminfo
cp target/release/alacritty /usr/local/bin
cp extra/logo/alacritty-term.svg /usr/share/pixmaps/Alacritty.svg
desktop-file-install extra/linux/Alacritty.desktop
update-desktop-database
mkdir -p /usr/local/share/man/man1
gzip -c extra/alacritty.man | tee /usr/local/share/man/man1/alacritty.1.gz > /dev/null
cd ..
rm -rf alacritty

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
echo "deb https://download.mono-project.com/repo/ubuntu stable-bionic main" | tee /etc/apt/sources.list.d/mono-official-stable.list
apt update
$APT mono-complete

# Development tools (snap)
snap install --classic code
snap install hugo postman clion android-studio

# Media/Productivity
snap install --classic slack
snap install discord inkscape gimp onlyoffice-desktopeditors spotify vlc zotero-snap

# Brave Browser
curl -s https://brave-browser-apt-release.s3.brave.com/brave-core.asc | apt-key --keyring /etc/apt/trusted.gpg.d/brave-browser-release.gpg add -
echo "deb [arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main" | tee /etc/apt/sources.list.d/brave-browser-release.list
apt update
$APT brave-browser

# Keybase
wget -O ./keybase.deb https://prerelease.keybase.io/keybase_amd64.deb
$APT ./keybase.deb
rm ./keybase.deb
run_keybase &
