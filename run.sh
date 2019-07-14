#!/usr/bin/env bash

docker build ./backend -t knockknock-backend
docker build ./cronjob -t knockknock-cronjob
docker-compose up
