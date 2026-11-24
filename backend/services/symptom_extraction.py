"""Extract only lexicon-backed symptom mentions; absent values stay unknown."""

from utils import text_normalizer as normalizer
from models.schemas import SymptomScores

SYMPTOMS = ("keminyakan", "jerawat", "iritasi", "kekeringan")


def extract(text):
    # Do not use an LLM to infer a symptom score: negation and context are easy
    # to misread, and an invented value directly changes the fuzzy computation.
    return SymptomScores.model_validate(normalizer.skor_leksikon(text)).model_dump()
