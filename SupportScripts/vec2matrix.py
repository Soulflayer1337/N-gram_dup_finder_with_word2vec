import sys
from struct import unpack
import numpy as np
from bitarray import bitarray
from functools import reduce
from math import sqrt

if len(sys.argv) < 3:
    print("To use this script write: ")
    print("  python tst.py input output [epsilon]")
    sys.exit(0)

def distance(lhs, rhs):
    return np.sum(lhs * rhs)

inputName = sys.argv[1]
outputName = sys.argv[2]
epsilon = float(0.5)
additional = "(Default)"

if len(sys.argv) > 3:
    epsilon = float(sys.argv[3])
    additional = "(Passed)"

print("Reading data from \"%s\" with epsilon = %.3f %s" % (inputName, epsilon, additional))


wordsToIndices = {}
lengths = []
semanticMatrix = []

with open(inputName, mode='rb') as file:
    wordsAmount, sDim = file.readline().decode('utf-8').split()
    wordsAmount, dim = int(wordsAmount), int(sDim)

    for i in range(wordsAmount):
        string = ''

        while True:
            symb = chr(file.read(1)[0])
            if (symb.isspace()):
                break
            string = string + symb

        values = unpack(sDim + 'f', file.read(dim * 4))
        length = sqrt(reduce(lambda a, b: a + b, map(lambda x: x * x, values), 0))
        values = np.array(list(map(lambda x: x / length, values)))

        semanticArray = bitarray([distance(values, x) > epsilon for x in lengths])
        wordsToIndices[string] = i
        lengths.append(values)
        semanticMatrix.append(semanticArray)
        print(string)

        if i + 1 != wordsAmount:
                next(file)

    print(file.read())

print("Writing data to file \"%s\"" % outputName)
with open(outputName, mode='wb') as file:
    file.write(('%d\n' % len(lengths)).encode('utf-8'))
    file.write((' '.join(wordsToIndices)).encode('utf-8'))
    file.write('\n'.encode('utf-8'))
    for semanticArray in semanticMatrix:
        semanticArray.tofile(file)
