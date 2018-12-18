#!/bin/bash
set -e
set -u

SED=sed
CSPLIT=csplit

if [[ "$OSTYPE" == "darwin"* ]]; then
    SED=gsed
    CSPLIT=gcsplit
fi

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
$CSPLIT --prefix="$PREFIX" $LAST_VISU '/new chain/' '{*}' &> /dev/null

# format each file as json
for file in ${PREFIX}*
do
    $SED -i '1d' $file
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
    $SED 's/\([[:digit:]]\):/"\1":/g' $file > $GENERATION_FOLDER/proces$SED$file'.json'
    rm $file
done

rm $LAST_VISU
