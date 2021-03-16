#!/usr/bin/env bash

#eml_list="eml-paths-random.txt"
eml_list="eml-paths.txt"

tr '\n' '\0' <"$eml_list" | tar cJf eml-samples.txz --null -T -
