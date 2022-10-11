#!/bin/bash

sudo apt update
sudo apt install gzip -y
sudo apt install python3-pip -y
sudo pip3 install pandas

sudo mkdir -p /opt/WarpDock
cd /opt/WarpDock

sudo wget https://raw.githubusercontent.com/BruningLab/warpDOCK/blob/main/bin/Conductor.py
sudo wget https://raw.githubusercontent.com/BruningLab/warpDOCK/blob/main/bin/FetchResults.py
sudo wget https://raw.githubusercontent.com/BruningLab/warpDOCK/blob/main/bin/FileDivider.py
sudo wget https://raw.githubusercontent.com/BruningLab/warpDOCK/blob/main/bin/PDBQTsplitter.py
sudo wget https://raw.githubusercontent.com/BruningLab/warpDOCK/blob/main/bin/ReDocking.py
sudo wget https://raw.githubusercontent.com/BruningLab/warpDOCK/blob/main/bin/Splitter.py
sudo wget https://raw.githubusercontent.com/BruningLab/warpDOCK/blob/main/bin/WarpDrive.py
sudo wget https://raw.githubusercontent.com/BruningLab/warpDOCK/blob/main/bin/ZincDownloader.py 

sudo wget https://github.com/QVina/qvina/raw/master/bin/qvina2.1

sudo chmod 777 /opt/WarpDock/*

sudo ln -s /opt/WarpDock/Conductor.py /usr/local/bin/Conductor
sudo ln -s /opt/WarpDock/FetchResults.py /usr/local/bin/FetchResults
sudo ln -s /opt/WarpDock/FileDivider.py /usr/local/bin/FileDivider
sudo ln -s /opt/WarpDock/PDBQTsplitter.py /usr/local/bin/PDBQTsplitter
sudo ln -s /opt/WarpDock/ReDocking.py /usr/local/bin/ReDocking
sudo ln -s /opt/WarpDock/Splitter.py /usr/local/bin/Splitter
sudo ln -s /opt/WarpDock/WarpDrive.py /usr/local/bin/WarpDrive
sudo ln -s /opt/WarpDock/ZincDownloader.py /usr/local/bin/ZincDownloader

sudo ln -s /opt/WarpDock/qvina2.1 /usr/local/bin/vina

cd

sudo rm -rf Installer.sh

