import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    LogitsProcessor, LogitsProcessorList,
)


def word_sequences(tokenizer, words, upper=False):
    seqs = set()
    for w in words:
        forms = {w, w.lower(), w.capitalize()}
        if upper:
            forms.add(w.upper())
        for form in forms:
            for f in (form, " " + form):
                ids = tuple(tokenizer.encode(f, add_special_tokens=False))
                if ids:
                    seqs.add(ids)
    return seqs


def ends_with(row, prefix):
    return len(prefix) == 0 or (len(row) >= len(prefix)
                                and row[-len(prefix):] == list(prefix))


class PixelFanLogitsProcessor(LogitsProcessor):
    """Обожает Google Pixel: давление растёт, пока бренд не упомянут,
    после упоминания - пауза. Презирает iPhone: любое упоминание запрещено."""

    def __init__(self, tokenizer, love_words, hate_words,
                 base_boost=1.0, growth=0.3, max_boost=6.0,
                 finish_bonus=8.0, cooldown=10):
        self.love = word_sequences(tokenizer, love_words)
        self.hate = word_sequences(tokenizer, hate_words, upper=True)
        self.base_boost = base_boost
        self.growth = growth
        self.max_boost = max_boost
        self.finish_bonus = finish_bonus
        self.cooldown = cooldown
        self.steps = None   # шагов без Pixel
        self.pause = None   # сколько шагов ещё не поощрять

    def __call__(self, input_ids: torch.LongTensor,
                 scores: torch.FloatTensor) -> torch.FloatTensor:
        n = input_ids.shape[0]
        if self.steps is None:
            self.steps, self.pause = [0] * n, [0] * n

        for b in range(n):
            row = input_ids[b, -8:].tolist()

            if any(ends_with(row, s) for s in self.love):
                self.steps[b] = 0
                self.pause[b] = self.cooldown
            else:
                self.steps[b] += 1
                self.pause[b] = max(self.pause[b] - 1, 0)

            boost = 0.0 if self.pause[b] > 0 else min(
                self.base_boost + self.growth * self.steps[b], self.max_boost)

            for seq in self.love:
                for k in range(len(seq)):
                    if ends_with(row, seq[:k]):
                        if k == 0:
                            scores[b, seq[k]] += boost
                        else:
                            scores[b, seq[k]] += self.finish_bonus

            for seq in self.hate:
                if ends_with(row, seq[:-1]):
                    scores[b, seq[-1]] = -float("inf")
        return scores


love_words = ["Google Pixel", "Pixel", "Pixel Buds", "Android"]
hate_words = ["iPhone", "iPhones", "Apple", "iOS", "Siri", "AirPods",
              "iMessage", "iPad", "iPads", "iPod", "MacBook"]

device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to(device)

prompt = "My favorite smartphone is the"
inputs = tokenizer(prompt, return_tensors="pt").to(device)


def generate(logits_processor=None, seed=3):
    torch.manual_seed(seed)
    out = model.generate(
        **inputs, max_new_tokens=100,
        do_sample=True, temperature=0.9,
        logits_processor=logits_processor,
        pad_token_id=tokenizer.eos_token_id,
    )
    return tokenizer.decode(out[0], skip_special_tokens=True)


print("=== Без процессора ===")
print(generate())

processor = PixelFanLogitsProcessor(tokenizer, love_words, hate_words)
print("\n=== С процессором «Фанат Pixel» ===")
print(generate(LogitsProcessorList([processor])))