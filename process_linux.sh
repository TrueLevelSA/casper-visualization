#!/bin/bash
set -e
set -u

# public
VISUALIZATION_DIR="../"

# private
PREFIX=_state
GENERATION_FOLDER=./generated

# pick last file generated in the $VISUALIZATION_DIR
LAST_VISU=blockchain_test.log

mkdir -p $GENERATION_FOLDER
cp $VISUALIZATION_DIR/$LAST_VISU .

# split the file in test cases files
csplit --prefix="$PREFIX" $LAST_VISU '/new chain/' '{*}'

# format each file as json
for file in ${PREFIX}*
do
    sed -i '1d' $file
    echo -e "[\n$(cat $file)" > $file
    sed -i 's/(/[/g' $file
    sed -i 's/)/]/g' $file
    sed -i 's/ ->/,/g' $file
    sed -i 's/LatestMsgs//g' $file
    sed -i '$ s/.$//' $file
    echo "]" >> $file
    sed -i 's/],\n]/]\n]/g' $file
    sed -i 's/M\([[:digit:]]\)/M\1:/g' $file
    sed -i -E "s/(0x([0-9]|[a-f])+|([A-Z]|[a-z])+|M[0-9]+)/\"\\1\"/g" $file
    sed 's/\([[:digit:]]\):/"\1":/g' $file > $GENERATION_FOLDER/processed$file'.json'
    rm $file
done

rm $LAST_VISU
