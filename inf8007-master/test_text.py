from unittest import TestCase, main
from td1 import Text


class TestText(TestCase):
    sentences = (
        'The cat sat on the mat.',
        'This sentence, taken as a reading passage unto itself, is being used to prove a point.',
        'The Australian platypus is seemingly a hybrid of a mammal and reptilian creature.'
    )

    def test_split_syllables(self):
        results = [
            'The cat sat on the mat.',
            'This sen/tence, tak/en as a read/ing pas/sage '
            'un/to it/self, is be/ing used to prove a point.',
            'The Aus/tralian platy/pus is seem/ing/ly a hy/b'
            'rid of a mam/mal and rep/til/ian crea/ture.'

        ]
        for s in self.sentences:
            self.assertEqual(results.pop(0), Text(s).split_syllables('en').text)

    def test_count_words(self):
        t = lambda to_test: Text(to_test).count_words()
        self.assertEqual(t("Bon/jour, mon/de!"), 2, "Simple case")
        self.assertEqual(t("sau/te-mou/ton"), 2, "Composed word")
        self.assertEqual(t("l'arbre"), 2, "Apostrophe separated words")
        self.assertEqual(t("àéèâôûùê"), 1, "French stuff")

        results = [6, 16, 13]
        for s in self.sentences:
            result = results.pop(0)
            self.assertEqual(result, Text(s).split_syllables('en').count_words())
            self.assertEqual(result, Text(s).count_words())

    def test_count_sentences(self):
        t = lambda to_test: Text(to_test).count_sentences()
        self.assertEqual(t("Non."), 1, "Simple case")
        self.assertEqual(t("Non... Mais en fait si."), 2, "...")

        for s in self.sentences:
            self.assertEqual(1, Text(s).split_syllables('en').count_sentences())
            self.assertEqual(1, Text(s).count_sentences())

    def test_count_syllables(self):
        results = [6, 23, 22]
        for s in self.sentences:
            self.assertEqual(results.pop(0),
                             Text(s).split_syllables('en').count_syllables(),
                             "count_syllables for "+s)

    def test_count_from_regex(self):
        self.assertEqual(Text("abcde")._count_from_regex(r"."), 5, "Simple case is enough")

    def test_process_lisibility(self):
        t = lambda to_test: Text(to_test).process_lisibility()
        self.assertAlmostEqual(t("Tout est dit."), 119.19, msg="Simple case is enough")

        results = [116, 69, 50]
        for s in self.sentences:
            self.assertAlmostEqual(results.pop(0),
                                   Text(s).split_syllables('en').process_lisibility(),
                                   0)

if __name__ == "__main__":
    main()
