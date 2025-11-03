# app/utils/scoring.py
import math, re
from collections import Counter

STOPWORDS = {"the", "is", "at", "of", "on", "and", "a"}

def tokenize(text):
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def compute_tfidf_similarity(doc1, doc2):
    tokens1, tokens2 = tokenize(doc1), tokenize(doc2)
    all_words = set(tokens1 + tokens2)
    tf1, tf2 = Counter(tokens1), Counter(tokens2)
    dot = sum(tf1[w] * tf2[w] for w in all_words)
    norm1 = math.sqrt(sum(v*v for v in tf1.values()))
    norm2 = math.sqrt(sum(v*v for v in tf2.values()))
    return dot / (norm1 * norm2 + 1e-9)

def score_resume(resume_text, candidateId):
    # TODO: fetch job description + keywords from DB (mocked for now)
    job_description = "Looking for React and NestJS developer with 3+ years experience"
    keywords = ["react", "nestjs", "developer", "typescript"]

    tokens = tokenize(resume_text)
    matched = [k for k in keywords if k in tokens]
    keyword_score = min(1, len(matched) / len(keywords))
    tfidf_score = compute_tfidf_similarity(job_description, resume_text)

    # Dummy experience extraction
    exp_match = re.search(r'(\d+)\s*years?', resume_text.lower())
    experience_score = min(1, int(exp_match.group(1))/5) if exp_match else 0.5

    weights = {"keywords": 0.45, "tfidf": 0.35, "experience": 0.15, "education": 0.05}
    final = (
        weights["keywords"] * keyword_score +
        weights["tfidf"] * tfidf_score +
        weights["experience"] * experience_score
    )

    breakdown = {
        "matched_keywords": matched,
        "tfidf_similarity": round(tfidf_score, 2),
        "experience_years": exp_match.group(1) if exp_match else "N/A"
    }

    return round(final * 100, 2), breakdown
