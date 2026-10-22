from datetime import date

from elpris.hamta_elpris import build_url


def test_build_url_uses_two_digit_month_and_day():
    url = build_url(date(2025, 3, 5))
    assert url == "https://www.elprisetjustnu.se/api/v1/prices/2025/03-05_SE3.json"


def test_build_url_other_area():
    assert build_url(date(2025, 12, 24), area="SE4").endswith("2025/12-24_SE4.json")