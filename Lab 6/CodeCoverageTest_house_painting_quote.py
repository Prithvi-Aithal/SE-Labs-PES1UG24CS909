import pytest
from house_painting_quote import painting_quote, paint_litres, crew_days

# Code (line) coverage tests: every statement in house_painting_quote.py
# is executed at least once.


# ---------- painting_quote ----------

def test_exterior_enamel():
    # 500 * 30 * 2 = 30000, + exterior surcharge 500 * 5 = 32500
    assert painting_quote("enamel", 500, 2, True) == 32500


def test_unknown_paint_raises():
    with pytest.raises(ValueError, match="unknown paint"):
        painting_quote("oil", 500, 1, False)


def test_zero_area_raises():
    with pytest.raises(ValueError, match="invalid job"):
        painting_quote("emulsion", 0, 1, False)


def test_distemper_exterior_raises():
    with pytest.raises(ValueError, match="interiors only"):
        painting_quote("distemper", 500, 1, True)


def test_large_area_gets_ten_percent_discount():
    # 2500 * 20 = 50000, + 2500 * 5 = 62500, - 62500 // 10 = 56250
    assert painting_quote("emulsion", 2500, 1, True) == 56250


def test_small_job_charged_minimum():
    # 100 * 20 + 100 * 5 = 2500, below the 5000 minimum
    assert painting_quote("emulsion", 100, 1, True) == 5000


# ---------- paint_litres ----------

def test_smooth_litres():
    assert paint_litres(200, 1, "smooth") == 2


def test_rough_litres_rounds_up():
    # 130 sqft / 60 sqft per litre = 2.17 -> 3 litres
    assert paint_litres(130, 1, "rough") == 3


def test_unknown_surface_raises():
    with pytest.raises(ValueError, match="unknown surface"):
        paint_litres(100, 1, "glass")


# ---------- crew_days ----------

def test_crew_days_with_wallpaper_removal():
    # 2 painters = 800 sqft/day; 1000 sqft -> 2 days, + 2 for wallpaper
    assert crew_days(1000, 2, True) == 4


def test_no_painters_raises():
    with pytest.raises(ValueError, match="at least one painter"):
        crew_days(1000, 0, False)
