#!/bin/bash

export LATITUDE=
export LONGITUDE=

export GOOGLE_API_KEY=…
#export TRAFFIC_FROM=
export TRAFFIC_FROM="${LATITUDE}-${LONGITUDE}"
export TRAFFIC_1_THROUGH=6JV5+4FP
export TRAFFIC_2_THROUGH=7JFQ+V8P
export TRAFFIC_TO=6JXP+GX

## Air information

export AIRLY_API_KEY=…

## Weather information

export FORECASTIO_API_KEY=

./epaper.py

