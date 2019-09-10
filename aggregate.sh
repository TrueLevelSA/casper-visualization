#! /usr/bin/env bash
set -e
set -u

function aggregate {
    local -r FOLDER="./generated/backup/"

    head -n1 $(ls ${FOLDER}*.csv | head -n1) > gen.csv
    head -n1 $(ls ${FOLDER}*.csv | head -n1) > gen_averages.csv

    local -r FOLDER_PREFIX=${FOLDER}$1

    for file in $(ls ${FOLDER_PREFIX}*gen.csv)
    do
        echo Aggregating $file
        tail -n +2 $file >> gen.csv
    done

    for file in $(ls ${FOLDER_PREFIX}*gen_averages.csv)
    do
        echo Aggregating $file
        tail -n +2 $file >> gen_averages.csv
    done
}

if [ $# -eq 1 ]
then
    aggregate $1
else
    echo usage: $0 file_prefix
    echo file_prefix is the prefix of the files located in ./generated/backup that will be aggregated
fi
