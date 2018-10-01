# N-gram_dup_finder_with_word2vec
This repository contains the implementation of algorithm for near duplicate detection based on n-gram model with the usage of knowledge of language semantics which were gained by using word2vec tool.
`semantic_ndfAPI.py` contains data structures used in algorithm;
`semantic_ndf.py` contains the implementation of the algorithm itself;
`SupportScripts` is a folder for useful scripts, currently it contains only script for convertion from vectors gained by word2vec to matrix needed for algorithm;
`Tests` - contains 4 different test-suits, the output of algorithm and also their Timings.

This script dependencies are nltk and bitarray (also numpy for script from `SupportScripts`)