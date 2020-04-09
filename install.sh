#!/bin/bash

sudo apt update
sudo apt dist-upgrade
curl -sL https://deb.nodesource.com/setup_12.x | sudo bash -
sudo apt install nodejs 
sudo apt install python3-opencv
sudo pip3 install shamir
sudo pip3 install torchvision
curl -sL https://raw.githubusercontent.com/shashigharti/federated-learning-on-raspberry-pi/master/PyTorch%20Wheels/torch-1.0.0a0%2B8322165-cp37-cp37m-linux_armv7l.whl > torch.whl
sudo pip3 install torch.whl
rm torch.whl
cd keypad
npm install
npm start &
cd ../shamir/
python3 crow_caw.py
