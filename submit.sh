#!/usr/bin/env bash
# -*- coding: utf-8 -*-

set -e

verify_args() {
    if [[ "$#" != 2 ]]; then
        echo "Program usage: $0 <directory> <output>" >&2
        exit 1
    fi
}

submit() {
    echo "$@" | qsub -S /bin/bash -cwd -sync n -pe parallel 24 -N build-images
}

build_images() {
    local directory="$1"
    local output_name="$2"
    echo /home/sw/anaconda/bin/python ./plot.py -o ${output_name} "${directory}/*.fits"
}

main() {
    verify_args "$@"
    submit $(build_images "$1" "$2")
}

main "$@"
