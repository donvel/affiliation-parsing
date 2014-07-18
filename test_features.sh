GRMM=/home/bartek/Projects/affiliation-parsing/grmm-0.1.3

train=crf/data/aff_fts_train.txt
tst=crf/data/aff_fts_test.txt
affs=resources/affiliations_stripped.xml
model=crf/data/tmpls_chain.txt

python scripts/export.py 100 $train $tst $affs "$1"

java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $train \
    --testing $tst \
    --model-file $model 2> /dev/null

python scripts/count_score.py acrf_output_Testing.txt one_number