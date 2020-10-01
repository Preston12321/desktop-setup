#!/bin/bash

INSTALL="apt install -y"
APT_PROGRAMS=""
SNAP_PROGRAMS=""
SNAP_PROGRAMS_CLASSIC=""

# Needed for adding PPAs/verifying signatures
$INSTALL apt-transport-https gnupg ca-certificates curl

# Miscellaneous utilities
$APT_PROGRAMS+="xclip unzip net-tools moreutils alacritty neovim wine64 ttf-mscorefonts-installer fonts-powerline pass neofetch"

# Plata theme for GNOME
add-apt-repository ppa:tista/plata-theme
$APT_PROGRAMS+="plata-theme"

# Development tools
$APT_PROGRAMS+="build-essential git default-jre default-jdk adb clangd clang-format gitk python3 python3-pip golang godot3"
SNAP_PROGRAMS_CLASSIC+="code flutter"
SNAP_PROGRAMS+="hugo postman android-studio"

# Mono
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
echo "deb https://download.mono-project.com/repo/ubuntu stable-focal main" | tee /etc/apt/sources.list.d/mono-official-stable.list
$APT_PROGRAMS+="mono-complete"

# NodeJS and yarn
mkdir -p "$NVM_DIR"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash # Install NVM
\. "$NVM_DIR/nvm.sh"  # Load nvm
nvm install node
npm install -g yarn

# Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup override set stable
rustup update stable

# Spotify daemon and spotify-tui
cargo install spotifyd --locked
SNAP_PROGRAMS+="spt"

# Brave Browser
curl -s https://brave-browser-apt-release.s3.brave.com/brave-core.asc | apt-key --keyring /etc/apt/trusted.gpg.d/brave-browser-release.gpg add -
echo "deb [arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main" | tee /etc/apt/sources.list.d/brave-browser-release.list
$APT_PROGRAMS+="brave-browser"

# Pass extensions
$APT_PROGRAMS+="pass-extension-update pass-extension-tail pass-extension-audit"

# Media/Productivity
SNAP_PROGRAMS_CLASSIC+="slack"
SNAP_PROGRAMS+="discord inkscape gimp onlyoffice-desktopeditors vlc zotero-snap"

# Install all the apt packages
apt update
$INSTALL "$APT_PROGRAMS"

# Install all the snap packages
snap install --classic "$SNAP_PROGRAMS_CLASSIC"
snap install "$SNAP_PROGRAMS"

# Install golang programs
go get -u github.com/justjanne/powerline-go

# Install Python packages
pip3 install pynvim

# Install NodeJS packages
npm i -g neovim

# NeoVim plugins/extensions
nvim -c 'PlugInstall|q'
nvim -c 'CocInstall -sync coc-snippets coc-marketplace coc-explorer coc-eslint coc-html coc-java coc-go coc-flutter coc-python coc-rls coc-sh coc-clangd coc-texlab coc-emmet coc-vimlsp coc-css coc-yaml coc-json
|q'

# Browserpass
git clone https://github.com/browserpass/browserpass-native.git
cd browserpass-native
make BIN=browserpass-linux64 configure
make BIN=browserpass-linux64 install
make hosts-brave-user
cd ..
rm -rf browserpass-native
git clone https://github.com/Preston12321/browserpass-extension.git $HOME/Desktop/browserpass-extension
cd $HOME/Desktop/browserpass-extension
make chromium

# Keybase
wget -O ./keybase.deb https://prerelease.keybase.io/keybase_amd64.deb
$INSTALL ./keybase.deb
rm ./keybase.deb
run_keybase &
