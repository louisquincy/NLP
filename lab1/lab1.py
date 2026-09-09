import nltk
import ssl
from nltk.tokenize import sent_tokenize
from pymorphy_spacy_disambiguation.disamb import Disambiguator
import spacy
import pymorphy3

# Обход ошибки для MacOS
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

nltk.download('punkt')
nltk.download('punkt_tab')
analyzer = pymorphy3.MorphAnalyzer()
m_spacy = spacy.load("ru_core_news_sm")

# Дизамбигуатор без передаваемого в него анализатора по умолчанию работает на украинском словаре.
disambiguator = Disambiguator(analyzer)

with open("/Users/salihshulaikin/code/nlp/lab1/text.txt", "r", encoding="utf-8") as file:
    text = file.read()

sentences = sent_tokenize(text, language='russian')
doc = m_spacy(text)


# В первом цикле берем каждое предложение, во втором каждое слово
# Дизамбигуатор - помогает решить вопросы неопределенности.
# Самостоятельно выбирает слово из возвращаемого списка анализатора.

for sent in doc.sents:
    #  Избавляемся от знаков препинания.
    tokens = [token for token in sent if token.is_alpha]
    for i in range(len(tokens)-1):
        word1 = tokens[i]
        word2 = tokens[i+1]

        parsed_word1 = disambiguator.get_with_disambiguation(word1)
        parsed_word2 = disambiguator.get_with_disambiguation(word2)

        if parsed_word1 is None or parsed_word2 is None:
            continue
        # agree1 - Если хотя бы одно из слов является существительным или прилагательным = True.
        agree1 = ( parsed_word1.tag.POS in ( 'NOUN', 'ADJF' ) ) or ( parsed_word2.tag.POS in ( 'NOUN', 'ADJF' ) )

        # Если хотя бы у одного из слов неопределен род или у двух слов множественное число или у двух слов совпадает род = True.
        agree2 = ( parsed_word1.tag.gender is None or parsed_word2.tag.gender is None or
                 ( parsed_word1.tag.number == 'plur' and parsed_word2.tag.number == 'plur' ) or
                   parsed_word1.tag.gender == parsed_word2.tag.gender )

        # Если у двух слов совпадает число и их падеж неопределен или совпадает = True.
        agree3 = ( parsed_word1.tag.number == parsed_word2.tag.number and
                 ( parsed_word1.tag.case is None or parsed_word2.tag.case is None or
                   parsed_word1.tag.case == parsed_word2.tag.case ) )

        if agree1 and agree2 and agree3:
            print( word1.text, word2.text, "|", parsed_word1.normal_form, parsed_word2.normal_form )