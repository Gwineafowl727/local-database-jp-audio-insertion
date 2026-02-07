def hira_to_kata(hiragana: str) -> str:
    """
    Converts Hiragana to Katakana, representing long vowels with 'ー'.
    Handles regular and irregular long vowel sequences like:
    ああ -> アー, ええ -> エー, えい -> エー, おお -> オー, おう -> オー
    """
    hira_to_kata_map = { 
        'あ': 'ア', 'い': 'イ', 'う': 'ウ', 'え': 'エ', 'お': 'オ',
        'か': 'カ', 'き': 'キ', 'く': 'ク', 'け': 'ケ', 'こ': 'コ',
        'さ': 'サ', 'し': 'シ', 'す': 'ス', 'せ': 'セ', 'そ': 'ソ',
        'た': 'タ', 'ち': 'チ', 'つ': 'ツ', 'て': 'テ', 'と': 'ト',
        'な': 'ナ', 'に': 'ニ', 'ぬ': 'ヌ', 'ね': 'ネ', 'の': 'ノ',
        'は': 'ハ', 'ひ': 'ヒ', 'ふ': 'フ', 'へ': 'ヘ', 'ほ': 'ホ',
        'ま': 'マ', 'み': 'ミ', 'む': 'ム', 'め': 'メ', 'も': 'モ',
        'や': 'ヤ', 'ゆ': 'ユ', 'よ': 'ヨ',
        'ら': 'ラ', 'り': 'リ', 'る': 'ル', 'れ': 'レ', 'ろ': 'ロ',
        'わ': 'ワ', 'を': 'ヲ', 'ん': 'ン',
        'が': 'ガ', 'ぎ': 'ギ', 'ぐ': 'グ', 'げ': 'ゲ', 'ご': 'ゴ',
        'ざ': 'ザ', 'じ': 'ジ', 'ず': 'ズ', 'ぜ': 'ゼ', 'ぞ': 'ゾ',
        'だ': 'ダ', 'ぢ': 'ヂ', 'づ': 'ヅ', 'で': 'デ', 'ど': 'ド',
        'ば': 'バ', 'び': 'ビ', 'ぶ': 'ブ', 'べ': 'ベ', 'ぼ': 'ボ',
        'ぱ': 'パ', 'ぴ': 'ピ', 'ぷ': 'プ', 'ぺ': 'ペ', 'ぽ': 'ポ',
        'ぁ': 'ァ', 'ぃ': 'ィ', 'ぅ': 'ゥ', 'ぇ': 'ェ', 'ぉ': 'ォ',
        'ゃ': 'ャ', 'ゅ': 'ュ', 'ょ': 'ョ', 'っ': 'ッ',
    }

    kata = ''
    i = 0
    while i < len(hiragana):
        char = hiragana[i]
        if char in hira_to_kata_map:
            kata_char = hira_to_kata_map[char]
            # Handle long vowel sequences
            if i+1 < len(hiragana):
                next_char = hiragana[i+1]
                long_vowel_pairs = [
                    ('あ','あ'), ('い','い'), ('う','う'), ('え','え'), ('え','い'), ('お','お'), ('お','う'),
                    ('か','あ'), ('き','い'), ('く','う'), ('け','え'), ('け','い'), ('こ','お'), ('こ','う'),
                    ('さ','あ'), ('し','い'), ('す','う'), ('せ','え'), ('せ','い'), ('そ','お'), ('そ','う'),
                    ('た','あ'), ('ち','い'), ('つ','う'), ('て','え'), ('て','い'), ('と','お'), ('と','う'),
                    ('な','あ'), ('に','い'), ('ぬ','う'), ('ね','え'), ('ね','い'), ('の','お'), ('の','う'),
                    ('は','あ'), ('ひ','い'), ('ふ','う'), ('へ','え'), ('へ','い'), ('ほ','お'), ('ほ','う'),
                    ('ま','あ'), ('み','い'), ('む','う'), ('め','え'), ('め','い'), ('も','お'), ('も','う'),
                    ('や','あ'), ('ゆ','う'), ('よ','お'), ('よ','う'),
                    ('ゃ','あ'), ('ゅ','う'), ('ょ','お'), ('ょ','う'),
                    
                    
                ]
                if (char, next_char) in long_vowel_pairs:
                    kata += kata_char + 'ー'
                    i += 2
                    continue
            kata += kata_char
        else:
            kata += char  # preserve symbols/punctuation
        i += 1
    return kata

def kata_to_hira(katakana: str) -> str:
    """Convert a Katakana string to Hiragana (ignores long vowels)."""
    result = []
    for ch in katakana:
        code = ord(ch)
        # Katakana range: U+30A1 (ァ) to U+30F6 (ヶ)
        if 0x30A1 <= code <= 0x30F6:
            result.append(chr(code - 0x60))  # Shift into Hiragana range
        else:
            result.append(ch)  # Leave non-Katakana as-is
    return "".join(result)


# Examples
print(kata_to_hira("カタカナ"))  # かたかな
print(kata_to_hira("オンオフ"))  # おんおふ
print(kata_to_hira("ゲーム"))    # げーむ


