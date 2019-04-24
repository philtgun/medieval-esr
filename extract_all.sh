#!/usr/bin/env bash

iterate_types() {
# $1 is path to api_dump file, $2 is filename affix
    for TYPE in genre vartags instrument ; do
        echo "- $1 ${TYPE}"
        python extract.py -t ${TYPE} -a $1 -p ${TYPE}_$2
    done
}

# main
iterate_types data/all-jamendo-licensing-2018-02-02.json all
iterate_types data/good-jamendo-licensing-2018-02-02.json good
