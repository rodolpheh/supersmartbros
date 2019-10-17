#!/bin/bash

if [ "$3" == "debug" ]; then
    pio ci -c configs/platformio-example-debug.ini --build-dir /tmp/piobuild --keep-build-dir -l lib/$1/ lib/$1/examples/$2.cpp
else
    pio ci -c configs/platformio-example.ini --build-dir /tmp/piobuild --keep-build-dir -l lib/$1/ lib/$1/examples/$2.cpp
fi
