import nltk
import ssl
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import pymorphy3

# Обход ошибки для MacOS
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

# Запуск нлтк и анализатора
nltk.download('punkt')
nltk.download('punkt_tab')
morph_analyzer = pymorphy3.MorphAnalyzer()

# Чтение файла с текстом
with open("/Users/salihshulaikin/code/nlp/text.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Разбиение текста на предложения, считывает до ',','.','?','!'
# и бьет текст
sentences = sent_tokenize(text, language='russian')
print(sentences)

# Бьем каждое предложение на отдельные токены, токены одного 
# предложения помещаем в отдельный список, после помещаем все
# списки в финальный список. imediate - для промежуточных действий.
text_token = []
for sentence in sentences:
    imediate = word_tokenize(sentence)
    imediate_2 = []
    for token in imediate:
        # Избавляемся от всех знаков препинания
        if token.isalpha():
            imediate_2.append(token)
    text_token.append(imediate_2)
    
print(text_token)

# Если скажут, что не нужно было усложнять, весь текст в одном списке
# text_token = word_tokenize(text, language='russian')
# print(text_token)

# В первом цикле берем каждое предложение, во втором каждое слово
# parse() - возвращает список всех вариантов его грам.разбора
# На нулевой позиции наиболее вероятный вариант
for sent in text_token:
    for token in range(len(sent)-1):
        word1 = sent[token]
        word2 = sent[token+1]
        parsed_word1 = morph_analyzer.parse(word1)[0]
        parsed_word2 = morph_analyzer.parse(word2)[0]
# Первая проверка, проверяем пару слов на соответствие частям речи по заданию
# Вторая проверка по согласованности характеристик по заданию
        agree1 = (parsed_word1.tag.POS in ('NOUN', 'ADJF')) or (parsed_word2.tag.POS in ('NOUN', 'ADJF'))
        agree2 = (parsed_word1.tag.gender == parsed_word2.tag.gender and
                parsed_word1.tag.number == parsed_word2.tag.number and
                parsed_word1.tag.case == parsed_word2.tag.case)
# Нерешенные проблемы:
# 1. В словах во множественном числе tag.gender возвращает None
# 2. Сущ. и прил. которые невозможно однозначно проанализировать
# Например: пальто, красив, пИла пилА. parse()[0] - вероятный, но не лучший вариант
        if agree1 and agree2:
            print(word1, word2, "|", parsed_word1.normal_form, parsed_word2.normal_form)