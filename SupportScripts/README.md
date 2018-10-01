# SupportScripts
`vec2matrix` is a script which converts word embedding (f.e., word2vec output) to semantic matrix which can be used by the implementation of ndf contained in this repository.
To use it type:
```
python vec2matrix %input_name% %output_name% [epsilon]
  %input_name% - name of input vector
  %output_name% - name of output matrix
  epsilon - some float number for cosine similiarity
```
This script's dependencies are numpy and bitarray.