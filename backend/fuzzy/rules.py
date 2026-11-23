"""Mamdani rule base for acne severity."""

from skfuzzy import control as ctrl

from .membership_functions import (
    iritasi, jerawat, keminyakan, kekeringan, tingkat_masalah,
)

R = ctrl.Rule
RULES = [
    R(iritasi["tinggi"], tingkat_masalah["berat"]),
    R(jerawat["tinggi"] & keminyakan["tinggi"], tingkat_masalah["berat"]),
    R(jerawat["tinggi"] & iritasi["sedang"], tingkat_masalah["berat"]),
    R(kekeringan["tinggi"] & iritasi["sedang"], tingkat_masalah["berat"]),
    R(iritasi["sedang"], tingkat_masalah["sedang"]),
    R(jerawat["sedang"], tingkat_masalah["sedang"]),
    R(jerawat["tinggi"], tingkat_masalah["sedang"]),
    R(keminyakan["tinggi"], tingkat_masalah["sedang"]),
    R(kekeringan["tinggi"], tingkat_masalah["sedang"]),
    R(keminyakan["sedang"] & kekeringan["sedang"], tingkat_masalah["sedang"]),
    R(iritasi["rendah"] & jerawat["rendah"] & keminyakan["rendah"] & kekeringan["rendah"], tingkat_masalah["ringan"]),
    R(iritasi["rendah"] & jerawat["rendah"] & keminyakan["sedang"], tingkat_masalah["ringan"]),
    R(iritasi["rendah"] & jerawat["rendah"] & kekeringan["sedang"], tingkat_masalah["ringan"]),
    R(iritasi["rendah"] & jerawat["rendah"] & keminyakan["rendah"], tingkat_masalah["ringan"]),
]
