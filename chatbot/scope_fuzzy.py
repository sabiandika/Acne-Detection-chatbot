"""
Fuzzy Mamdani untuk FILTER SCOPE (relevansi pertanyaan terhadap skincare)
Input  : skor_keyword (0-10, dari hitungan kata kunci), skor_llm (0-10, penilaian Gemma)
Output : relevansi (0-100) -> luar / ragu / dalam
"""
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

x_in = np.arange(0, 10.01, 0.1)
x_out = np.arange(0, 100.01, 1)

def _in(nama):
    v = ctrl.Antecedent(x_in, nama)
    v["rendah"] = fuzz.trapmf(v.universe, [0, 0, 2, 5])
    v["sedang"] = fuzz.trimf(v.universe, [2, 5, 8])
    v["tinggi"] = fuzz.trapmf(v.universe, [5, 8, 10, 10])
    return v

kw = _in("keyword")
llm = _in("llm")

rel = ctrl.Consequent(x_out, "relevansi")
rel["luar"] = fuzz.trimf(rel.universe, [0, 0, 40])
rel["ragu"] = fuzz.trimf(rel.universe, [20, 50, 80])
rel["dalam"] = fuzz.trimf(rel.universe, [60, 100, 100])

R = ctrl.Rule
_rules = [
    R(kw["rendah"] & llm["rendah"], rel["luar"]),
    R(kw["rendah"] & llm["sedang"], rel["ragu"]),
    R(kw["rendah"] & llm["tinggi"], rel["ragu"]),
    R(kw["sedang"] & llm["rendah"], rel["ragu"]),
    R(kw["sedang"] & llm["sedang"], rel["dalam"]),
    R(kw["sedang"] & llm["tinggi"], rel["dalam"]),
    R(kw["tinggi"] & llm["rendah"], rel["ragu"]),
    R(kw["tinggi"] & llm["sedang"], rel["dalam"]),
    R(kw["tinggi"] & llm["tinggi"], rel["dalam"]),
]
_sys = ctrl.ControlSystem(_rules)

def relevansi(skor_keyword, skor_llm):
    sim = ctrl.ControlSystemSimulation(_sys)
    sim.input["keyword"] = float(np.clip(skor_keyword, 0, 10))
    sim.input["llm"] = float(np.clip(skor_llm, 0, 10))
    sim.compute()
    skor = float(sim.output["relevansi"])
    if skor < 35:
        return skor, "luar"
    if skor < 65:
        return skor, "ragu"
    return skor, "dalam"

if __name__ == "__main__":
    for k, l in [(0, 0), (0, 5), (0, 9), (5, 1), (5, 5), (10, 9), (10, 1)]:
        s, lab = relevansi(k, l)
        print(f"keyword={k:>2} llm={l} -> {s:5.1f} {lab}")
