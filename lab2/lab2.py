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
