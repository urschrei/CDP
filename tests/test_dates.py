import pytest

from cdpp.dates import year_number, year_text


@pytest.mark.parametrize(
    ("text", "number"),
    [("1244 BC", -1243), ("2 BC", -1), ("1 BC", 0), ("1 AD", 1), ("75 AD", 75)],
)
def test_years_convert_to_astronomical_numbers_and_back(text: str, number: int) -> None:
    assert year_number(text) == number
    assert year_text(number) == text


def test_year_number_reads_other_spacing_and_case() -> None:
    assert year_number(" 2  bc ") == -1


@pytest.mark.parametrize("text", ["1244", "BC", "0 BC", "1244 BCE", ""])
def test_other_texts_are_not_years(text: str) -> None:
    with pytest.raises(ValueError, match="Not a year"):
        year_number(text)
