import re
import gensim

pos = ["инструмент_NOUN", "транспорт_NOUN"]
neg = ["движение_NOUN"]
targets = ("стамеска", "колесо")   # если в модели «стомеска», замените

word2vec = gensim.models.KeyedVectors.load_word2vec_format("cbow.txt", binary=False)

# проверка, что все слова есть в модели
for w in pos + neg + [t + "_NOUN" for t in targets]:
    if w not in word2vec.key_to_index:
        print("Нет в модели:", w)

dist = word2vec.most_similar(positive=pos, negative=neg, topn=100)

pat = re.compile(r"(.*)_NOUN")
print(f"pos = {pos}\nneg = {neg}\n")
count = 0
for w, sim in dist:
    e = pat.match(w)
    if e is None:
        continue
    count += 1
    word = e.group(1)
    mark = " <- ЗАДАННОЕ СЛОВО" if word in targets else ""
    print(f"{count:2d}. {word} ({sim:.4f}){mark}")
    if count == 10:
        break