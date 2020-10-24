#!/bin/bash

INSTALL="sudo apt install -y"
ADD_REPO="sudo add-apt-repository -y"
APT_PROGRAMS=()
SNAP_PROGRAMS_CLASSIC=()
SNAP_PROGRAMS=()

# Needed for adding PPAs/verifying signatures
$INSTALL apt-transport-https gnupg ca-certificates curl

if [ "$1" == "--desktop" ]; then
    $ADD_REPO ppa:tatokis/ckb-next
    APT_PROGRAMS+=( ckb-next )
fi

# Miscellaneous utilities
APT_PROGRAMS+=( snap gnome-tweaks xclip unzip net-tools moreutils alacritty neovim wine64 ttf-mscorefonts-installer fonts-powerline pass neofetch )

# Plata theme for GNOME
$ADD_REPO ppa:tista/plata-theme
APT_PROGRAMS+=( plata-theme )

# Development tools
APT_PROGRAMS+=( build-essential git default-jre default-jdk adb clangd clang-format gitk python3 python3-pip golang godot3 )
SNAP_PROGRAMS_CLASSIC+=( code flutter android-studio )
SNAP_PROGRAMS+=( hugo postman )

# Mono
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
echo "deb https://download.mono-project.com/repo/ubuntu stable-focal main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list
APT_PROGRAMS+=( mono-complete )

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
SNAP_PROGRAMS+=( spt )

# Brave Browser
curl -s https://brave-browser-apt-release.s3.brave.com/brave-core.asc | sudo apt-key --keyring /etc/apt/trusted.gpg.d/brave-browser-release.gpg add -
echo "deb [arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main" | sudo tee /etc/apt/sources.list.d/brave-browser-release.list
APT_PROGRAMS+=( brave-browser )

# Nextcloud client and Nautilus integration
$ADD_REPO ppa:nextcloud-devs/client
APT_PROGRAMS+=( nextcloud-desktop nautilus-nextcloud )

# Pass extensions
wget -qO - https://pkg.pujol.io/debian/gpgkey | sudo apt-key add -
sudo su --command="echo 'deb https://pkg.pujol.io/debian/repo all main' > /etc/apt/sources.list.d/pkg.pujol.io.list"
APT_PROGRAMS+=( pass-extension-update pass-extension-tail pass-extension-audit )

# Media/Productivity
SNAP_PROGRAMS_CLASSIC+=( slack )
SNAP_PROGRAMS+=( discord inkscape gimp onlyoffice-desktopeditors vlc zotero-snap )

# Install all the apt packages
sudo apt update
$INSTALL ${APT_PROGRAMS[@]}

# Install all the snap packages
for program in ${SNAP_PROGRAMS_CLASSIC[@]}; do
  sudo snap install --classic $program
done

sudo snap install ${SNAP_PROGRAMS[@]}

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
