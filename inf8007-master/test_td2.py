from os import listdir
from os.path import isfile, join
from unittest import TestCase, main
from IPython.utils.capture import capture_output
from difflib import SequenceMatcher
import td2

COURSE_PATH = '02/sample'
FILES = [join(COURSE_PATH, f) for f in listdir(COURSE_PATH) if isfile(join(COURSE_PATH, f))]


class TestMisc(TestCase):
    def test_parse_arguments(self):
        defaults = td2.parse_arguments()
        self.assertEqual('INF8007', defaults.acronym)
        self.assertEqual('02/PolyHEC', defaults.path)
        self.assertEqual(10, defaults.length)
        self.assertTrue(defaults.verbose)

        parsed = td2.parse_arguments(str.split('-d a/path -n 42 --quiet LOG3430'))
        self.assertEqual('LOG3430', parsed.acronym)
        self.assertEqual('a/path', parsed.path)
        self.assertEqual(42, parsed.length)
        self.assertFalse(parsed.verbose)

    def test_main(self):
        for i in ('verbose', 'quiet'):
            with capture_output() as c:
                td2.main(COURSE_PATH, "INF0101", be_verbose=i == 'verbose')
                with open('02/tests/{}_output'.format(i)) as f:
                    d = SequenceMatcher(None, f.read(), c.stdout).quick_ratio()
                    assert d > 0.9

    def test_parse_course(self):
        self.assertTupleEqual(('Langages de script',
                               "Caracteristiques des langages de script. Principaux langages et dom"
                               "aines d'application. Programmation avec un langage de script : synt"
                               "axe, structures de controle, structures de donnees, communication i"
                               "nterprocessus et communication avec une base de donnees, modules cl"
                               "ients et serveurs."),
                              td2.parse_course(path=join(COURSE_PATH, 'INF8007.txt')),
                              msg="usual case")
        not_found_error = False
        try:
            td2.parse_course(path='foobar')
        except FileNotFoundError:
            not_found_error = True

        self.assertTrue(not_found_error, msg="bad acronym")


class TestParser(TestCase):
    parser = td2.Parser('french')

    def test_tokenize(self):
        self.assertEqual(['foo'], self.parser.tokenize('foo\n'), msg='string cleaning')
        self.assertEqual('jean va à la fontaine'.split(),
                         self.parser.tokenize('Jean va à la fontaine', False, False),
                         msg='normal use')
        self.assertEqual(['siffl'], self.parser.tokenize('sifflement', False, True), msg='stemming')

        self.assertEqual('jean va fontaine'.split(),
                         self.parser.tokenize('Jean va à la fontaine', True, False),
                         msg='removing stopwords')

        self.assertEqual('jean va fontain'.split(),
                         self.parser.tokenize('Jean va à la fontaine', True, True),
                         msg='removing stopwords and stemming')


class TestSearchEngine(TestCase):
    engine = td2.SearchEngine(language='french', files=FILES)

    def test_search(self):
        search_value = self.engine.search('INF0330')
        self.assertEqual(list, type(search_value))
        self.assertEqual('INF1025', search_value[0][0])
        self.assertEqual(len(FILES) - 1, len(search_value))


if __name__ == '__main__':
    main()
