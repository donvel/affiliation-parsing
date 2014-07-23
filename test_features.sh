GRMM=/home/bartek/Projects/affiliation-parsing/grmm-0.1.3

train=crf/data/aff_fts_train.txt
tst=crf/data/aff_fts_test.txt
affs=resources/final.xml
model=crf/data/tmpls_chain.txt
err=crf/data/aff_fts_err.xml
err_html=aff_fts_err.html
test_number=5000

python scripts/export2.py --train $train --test $tst --input \
    $affs --train_number $1 --test_number $test_number --neighbor $2 --rare $3 "$4"

java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $train \
    --testing $tst \
    --model-file $model 2> err_$1_$2_$3.txt

python scripts/count_score.py --error_file $err
python scripts/make_readable.py --xml $err --html $err_html

firefox $err_html &
