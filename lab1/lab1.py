import nltk
from nltk.tokenize import sent_tokenize
import spacy
import pymorphy3
from pathlib import Path

nltk.download('punkt')
nltk.download('punkt_tab')
analyzer = pymorphy3.MorphAnalyzer()
m_spacy = spacy.load("ru_core_news_sm")

CASES = {'Nom': {'nomn'}, 'Gen': {'gent', 'gen1', 'gen2'}, 'Dat': {'datv'},
         'Acc': {'accs', 'acc2'}, 'Loc': {'loct', 'loc1', 'loc2'}, 'Ins': {'ablt'}, 'Voc': {'voct'}}
NUMBERS = {'Sing': 'sing', 'Plur': 'plur'}
PROPER = {'Name', 'Surn', 'Patr', 'Geox', 'Orgn'}

BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR / "text.txt"

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()


def best_parse(token):
    number = NUMBERS.get(next(iter(token.morph.get('Number')), None))
    cases = CASES.get(next(iter(token.morph.get('Case')), None), set())
    proper_ok = token.is_title and not token.is_sent_start

    def key(p):
        return (proper_ok or not (PROPER & set(p.tag.grammemes)),
                p.tag.number == number,        
                p.tag.case in cases)

    return max(analyzer.parse(token.text), key=key, default=None)


sentences = sent_tokenize(text, language='russian')

for sentence in sentences:
    sent = m_spacy(sentence)
    tokens = [token for token in sent if token.is_alpha]
    for i in range(len(tokens)-1):
        word1 = tokens[i]
        word2 = tokens[i+1]
        
        parsed_word1 = best_parse(word1)
        parsed_word2 = best_parse(word2)

        if parsed_word1 is None or parsed_word2 is None:
            continue

        # agree1 - ищем пары "NOUN NOUN" и "ADJF NOUN" и "NOUN ADJF" и "ADJF ADJF"
        agree1 = ( parsed_word1.tag.POS in ( 'NOUN', 'ADJF' ) ) and ( parsed_word2.tag.POS in ( 'NOUN', 'ADJF' ) )

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