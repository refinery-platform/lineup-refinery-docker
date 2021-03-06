#!/usr/bin/env bash
set -o errexit

source environment.sh

DEFAULTS="--name $CONTAINER_NAME --detach --publish $PORT:80 $IMAGE"

if [ -z "$@" ]; then
    JSON=`cat fixtures/fake-input.json`
    $OPT_SUDO docker run --env INPUT_JSON="$JSON" $DEFAULTS
else
    echo "Will mount command line arguments: $@"
    VOLS=''
    I=0
    IN_CONTAINER_ARGS=''
    for ARG in "$@"; do
        ((I++))
        ABSOLUTE_PATH=`realpath $ARG`
        IN_CONTAINER_PATH=/tmp/$I.txt
        VOLS="$VOLS --volume $ABSOLUTE_PATH:$IN_CONTAINER_PATH"
        IN_CONTAINER_ARGS="$IN_CONTAINER_ARGS $IN_CONTAINER_PATH"
    done
    $OPT_SUDO docker run $VOLS $DEFAULTS ../on_startup.sh $IN_CONTAINER_ARGS
fi
echo "Visit http://localhost:$PORT"