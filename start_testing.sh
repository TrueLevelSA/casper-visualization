#!/usr/bin/env bash
set -e
set -u

function run_once {
    pushd ..
    set +e
    cargo test --features integration_test blockchain -- --nocapture
    if [ $? -ne 0 ]
    then
        popd
        set -e
        return
    else
        set -e
        popd
    fi

    mkdir -p ./generated/backup
    local -r DATE=$(date +"%y-%m-%d_%H-%M-%S_")
    local -r PREFIX=$1

    pipenv run python ./process_metrics.py
    rm ../stats*.log

    cp ./gen.csv ./generated/backup/${PREFIX}_${DATE}gen.csv
}

function main {
    for i in {1..100}
    do
        run_once $1
    done
}

if [ $# -eq 1 ]
then
    main $1
else
    main default
fi
