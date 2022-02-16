#!/bin/bash

curl https://github.com/ryanoasis/nerd-fonts/releases/download/v2.1.0/FiraMono.zip > FiraMono.zip
unzip -d FiraMono FiraMono.zip
rm FiraMono/Fura*
rm FiraMono/*Windows\ Compatible.otf
mkdir -p /usr/share/fonts/opentype/nerd/fira/
cp *.otf /usr/share/fonts/opentype/nerd/fira/
rm -rf FiraMono
