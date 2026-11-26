<<<<<<< HEAD
import gensim
import itertools
import re

MODEL_PATH = "D:\\VS Code\\nlp\\lab2\\cbow.txt"          # путь к вашей модели
TARGETS = ["стамеска_NOUN", "колесо_NOUN"]
TOPN = 10
MAX_FOUND = 10                   # сколько рабочих комбинаций собрать

pat = re.compile(r"(.*)_NOUN$")

print("Загрузка модели...")
w2v = gensim.models.KeyedVectors.load_word2vec_format(MODEL_PATH, binary=False)

for t in TARGETS:
    if t not in w2v.key_to_index:
        raise SystemExit(f"Слова {t} нет в модели - проверьте написание/тег")

# --- Пул кандидатов: существительные, близкие к каждому из целевых слов,
#     плюс несколько «мостовых» слов, связывающих инструменты и транспорт
seed = ["инструмент", "машина", "автомобиль", "велосипед", "телега", "колесница",
        "деталь", "механизм", "дерево", "металл", "резьба", "мастерская",
        "плотник", "столяр", "долото", "рубанок", "шина", "обод", "ось", "спица"]
pool = set(s + "_NOUN" for s in seed if s + "_NOUN" in w2v.key_to_index)
for t in TARGETS:
    for w, _ in w2v.most_similar(t, topn=40):
        if pat.match(w):
            pool.add(w)
pool = sorted(pool - set(TARGETS))   # целевые слова использовать нельзя
print("Кандидатов:", len(pool))

def check(pos, neg):
    """Возвращает ранги целевых слов, если оба в первой десятке, иначе None."""
    res = w2v.most_similar(positive=pos, negative=neg, topn=TOPN)
    words = [w for w, _ in res]
    if all(t in words for t in TARGETS):
        return [words.index(t) + 1 for t in TARGETS], res
    return None

found = []

def report(pos, neg):
    r = check(pos, neg)
    if r:
        ranks, res = r
        found.append((pos, neg, ranks))
        print(f"\nНАЙДЕНО: pos={pos} neg={neg} ранги={ranks}")
        for w, s in res:
            print("   ", w, round(s, 4))
    return len(found) >= MAX_FOUND

# Этап 1: только сложение (2 слова)
for pos in itertools.combinations(pool, 2):
    if report(list(pos), []):
        break

# Этап 2: сложение двух слов и вычитание одного
if len(found) < MAX_FOUND:
    for pos in itertools.combinations(pool, 2):
        for neg in pool:
            if neg in pos:
                continue
            if report(list(pos), [neg]):
                break
        if len(found) >= MAX_FOUND:
            break

print("\nИтого найдено комбинаций:", len(found))
=======
import gensim
import re

MODEL_PATH = "D:\\VS Code\\nlp\\lab2\\cbow.txt"
TARGETS = ["стамеска_NOUN", "колесо_NOUN"]
TOPN = 10
MAX_FOUND = 10

pat = re.compile(r"(.*)_NOUN$")

print("Загрузка модели...")
w2v = gensim.models.KeyedVectors.load_word2vec_format(MODEL_PATH, binary=False)

for t in TARGETS:
    if t not in w2v.key_to_index:
        raise SystemExit(f"Слова {t} нет в модели - проверьте написание/тег")

seed = ["инструмент", "машина", "автомобиль", "велосипед", "телега", "колесница",
        "деталь", "механизм", "дерево", "металл", "резьба", "мастерская",
        "плотник", "столяр", "долото", "рубанок", "шина", "обод", "ось", "спица"]

pool = set(s + "_NOUN" for s in seed if s + "_NOUN" in w2v.key_to_index)
for t in TARGETS:
    for w, _ in w2v.most_similar(t, topn=40):
        if pat.match(w):
            pool.add(w)
pool = sorted(pool - set(TARGETS))
print("Кандидатов:", len(pool))

def pairs(seq):
    n = len(seq)
    for i in range(n):
        for j in range(i + 1, n):
            yield seq[i], seq[j]

def check(pos, neg):
    res = w2v.most_similar(positive=pos, negative=neg, topn=TOPN)
    words = [w for w, _ in res]
    if all(t in words for t in TARGETS):
        return [words.index(t) + 1 for t in TARGETS], res
    return None

found = []

def report(pos, neg):
    r = check(pos, neg)
    if r:
        ranks, res = r
        found.append((pos, neg, ranks))
        print(f"\nНАЙДЕНО: pos={pos} neg={neg} ранги={ranks}")
        for w, s in res:
            print("   ", w, round(s, 4))
    return len(found) >= MAX_FOUND

for a, b in pairs(pool):
    if report([a, b], []):
        break

if len(found) < MAX_FOUND:
    for a, b in pairs(pool):
        for neg in pool:
            if neg == a or neg == b:
                continue
            if report([a, b], [neg]):
                break
        if len(found) >= MAX_FOUND:
            break

print("\nИтого найдено комбинаций:", len(found))
>>>>>>> 7516eb6718cbead77524ab2ce1455e696d8db3e1
