# #!/usr/local/bin/zsh
cp states.dat states2.dat
gsed -i '1d' states2.dat
gsed -i '/tests/d' states2.dat
gsed -i '/test example::/d' states2.dat
gsed -i '/test result:/d' states2.dat
csplit states2.dat '/new chain/' '{100}'
for file in xx*; do
    gsed -i '1d' $file
    echo "[\n$(cat $file)" > $file
    gsed -i 's/Some(Block(ProtoBlock//g' $file
    gsed -i 's/Block(ProtoBlock//g' $file
    gsed -i 's/, txs: {} //g' $file
    gsed -i 's/LatestMsgs(//g' $file
    gsed -i 's/(//g' $file
    gsed -i 's/)//g' $file
    gsed -i '$ s/.$//' $file
    echo "]" >> $file
    gsed -i 's/],\n]/]\n]/g' $file
    gsed -i 's/M\([[:digit:]]\)/M\1:/g' $file
    sed -E "s/([a-z]+|N[a-z]+|M[0-9]+|[0-9]+)/\"\\1\"/g" $file > processed$file'.json'
done
