#!/bin/bash
set -e
set -u

SED=sed

if [[ "$OSTYPE" == "darwin"* ]]; then
    SED=gsed
fi

# public
VISUALIZATION_DIR="../"

# private
PREFIX=_state
GENERATION_FOLDER=./generated

# pick last file generated in the $VISUALIZATION_DIR
LAST_VISU=blockchain_test_*.log

mkdir -p $GENERATION_FOLDER
cp $VISUALIZATION_DIR/$LAST_VISU .

# format each file as json
for file in $LAST_VISU
do
    echo Processing $file
#    $SED -i '1d' $file
    echo -e "[\n$(cat $file)" > $file
    $SED -i 's/(/[/g' $file
    $SED -i 's/)/]/g' $file
    $SED -i 's/ ->/,/g' $file
    $SED -i 's/LatestMsgs//g' $file
    $SED -i '$ s/.$//' $file
    echo "]" >> $file
    $SED -i 's/],\n]/]\n]/g' $file
    $SED -i 's/M\([[:digit:]]\)/M\1:/g' $file
    $SED -i -E "s/(0x([0-9]|[a-f])+|([A-Z]|[a-z])+|M[0-9]+)/\"\\1\"/g" $file
    $SED 's/\([[:digit:]]\):/"\1":/g' $file > $GENERATION_FOLDER/processed_$file'.json'
    rm $file
done
