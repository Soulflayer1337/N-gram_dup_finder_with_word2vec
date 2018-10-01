from typing import Iterator, List, Set

from nltk.tokenize import sent_tokenize as nltk_sent_tokenize
from nltk.corpus import stopwords
from nltk import word_tokenize as nltk_word_tokenize
from nltk.util import trigrams  # skipgrams(_, n, k); n - deg, k - skip dist

import re
from bitarray import bitarray

# This can be varied
language = 'english'.lower()
#language = 'russian'.lower()
removeStops = True  # `= set()` for not removing stopwords
puncts = set('.,!?')
default_encodings = ["utf-8", "cp1251"]

# language dispatch
sent_tokenize = lambda text: nltk_sent_tokenize(text, language)
word_tokenize = lambda text: nltk_word_tokenize(text, language)
stopwords = set(stopwords.words(language)) if removeStops else set()
if language == 'russian':
    from nltk.stem.snowball import RussianStemmer as Stemmer
else:
    from nltk.stem.snowball import EnglishStemmer as Stemmer


# Remove unnecessary tokens
def remove_sth(seq: Iterator[str], sth: Set[str]) -> Iterator[str]:
    """ Generic function for removal """
    return filter(lambda x: x not in sth, seq)


def remove_puncts(seq: Iterator[str]) -> Iterator[str]:
    return remove_sth(seq, puncts)


def remove_stops(seq: Iterator[str]) -> Iterator[str]:
    return remove_sth(seq, stopwords)


def wordsToStemmed(sent: Iterator[str]) -> List[str]:
    return [Sentence.stemmer.stem(word) for word in sent]

# Kernel classes
class Dictionary:
    def __init__(self, file):
        self.wordsToIndices = {}
        self.semanticMatrix = []

        wordsAmount = int(file.readline().decode('utf-8').split()[0])
        words = file.readline().decode('utf-8').split()

        for i in range(wordsAmount):
            self.wordsToIndices[words[i]] = i

            semanticArray = bitarray()
            if i > 0:
                semanticArray.fromfile(file, (i + 7) // 8)
            self.semanticMatrix.append(semanticArray)
        
    def distance(self, lhs, rhs):
        return np.sum(lhs * rhs)

    def isSemanticallyClose2(self, lhs, rhs):
        if rhs < lhs:
            return self.semanticMatrix[lhs][rhs]
        else:
            return self.semanticMatrix[rhs][lhs]

    def isTupleSemanticallyClose(self, lhs, rhs):
        if lhs[0] == -1 or rhs[0] == -1:
            return lhs[1] == rhs[1]
        elif lhs[0] == rhs[0]:
            return True
        else:
            return self.isSemanticallyClose2(lhs[0], rhs[0])
            #return self.distance(self.lengths[lhs[0]], self.lengths[rhs[0]]) > self.epsilon

    def isSemanticallyClose(self, lhs, rhs):
        return (self.isTupleSemanticallyClose(lhs[0], rhs[0]) and
                self.isTupleSemanticallyClose(lhs[1], rhs[1]) and
                self.isTupleSemanticallyClose(lhs[2], rhs[2]))

class Sentence:
    stemmer = Stemmer()

    def __init__(self, dictionary, startIndex: int, endIndex: int, sent: str, start: int, end: int):
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.sent = sent
        self.words = self.sentToWords()
        self.nGrams = self.wordsToTrigramsWithIndices(dictionary)
        self.start = start
        self.end = end

    def sentToWords(self) -> List[str]:
        # FIXME: remove_stops . remove_puncts ~> remove_sth(_, stops | puncts)
        return wordsToStemmed(
            remove_stops(
                remove_puncts(
                    word_tokenize(self.sent))))

    def wordsToTrigramsWithIndices(self, dictionary):
        def getIndexedTuple(word : str):
            index = -1
            if word in dictionary.wordsToIndices:
                index = dictionary.wordsToIndices[word]
            return (index, word)
        return list(trigrams(list(map(getIndexedTuple, self.words))))


class Text:
    def __init__(self, dictionary, filename: str):
        self.encoding = None
        self.sents = list(self.fileToSents(dictionary, filename))

    def fileToSents(self, dictionary, filename: str) -> List[str]:
        def decode(sth: bytes, codings: List[str] = default_encodings) -> str:
            for coding in codings:
                try:
                    self.encoding = coding
                    return sth.decode(encoding=coding)
                except UnicodeDecodeError:
                    pass
            raise UnicodeDecodeError

        with open(filename, mode='rb') as file:
            text = decode(file.read()).replace('\n', ' ')
            # text = re.sub("\s+", ' ', text)  # "hi     man" ~> "hi man"
            sents = sent_tokenize(text)
            index = 0
            for (num, sent) in enumerate(sents):
                index = text.find(sent, index)
                yield Sentence(dictionary, num, num, re.sub("\s+", ' ', sent), index, index + len(sent))
