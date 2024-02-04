from pytest_cases import parametrize
from python_tidal_experimental.models import from_camel


@parametrize(
    "camel, snake",
    [
        ("lower", "lower"),
        ("twoWords", "two_words"),
        ("threeWordWords", "three_word_words"),
    ],
)
def test_from_camel_converts_to_snake_case(camel, snake):
    assert from_camel(camel) == snake


@parametrize(
    "lower",
    [
        "jsuttext",
        "snake_case",
        "funny-stuff",
    ],
)
def test_from_camel_passes_lowercase_input_untouched(lower):
    assert from_camel(lower) == lower
