def hiragana_to_katakana(hiragana):
    """Convert hiragana to katakana."""
    return "".join(
        chr(ord(char) + 96) if "ぁ" <= char <= "ゖ" else char for char in hiragana
    )


def katakana_to_hiragana(katakana):
    """Convert katakana to hiragana."""
    return "".join(
        chr(ord(char) - 96) if "ァ" <= char <= "ヶ" else char for char in katakana
    )


def isVerbDictForm(verb):
    return verb.endswith(("う", "く", "す", "つ", "ぬ", "む", "ゆ", "る", "ぐ"))