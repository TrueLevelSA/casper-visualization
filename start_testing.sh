#!/usr/bin/env bash
set -e
set -u

function run_once {
    pushd ..
    set +e
    set +u
    cargo test --features integration_test blockchain $2 -- --nocapture
    if [ $? -ne 0 ]
    then
        popd
        set -e
        set -u
        return
    else
        set -e
        set -u
        popd
    fi

    mkdir -p ./generated/backup
    mkdir -p ./generated/stats
    local -r DATE=$(date +"%y-%m-%d_%H-%M-%S_")
    local -r PREFIX=$1

    pipenv run python ./process_metrics.py
    for f in ../stats*.log
    do
        FILENAME=$(basename $f)
        mv ../$FILENAME ./generated/stats/${PREFIX}_${DATE}${FILENAME}
    done

    cp ./gen_averages.csv ./generated/backup/${PREFIX}_${DATE}gen_averages.csv
    cp ./gen.csv ./generated/backup/${PREFIX}_${DATE}gen.csv
}

function main {
    for i in {1..100}
    do
        run_once "$1" "$2"
    done
}

if [ $# -eq 2 ]
then
    echo not default
    main "$1" "--jobs $2"
else
    echo usage: $0 name_of_logs num_of_jobs
fi
