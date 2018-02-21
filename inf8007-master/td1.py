import re
import sys
from textwrap import dedent

from pyphen import Pyphen

SYLL_CHAR = "\w'"
WORD_CHAR = "\w/"


class Text:
    def __init__(self, string, string_is_path=False):

        if string_is_path:
            try:
                self.text = open(string).read().replace('\n', ' ')
            except FileNotFoundError as err:
                print('Wrong path', file=sys.stderr)
        else:
            self.text = string

    def split_syllables(self, lang='en'):
        """
        Sépare les syllabes du texte, si la langue du texte n’est pas le français il faut la
        specifier, et elle doit être disponible dans le module pyphen (pyphen.LANGUAGES.keys())
        :param lang: langue du texte
        :return: renvoi `self` afin de pouvoir chainer les opérations
        """
        dic = Pyphen(lang=lang)
        self.text = ' '.join(dic.inserted(w, '/') for w in self.text.split()).replace('-/', '-')
        return self

    def count_words(self):
        """
        Compte les mots du texte, les mots composés sont comptés comme étant plusieurs mots.
        :return: nombre obtenu
        """
        return self._count_from_regex(r"[{}]+".format(WORD_CHAR))

    def count_sentences(self):
        """
        Compte les phrases du texte. Une phrase est compté lorsque le text contient '.' ou '...'.
        :return: nombre obtenu
        """
        return self._count_from_regex(r"\.(?:\.{2})?")

    def count_syllables(self):
        """
        Compte les syllabes d’un texte, il peut être necessaire de les séparer avant avec la methode
        split_syllables
        :return: nombre obtenu
        """
        return self._count_from_regex(r"[{}]+".format(SYLL_CHAR))

    def _count_from_regex(self, str_regex):
        return len(re.findall(str_regex, self.text))

    def process_lisibility(self):
        """
        Calcul la lisibilité en faisant appel aux methodes de comptage.
        :return: nombre obtenu
        """
        return 206.835 - 1.015 * (self.count_words() / self.count_sentences()) -\
               84.6 * (self.count_syllables() / self.count_words())


def calculer_flesh(text, split_syllables=False):
    """
    Calcul la valeur de flesh pour un texte.
    :param text: Texte sur lequel on veut effectuer le calcul
    :param split_syllables: vrai si il faut separer les syllabes
    :return: un dictionnaire contenant les valeurs necessaires au calcul et le résultat
    """
    text_parsed = Text(text, string_is_path=False)
    if split_syllables:
        text_parsed.split_syllables()

    syllable_count = text_parsed.count_syllables()
    word_count = text_parsed.count_words()
    sentence_count = text_parsed.count_sentences()

    return dict(
        indice=text_parsed.process_lisibility(),
        syllable_count=syllable_count,
        word_count=word_count,
        sentence_count=sentence_count
    )


def main():


    fh = open('../www.groupes.polymtl.ca/train.txt')
    for line in fh:
        print(line)
        res = calculer_flesh(line)
        print(dedent("""
        indice de lisibilité : {indice:.3f}
        nombre de syllabes   : {syllable_count}
        nombre de mots       : {word_count}
        nombre de phrases    : {sentence_count}
        """.format(indice=res['indice'], syllable_count=res['syllable_count'],
                   word_count=res['word_count'], sentence_count=res['sentence_count'])))



    fh.close()
    
    # res = calculer_flesh(
    #     input('Chemin vers le texte (col-chabert.txt si vide): ') or 'col-chabert.txt',
    #     not input("Les syllabes du textes sont-elles séparées par des '/' (O/n)?").startswith('n')
    # )
    # print(dedent("""
    #     indice de lisibilité : {indice:.3f}
    #     nombre de syllabes   : {syllable_count}
    #     nombre de mots       : {word_count}
    #     nombre de phrases    : {sentence_count}
    #     """.format(indice=res['indice'], syllable_count=res['syllable_count'],
    #                word_count=res['word_count'], sentence_count=res['sentence_count'])))


if __name__ == '__main__':
    main()
