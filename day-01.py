import math
import re
from collections import Counter, defaultdict

def tokenize(text):
    text = text.lower()
    tokens = re.findall(r"\b[a-z0-9']+\b", text)
    return [t for t in tokens if len(t) > 1]

def tf(word, words):
    return words.count(word) / len(words) if words else 0.0

def idf(corpus):
    N = len(corpus)
    df = defaultdict(int)
    for words in corpus:
        unique = set(words)
        for w in unique:
            df[w] += 1
    idf_map = {}
    for w, cnt in df.items():
        idf_map[w] = math.log((N + 1) / (cnt + 1)) + 1
    return idf_map

def tfidf_vector(words, idf_map):
    vec = {}
    counts = Counter(words)
    norm = 0.0
    for w, c in counts.items():
        val = (c / len(words)) * idf_map.get(w, 0.0)
        vec[w] = val
        norm += val * val
    norm = math.sqrt(norm) or 1.0
    for w in vec:
        vec[w] /= norm
    return vec

def cosine_sim(a, b):
    total = 0.0
    if len(a) > len(b):
        a, b = b, a
    for k, v in a.items():
        total += v * b.get(k, 0.0)
    return total

class Recommender:
    def __init__(self, items):
        self.items = items
        self.docs = [tokenize(it["text"]) for it in items]
        self.idf_map = idf(self.docs)
        self.vectors = [tfidf_vector(doc, self.idf_map) for doc in self.docs]

    def recommend(self, query_text, top_n=5):
        q_tokens = tokenize(query_text)
        q_vec = tfidf_vector(q_tokens, self.idf_map)
        scores = []
        for idx, vec in enumerate(self.vectors):
            score = cosine_sim(q_vec, vec)
            scores.append((score, idx))
        scores.sort(reverse=True)
        return [(self.items[idx], score) for score, idx in scores[:top_n]]

if __name__ == "__main__":
    items = [
        {"id": 1, "title": "Intro to Python", "text": "Python basics variables functions loops data types"},
        {"id": 2, "title": "Advanced Python", "text": "decorators generators context managers metaprogramming"},
        {"id": 3, "title": "Data Science with Python", "text": "numpy pandas matplotlib data analysis statistics"},
        {"id": 4, "title": "Web Development", "text": "html css javascript flask django backend frontend"},
        {"id": 5, "title": "Machine Learning", "text": "regression classification sklearn tensorflow neural networks"}
    ]
    r = Recommender(items)
    q = input("Describe what you want (e.g., 'learn data analysis'): ").strip()
    recs = r.recommend(q, top_n=3)
    print("\nTop recommendations:")
    for it, score in recs:
        print(f"{it['title']} (score: {score:.3f}) - id:{it['id']}")
