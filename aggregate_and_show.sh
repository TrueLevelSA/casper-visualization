#! /usr/bin/env bash

head -n1 $(ls ./generated/backup/*.csv | head -n1) > gen.csv

for file in $(ls ./generated/backup/*.csv)
do
    tail -n +2 $file >> gen.csv
done

pipenv run python ./visualization_metrics.py

