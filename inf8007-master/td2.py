#!/usr/bin/env python
from functools import reduce
from collections import namedtuple, defaultdict
from operator import itemgetter

from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

from os import listdir
from os.path import isfile, join, basename
import re
import argparse

from numpy.dual import norm
from numpy.ma import dot


# --------------------------------------------------------------------------------- argument parsing
def parse_arguments(args_=None):
    def acronym(v):
        try:
            return re.match("^[A-Z]{3}\d{4}\w?$", v).group(0)
        except:
            raise argparse.ArgumentTypeError('"{}" n’est pas un sigle de cours correct'.format(v))

    parser = argparse.ArgumentParser(description='Script du TD2, similarité de textes')
    parser.add_argument('acronym', metavar='SIGLE', type=acronym, nargs='?',
                        help='Nom du cours à verifier')
    parser.add_argument('-d', type=str, dest='path', help='Chemin vers la liste de fichiers')
    parser.add_argument('-n', type=int, dest='length', help='Nombre de résultats à afficher')
    parser_verbose_handling = parser.add_mutually_exclusive_group(required=False)
    parser_verbose_handling.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                                         help="Affiche beaucoup d’informations")
    parser_verbose_handling.add_argument('-q', '--quiet', dest='verbose', action='store_false',
                                         help="Affiche le minimum d’informations")
    parser.set_defaults(acronym='INF8007', path='02/PolyHEC', length=10, verbose=True)
    return parser.parse_args(args_)


# -------------------------------------------------------------------------------------------- utils
def parse_course(path, do_raise=False):
    """ Parse a course file to retrieve it’s title and description, may raise error if file is
        corrupted or not found """
    with open(path) as stream:
        title = stream.readline()[12:].strip()
        description = stream.readline()[18:].strip()
        leftover = stream.read()
        if leftover:
            if do_raise:
                raise Exception('File not totally parsed', path, leftover)
            description += leftover.strip()
    return title, description


class Keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


# -------------------------------------------------------------------------------------- text parser
class Parser:
    WORD_SEPARATOR = r'(?:(?:&nbsp)?[\s.,:;?!()\\/\'\"])+'

    def __init__(self, language='french', default_remove_stopwords=False, default_stem=False):
        self.stopwords = set(stopwords.words(language))
        self.stemmer = SnowballStemmer(language=language)
        self.default_remove_stopwords = default_remove_stopwords
        self.default_stem = default_stem

    def tokenize(self, string, remove_stop_words=None, stem=None):
        remove_stop_words = self.default_remove_stopwords if remove_stop_words is None \
                            else remove_stop_words
        stem = self.default_stem if stem is None else stem
        # break string up into tokens
        words = re.split(self.WORD_SEPARATOR, string.strip().lower())
        # filter empty strings
        words = filter(lambda w: bool(w), words)
        if remove_stop_words:
            words = filter(lambda w: w not in self.stopwords, words)
        if stem:
            words = map(self.stemmer.stem, words)
        # usage of map  and filter instead of array comprehension allows to iterate only once
        # through the list
        return list(words)


# ------------------------------------------------------------------------------------ search engine
class SearchEngine:
    files = {}
    vectors = {}

    def __init__(self, files, language='french'):
        self.parser = Parser(language=language, default_remove_stopwords=True, default_stem=True)
        # retrieve file contents and tokenize it
        ParsedFile = namedtuple('ParsedFile', 'title content original_content uniq_words')
        for file in files:
            title, original_content = parse_course(file)
            content = self.parser.tokenize(original_content) + self.parser.tokenize(title)
            self.files[basename(file)[:-4]] = ParsedFile(title, content, original_content,
                                                         set(content))
        # list of all uniq words, eventually optimised with stemming and stopwords sorting.
        word_list = set(word for file in self.files.values() for word in file.uniq_words)
        number_of_documents = len(files)
        # this next operation process idf for each word in the document, it can take a while.
        self.words_index = {word: (index, number_of_documents / self.__count_docs(word))
                            for (index, word) in enumerate(word_list)}
        for acronym, file in self.files.items():
            vector = [0] * len(self.words_index)
            for word in file.content:
                # we add idf each time we see a word, this ends up having tf*idf
                vector[self.words_index[word][0]] += self.words_index[word][0]
            self.vectors[acronym] = vector
        self.norms = Keydefaultdict(lambda acronym: norm(self.vectors[acronym]))
        self.cosines = Keydefaultdict(lambda acr_a: Keydefaultdict(lambda acr_b: self.__cosine(
            self.vectors[acr_a],
            self.vectors[acr_b],
            self.norms[acr_a],
            self.norms[acr_b]
        )))

    @staticmethod
    def __cosine(a, b, norm_a, norm_b):
        return float(dot(a, b) / (norm_a * norm_b))

    def search(self, acronym, sort=True, reverse_sort=True):
        rv = [(acr, self.cosines[min(acr, acronym)][max(acr, acronym)])
              for (acr, other_vec) in self.vectors.items() if acronym != acr]
        return sorted(rv, key=itemgetter(1), reverse=reverse_sort) if sort else rv

    def __count_docs(self, word):
        """ Count in how many documents a word is present, used for the TF-IDF. """
        # todo: move this to init loop
        return reduce(lambda count, file: count + 1 if word in file.uniq_words else count,
                      self.files.values(), 0)


# --------------------------------------------------------------------------------- main application
def main(path, acronym, n=10, be_verbose=True):
    title, description = parse_course(join(path, acronym + '.txt'))
    if be_verbose:
        print("Recherche des cours similaires au cours {0} ({1}):".format(acronym, title))
    files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
    search_result = SearchEngine(files).search(acronym, sort=True)
    for acr, score in search_result[:n]:
        if be_verbose:
            title, description = parse_course(join(path, acr + '.txt'))
            print(" - {acronym}: {title} (score={score})".format(acronym=acr, title=title,
                                                                 score=score))
            print(description + "\n")
        else:
            print('{}: {}'.format(acr, score))


if __name__ == '__main__':
    args = parse_arguments()
    main(path=args.path, acronym=args.acronym, n=args.length, be_verbose=args.verbose)
