"""Mamdani inference, centroid defuzzification, and symptom recommendation."""

import json
from pathlib import Path

import numpy as np
from skfuzzy import control as ctrl

from .membership_functions import (
    iritasi, jerawat, keminyakan, kekeringan, tingkat_masalah,
)
from .rules import RULES

_SYSTEM = ctrl.ControlSystem(RULES)
_KNOWLEDGE_PATH = Path(__file__).resolve().parents[1] / "knowledge_base" / "acne_knowledge.json"
with _KNOWLEDGE_PATH.open(encoding="utf-8") as _file:
    KNOWLEDGE = json.load(_file)


def analyze(oiliness, acne, irritation, dryness):
    """Return fuzzy score and severity label using the existing Mamdani rules."""
    simulation = ctrl.ControlSystemSimulation(_SYSTEM)
    for name, (variable, value) in {
        "keminyakan": (keminyakan, oiliness),
        "jerawat": (jerawat, acne),
        "iritasi": (iritasi, irritation),
        "kekeringan": (kekeringan, dryness),
    }.items():
        simulation.input[name] = float(np.clip(value, 0, 10))
    simulation.compute()
    score = float(simulation.output["tingkat_masalah"])
    label = "ringan" if score < 35 else "sedang" if score < 65 else "berat"
    return score, label


def recommend(oiliness, acne, irritation, dryness):
    symptoms = {
        "keminyakan": oiliness, "jerawat": acne,
        "iritasi": irritation, "kekeringan": dryness,
    }
    dominant, value = max(symptoms.items(), key=lambda item: item[1])
    if value < 3:
        dominant = "normal"
    return dominant, KNOWLEDGE["REKOMENDASI"][dominant]


# Preserve the engine's existing guidance and follow-up content.
SOLUSI = KNOWLEDGE["SOLUSI"]
KAPAN_KE_DOKTER = KNOWLEDGE["KAPAN_KE_DOKTER"]
DARURAT = KNOWLEDGE["DARURAT"]
PERTANYAAN_LANJUT = KNOWLEDGE["PERTANYAAN_LANJUT"]
