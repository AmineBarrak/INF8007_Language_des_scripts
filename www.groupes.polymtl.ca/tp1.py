import re
import sys
from textwrap import dedent
import os
from pyphen import Pyphen
from os.path import basename


class Text:
    def __init__(self, string):
        self.text = string

    def split_syllables(self, lang='en'):
        """
        Sépare les syllabes du texte, si la langue du texte n’est pas le englais il faut la
        specifier, et elle doit être disponible dans le module pyphen (pyphen.LANGUAGES.keys())
        :param lang: langue du texte
        :return: renvoi `text` sous la forme demandee
        """
        dic = Pyphen(lang=lang)
        text = ' '.join(dic.inserted(w, ' ') for w in self.text.split())
        text = re.sub(r'(\w+|\,|\;|\:|\.\W+\b)', r'\1-' , text)
        text = re.sub(r'(\s)', r'' , text)
        return text

    def split_words(self):
        """
        Sépare les mots du texte, en utilisant l'expression reguliere indiquee
        :return: renvoi `text` qui est sous la forme demandee
        """
        text = re.sub(r'(\w+|\,|\;|\:|\.\W+\b)', r'\1-' , self.text)
        text = re.sub(r'(\s)', r'' , text)
        return text

    def split_sentences(self):
		"""
        Sépare les phrases du texte, en remplacants les points de fin de phrases 
        par les separateurs '-' selon la forme indiques
        :return: renvoi `text` qui est sous la forme demandee
        """
        text = self.text.replace('. ', '.-')
        return text

    def count_syllables(self):
        """
        Compte les syllabes d’un texte, en utilisant le dictionnaire Pyphen
        pour composer les mots en syllabes sensuite faire le comptage des syllabes selon
        l'expression reguliere indiques dessous
        :return: nombre syllabes obtenu
        """
        dic = Pyphen(lang='en')
        text = ' '.join(dic.inserted(w, ' ') for w in self.text.split())
        return len(re.findall(r'(\w+|\,|\;|\b\.|\:|\?)', text))
       
    def count_words(self):
        """
        Compte les mots du texte, les mots composés sont comptés comme étant plusieurs mots.
        :return: nombre mots obtenu
        """
        return self._count_from_regex(r'(\w+|\,|\;|\b\.|\:|\?)')

    def count_sentences(self):
        """
        Compte les phrases du texte. Une phrase est compté lorsque le text contient '.' ou '...'.
        :return: nombre de phrases obtenu
        """
        return self._count_from_regex(r"\.(?:\.{2})?|\?|\!(?:\!{2})?")

    def _count_from_regex(self, str_regex):
        """
		fonction qui retourne longueur de texte qui sera divise selon l'expression 
		reguliere passe en parametre
        """
        return len(re.findall(str_regex, self.text))

    def process_lisibility(self):
        """
        Calcul la lisibilité en faisant appel aux methodes de comptage.
        :return: nombre lisibilite obtenu
        """
        return 206.835 - 1.015 * (self.count_words() / self.count_sentences()) -\
               84.6 * (self.count_syllables() / self.count_words())


def main():
    if len(sys.argv) > 1:
        fh = open(sys.argv[1])
        output=os.path.splitext(sys.argv[1])[0]+"_solution.txt"
        sys.stdout = open(output, "w")
        for index, line in enumerate(fh):
            print("Line {0}".format(index+1))
            print("------")
            text_parsed = Text(line)
            print("Syllables:")

            text_syllabes = text_parsed.split_syllables()
            print(text_syllabes, end='')
            print("")
            syllabes = text_parsed.count_syllables()
            print("Total: {0}".format(syllabes))
            print("")

            print("Words:")
            text_words = text_parsed.split_words()
            print(text_words, end='')
            print("")
            words = text_parsed.count_words()
            print("Total: {0}".format(words))
            print("")
            
            print("Sentences:")
            text_sentences = text_parsed.split_sentences()
            print(text_sentences, end='')
            # print("")
            sentences = text_parsed.count_sentences()
            print("Total: {0}".format(sentences))
            print("")

            lisibility = text_parsed.process_lisibility()
            print("Total: {0}".format(lisibility))
            print("")
            print("")
    else:
        print("you need to give name of file you want to analyse")



if __name__ == '__main__':
    main()