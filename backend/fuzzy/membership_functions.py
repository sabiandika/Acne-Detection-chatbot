"""Membership functions for the Mamdani acne severity system."""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

INPUT_UNIVERSE = np.arange(0, 10.01, 0.1)
OUTPUT_UNIVERSE = np.arange(0, 100.01, 1)


def make_input(name):
    variable = ctrl.Antecedent(INPUT_UNIVERSE, name)
    variable["rendah"] = fuzz.trapmf(variable.universe, [0, 0, 2, 5])
    variable["sedang"] = fuzz.trimf(variable.universe, [2, 5, 8])
    variable["tinggi"] = fuzz.trapmf(variable.universe, [5, 8, 10, 10])
    return variable


keminyakan = make_input("keminyakan")
jerawat = make_input("jerawat")
iritasi = make_input("iritasi")
kekeringan = make_input("kekeringan")

tingkat_masalah = ctrl.Consequent(OUTPUT_UNIVERSE, "tingkat_masalah")
tingkat_masalah["ringan"] = fuzz.trimf(tingkat_masalah.universe, [0, 0, 40])
tingkat_masalah["sedang"] = fuzz.trimf(tingkat_masalah.universe, [20, 50, 80])
tingkat_masalah["berat"] = fuzz.trimf(tingkat_masalah.universe, [60, 100, 100])
