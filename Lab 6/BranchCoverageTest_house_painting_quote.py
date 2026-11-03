import pytest
from house_painting_quote import painting_quote, paint_litres, crew_days

# Branch coverage tests: every decision in house_painting_quote.py is
# evaluated both True and False, including boundary values.


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


def test_negative_area_raises():
    with pytest.raises(ValueError, match="invalid job"):
        painting_quote("emulsion", -100, 1, False)


def test_zero_coats_raises():
    # area is valid, so only the coats < 1 half of the condition is true
    with pytest.raises(ValueError, match="invalid job"):
        painting_quote("emulsion", 500, 0, False)


def test_distemper_exterior_raises():
    with pytest.raises(ValueError, match="interiors only"):
        painting_quote("distemper", 500, 1, True)


def test_distemper_interior_allowed():
    # is_exterior False: distemper check and surcharge both skipped
    assert painting_quote("distemper", 500, 1, False) == 6000


def test_emulsion_exterior_allowed():
    # is_exterior True but paint is not distemper: no error
    assert painting_quote("emulsion", 300, 1, True) == 7500


def test_interior_has_no_surcharge():
    # 300 * 20 * 2 = 12000, no exterior surcharge
    assert painting_quote("emulsion", 300, 2, False) == 12000


def test_large_area_gets_ten_percent_discount():
    # 2500 * 20 = 50000, + 2500 * 5 = 62500, - 62500 // 10 = 56250
    assert painting_quote("emulsion", 2500, 1, True) == 56250


def test_area_exactly_2000_gets_no_discount():
    # boundary: discount only applies above 2000 sqft
    assert painting_quote("enamel", 2000, 1, False) == 60000


def test_area_2001_gets_discount():
    # 2001 * 20 = 40020, - 40020 // 10 = 36018
    assert painting_quote("emulsion", 2001, 1, False) == 36018


def test_small_job_charged_minimum():
    # 100 * 20 + 100 * 5 = 2500, below the 5000 minimum
    assert painting_quote("emulsion", 100, 1, True) == 5000


def test_cost_exactly_5000_is_not_raised():
    # boundary: 250 * 20 = 5000 is not below the minimum
    assert painting_quote("emulsion", 250, 1, False) == 5000


def test_cost_just_below_minimum():
    # 249 * 20 = 4980 -> raised to 5000
    assert painting_quote("emulsion", 249, 1, False) == 5000


# ---------- paint_litres ----------

def test_smooth_litres():
    assert paint_litres(200, 1, "smooth") == 2


def test_smooth_litres_rounds_up():
    # 250 sqft / 100 sqft per litre = 2.5 -> 3 litres
    assert paint_litres(250, 1, "smooth") == 3


def test_rough_litres_rounds_up():
    # 130 sqft / 60 sqft per litre = 2.17 -> 3 litres
    assert paint_litres(130, 1, "rough") == 3


def test_rough_litres_exact():
    # 120 / 60 = 2 exactly, no rounding
    assert paint_litres(120, 1, "rough") == 2


def test_litres_multiply_by_coats():
    # 200 * 2 = 400 sqft of painting -> 4 litres
    assert paint_litres(200, 2, "smooth") == 4


def test_unknown_surface_raises():
    with pytest.raises(ValueError, match="unknown surface"):
        paint_litres(100, 1, "glass")


# ---------- crew_days ----------

def test_crew_days_with_wallpaper_removal():
    # 2 painters = 800 sqft/day; 1000 sqft -> 2 days, + 2 for wallpaper
    assert crew_days(1000, 2, True) == 4


def test_crew_days_partial_day_without_wallpaper():
    # 1000 sqft / 800 per day -> 2 days, no wallpaper
    assert crew_days(1000, 2, False) == 2


def test_crew_days_exact_multiple():
    # 800 sqft / 800 per day = exactly 1 day, no extra partial day
    assert crew_days(800, 2, False) == 1


def test_crew_days_exact_multiple_with_wallpaper():
    # 400 sqft / 400 per day = 1 day, + 2 for wallpaper
    assert crew_days(400, 1, True) == 3


def test_no_painters_raises():
    with pytest.raises(ValueError, match="at least one painter"):
        crew_days(1000, 0, False)


def test_one_painter_is_allowed():
    # boundary: painters == 1 is valid; 1000 / 400 -> 3 days
    assert crew_days(1000, 1, False) == 3
