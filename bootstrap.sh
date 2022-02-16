#!/bin/bash

apt=$(which apt)
pacman=$(which pacman)

PKG_MNGR=""

if [ -n "$apt" ]; then
  PKG_MNGR="apt"
elif [ -n "$pacman" ]; then
  PKG_MNGR="pacman"
else
  echo "Error: Couldn't locate any common package manager"
  exit 1
fi

sudo echo "Obtained root privileges"

# Basic packages that we'll need for everything else
if [ "$PKG_MNGR" == "apt" ]; then
  sudo apt update
  sudo apt upgrade -y
  sudo apt install -y build-essential apt-transport-https gnupg ca-certificates curl snapd git python3 python3-pip unzip
else
  sudo pacman -Syyu # Update repos and upgrade packages
  sudo pacman --noconfirm -S base-devel gnupg ca-certificates curl git python python-pip unzip

  # Install paru if not already present
  paru=$(which paru)
  if [ -z "$paru" ]; then
    git clone https://aur.archlinux.org/paru-bin.git
    cd paru-bin
    sudo makepkg -s -i # Install dependencies, build package, then install
    cd ..
    rm -rf paru-bin
  fi

  # Install snapd
  paru --skipreview -S snapd 
fi

# Pull down dotfiles before installing other programs. Will ensure they
# don't wreck the home directory before XDG paths are set
GIT_BARE="git --git-dir=$HOME/.home-bare-repo --work-tree=$HOME"
git clone --bare https://github.com/Preston12321/home-bare-repo.git $HOME/.home-bare-repo
$GIT_BARE reset --hard HEAD
$GIT_BARE config status.showUntrackedFiles no

source $HOME/.profile

git clone https://github.com/Preston12321/desktop-setup.git
cd desktop-setup

# Dependencies for install script generator
# Install as sudo since setup.py will also be run as sudo
sudo pip3 install -r requirements.txt

# Generate install script based off of YAML files
sudo python3 setup.py || exit 1

cd ..
rm -rf desktop-setup
