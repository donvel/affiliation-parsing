GRMM=/home/bartek/Projects/affiliation-parsing/grmm-0.1.3

java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $1 \
    --testing $2 \
    --model-file $3
    2>&1 >/dev/null | grep 'Testing\|Training'
