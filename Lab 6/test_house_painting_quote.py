import pytest
from house_painting_quote import painting_quote, paint_litres, crew_days

#Example test cases:
def test_exterior_enamel():
    assert painting_quote("enamel", 500, 2, True) == 32500

def test_smooth_litres():
    assert paint_litres(200, 1, "smooth") == 2

#Write the rest of the test cases so that the code is 90- 100% covered.
