from typing import List


def extract_keyboard_entries(keyboard) -> List[str]:
    result = []
    [result.extend(r) for r in keyboard]
    return [button.text.replace("_button", "") for button in result]


def get_random_locale() -> str:
    # return Random().choice(config_reader.config.locales)
    return "ru"  # todo fix en this working as ru
