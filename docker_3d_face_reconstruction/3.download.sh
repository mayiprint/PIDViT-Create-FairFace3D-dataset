#!/bin/bash

echo "This script will download the VRN network model."
if [ -f "vrn-unguided.t7" ]; then
    echo "File vrn-unguided.t7 exists."
else
    wget -O vrn-unguided.t7 \
     https://asjackson.s3.fr-par.scw.cloud/vrn/vrn-unguided.t7
fi
if [ -f "face-alignment/2D-FAN-300W.t7" ]; then
    echo "File 2D-FAN-300W.t7 exists."
else
    wget -O face-alignment/2D-FAN-300W.t7 \
     https://asjackson.s3.fr-par.scw.cloud/vrn/2D-FAN-300W.t7
fi