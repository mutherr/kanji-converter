from sudachipy import Dictionary, SplitMode
import kenlm
import heapq

from util.kanji import find_kanji_for_kana

# todo: clean up this code, it is a mess

tokenizer = Dictionary().create()

posToCheck = [
    "普通名詞",
    "名詞",
    "形容詞",
    "形容動詞",
    "名詞的",
    "動詞",
    "形状詞",
    "代名詞",
    "接尾辞",
    "副詞",
    "助動詞",
    "連体詞",
]


def reinflect_verb(surface_form, dictionary_form):
    """
    Comprehensive verb reinflection to handle various conjugated forms.
    Returns the reinflected form or None if no pattern matches.
    """
    # Handle compound する verbs first
    if dictionary_form.endswith("する"):
        stem = dictionary_form[:-2]  # Remove する
        if surface_form.endswith("し"):
            return stem + "し"
        elif surface_form.endswith("して"):
            return stem + "して"
        elif surface_form.endswith("した"):
            return stem + "した"
        elif surface_form.endswith("すれ"):
            return stem + "すれ"
        elif surface_form.endswith("しよう"):
            return stem + "しよう"
        elif surface_form.endswith("さ"):
            return stem + "さ"

    # Handle irregular verbs
    if dictionary_form in ["する", "為る"]:
        if surface_form.endswith("し"):
            return dictionary_form[:-2] + "し"
        elif surface_form.endswith("して"):
            return dictionary_form[:-2] + "して"
        elif surface_form.endswith("した"):
            return dictionary_form[:-2] + "した"
        elif surface_form.endswith("すれ"):
            return dictionary_form[:-2] + "すれ"
        elif surface_form.endswith("しよう"):
            return dictionary_form[:-2] + "しよう"
        elif surface_form == "さ":
            return dictionary_form[:-2] + "さ"

    if dictionary_form in ["くる", "来る"]:
        if surface_form in ["き", "来"]:
            return dictionary_form[:-2] + "き"
        elif surface_form.endswith("きて"):
            return dictionary_form[:-2] + "きて"
        elif surface_form.endswith("きた"):
            return dictionary_form[:-2] + "きた"
        elif surface_form.endswith("くれ"):
            return dictionary_form[:-2] + "くれ"
        elif surface_form.endswith("こよう"):
            return dictionary_form[:-2] + "こよう"

    # Handle special case of いく -> いって (not いいて)
    if dictionary_form.endswith("いく") and surface_form.endswith("いって"):
        return dictionary_form[:-2] + "いって"
    elif dictionary_form.endswith("いく") and surface_form.endswith("いった"):
        return dictionary_form[:-2] + "いった"

    # Ichidan verbs (る-verbs) - only match if they follow ichidan patterns exactly
    if dictionary_form.endswith("る"):
        stem = dictionary_form[:-1]

        # Check if this looks like an ichidan verb by checking if surface form matches ichidan patterns
        # Ichidan verbs have simple stem + ending patterns, not complex sound changes like godan
        if surface_form == stem:  # stem form (masu-stem)
            return stem
        elif surface_form == stem + "て":  # exact match for te-form
            return stem + "て"
        elif surface_form == stem + "た":  # exact match for past (not sound-changed forms like った)
            return stem + "た"
        elif surface_form == stem + "れ":  # exact match for imperative
            return stem + "れ"
        elif surface_form == stem + "よう":  # exact match for volitional
            return stem + "よう"
        elif surface_form == stem + "ば":  # exact match for conditional
            return stem + "ば"
        elif surface_form == stem + "ない":  # exact match for negative
            return stem + "ない"
        elif surface_form == stem + "られる":  # passive/potential
            return stem + "られる"
        elif surface_form == stem + "させる":  # causative
            return stem + "させる"
        elif surface_form == stem + "ている":  # progressive
            return stem + "ている"
        elif surface_form == stem + "てある":  # state
            return stem + "てある"
        elif surface_form == stem + "ておく":  # preparation
            return stem + "ておく"

    # Godan verbs (う-verbs) - comprehensive patterns with correct sound changes
    godan_endings = {
        "う": {"i": "い", "a": "わ", "e": "え", "o": "お", "past": "った", "te": "って"},
        "く": {"i": "き", "a": "か", "e": "け", "o": "こ", "past": "いた", "te": "いて"},
        "ぐ": {"i": "ぎ", "a": "が", "e": "げ", "o": "ご", "past": "いだ", "te": "いで"},
        "す": {"i": "し", "a": "さ", "e": "せ", "o": "そ", "past": "した", "te": "して"},
        "つ": {"i": "ち", "a": "た", "e": "て", "o": "と", "past": "った", "te": "って"},
        "ぬ": {"i": "に", "a": "な", "e": "ね", "o": "の", "past": "んだ", "te": "んで"},
        "ぶ": {"i": "び", "a": "ば", "e": "べ", "o": "ぼ", "past": "んだ", "te": "んで"},
        "む": {"i": "み", "a": "ま", "e": "め", "o": "も", "past": "んだ", "te": "んで"},
        "る": {"i": "り", "a": "ら", "e": "れ", "o": "ろ", "past": "った", "te": "って"}
    }

    for ending, forms in godan_endings.items():
        if dictionary_form.endswith(ending):
            stem = dictionary_form[:-1]

            # Masu-stem (i-form)
            if surface_form == stem + forms["i"]:
                return stem + forms["i"]
            # Past tense patterns with correct sound changes
            elif surface_form.endswith(forms["past"]):
                return stem + forms["past"]
            elif surface_form.endswith(forms["te"]):
                return stem + forms["te"]
            # Conditional
            elif surface_form.endswith(forms["e"] + "ば"):
                return stem + forms["e"] + "ば"
            # Volitional
            elif surface_form.endswith(forms["o"] + "う"):
                return stem + forms["o"] + "う"
            # Negative
            elif surface_form.endswith(forms["a"] + "ない"):
                return stem + forms["a"] + "ない"
            # Passive
            elif surface_form.endswith(forms["a"] + "れる"):
                return stem + forms["a"] + "れる"
            # Causative
            elif surface_form.endswith(forms["a"] + "せる"):
                return stem + forms["a"] + "せる"
            # Imperative
            elif surface_form.endswith(forms["e"]):
                return stem + forms["e"]
            # Various te-form combinations
            elif surface_form.endswith(forms["te"] + "いる"):
                return stem + forms["te"] + "いる"
            elif surface_form.endswith(forms["te"] + "ある"):
                return stem + forms["te"] + "ある"
            elif surface_form.endswith(forms["te"] + "おく"):
                return stem + forms["te"] + "おく"

    # Handle ください pattern (should come after other patterns to avoid conflicts)
    if surface_form.endswith("ください"):
        # Return the full surface form for ください patterns
        return surface_form

    # Handle っ ending (sokuon)
    if surface_form.endswith("っ"):
        return dictionary_form[:-1] + "っ"

    return None


def reinflect_i_adjective(surface_form, dictionary_form):
    """
    Comprehensive i-adjective reinflection.
    """
    if not dictionary_form.endswith("い"):
        return None

    stem = dictionary_form[:-1]

    # Handle irregular いい/よい
    if dictionary_form in ["いい", "よい", "良い"]:
        if surface_form.endswith("くなかった"):  # Check longer patterns first
            return "よくなかった"
        elif surface_form.endswith("かったら"):
            return "よかったら"
        elif surface_form.endswith("かった"):
            return "よかった"
        elif surface_form.endswith("ければ"):
            return "よければ"
        elif surface_form.endswith("く"):
            return "よく"

    # Regular i-adjective patterns - check specific patterns first, then general ones
    if surface_form == "ない":
        return dictionary_form
    elif surface_form.endswith("くなかった"):  # Most specific first
        return stem + "くなかった"
    elif surface_form.endswith("くない"):
        return stem + "くない"
    elif surface_form.endswith("かったら"):
        return stem + "かったら"
    elif surface_form.endswith("かった"):
        return stem + "かった"
    elif surface_form.endswith("ければ"):
        return stem + "ければ"
    elif surface_form.endswith("かっ") and dictionary_form.endswith("い"):
        return stem + "かっ"
    elif surface_form.endswith("く"):
        return stem + "く"
    elif surface_form.endswith("し") and dictionary_form.endswith("い"):
        # Handle し-form properly for words ending in しい
        if dictionary_form.endswith("しい") and len(stem) >= 2:
            return stem[:-1] + "し"  # Remove the し from stem and add し
        else:
            return stem + "し"
    elif surface_form.endswith("い") and dictionary_form.endswith("い"):
        # Basic form - check last since it's most general
        return dictionary_form

    return None


def reinflect_na_adjective(surface_form, dictionary_form):
    """
    Comprehensive na-adjective reinflection.
    """
    # Basic form
    if surface_form == dictionary_form:
        return dictionary_form

    # Past tense
    if surface_form.endswith("だった"):
        return dictionary_form + "だった"
    elif surface_form.endswith("でした"):
        return dictionary_form + "でした"

    # Te-form
    if surface_form.endswith("で"):
        return dictionary_form + "で"

    # Conditional
    if surface_form.endswith("なら"):
        return dictionary_form + "なら"
    elif surface_form.endswith("だったら"):
        return dictionary_form + "だったら"

    # Negative
    if surface_form.endswith("じゃない"):
        return dictionary_form + "じゃない"
    elif surface_form.endswith("ではない"):
        return dictionary_form + "ではない"
    elif surface_form.endswith("じゃなかった"):
        return dictionary_form + "じゃなかった"
    elif surface_form.endswith("ではなかった"):
        return dictionary_form + "ではなかった"

    # Adverbial form
    if surface_form.endswith("に"):
        return dictionary_form + "に"

    return dictionary_form


def getPossibleKanji(morphemes):
    possibilities = []
    for c in morphemes:
        if c.part_of_speech()[0] in posToCheck:
            surface_form = c.surface()
            print(c.surface(), c.dictionary_form())
            kanji_forms = find_kanji_for_kana(c.dictionary_form())

            if surface_form != c.dictionary_form():
                kanji_forms = kanji_forms.union(find_kanji_for_kana(c.surface()))

            possible_forms = [surface_form]
            for form in kanji_forms:
                # Comprehensive verb reinflection
                if "動詞" in c.part_of_speech():
                    inflected_form = reinflect_verb(surface_form, form)
                    if inflected_form:
                        possible_forms.append(inflected_form)
                    else:
                        if len(form) < len(surface_form) and len(form) > 1:
                            print(
                                "Unsure how to reinflect surface form",
                                surface_form,
                                "given",
                                form,
                            )
                        # Fallback to simple truncation
                        possible_forms.append(form[: len(surface_form)])
                # い-Adjectives
                elif "形容詞" in c.part_of_speech():
                    inflected_form = reinflect_i_adjective(surface_form, form)
                    if inflected_form:
                        possible_forms.append(inflected_form)
                    else:
                        print(
                            "Unsure how to reinflect surface form ",
                            surface_form,
                            " given ",
                            form,
                        )
                        # Fallback
                        possible_forms.append(form)
                # な-Adjectives
                elif "形状詞" in c.part_of_speech():
                    inflected_form = reinflect_na_adjective(surface_form, form)
                    if inflected_form:
                        possible_forms.append(inflected_form)
                    else:
                        possible_forms.append(form)
                else:
                    possible_forms.append(form)

            possible_forms = sorted(list(set(possible_forms)))
            print("Inflected forms:", possible_forms)
            print(len(possible_forms), "possible forms for", c.surface())
            

            print("Surface form:", surface_form, c.dictionary_form())
            print("Possible forms:", possible_forms)
            print("Part of speech:", c.part_of_speech())
            possibilities.append(possible_forms)
        else:
            print(c.surface(), "not in posToCheck")
            print("Part of speech:", c.part_of_speech())
            possibilities.append([c.surface()])

    return possibilities


def addExtraOptions(morphemes, possibilities):
    """
    Add extra options to the possibilities list.
    This can be used to smooth over issues with the parser.
    """
    for i, p in enumerate(possibilities):
        # if we find two adjacent "お" options, we can add an extra "大" option to the second and
        # let the first be skipped
        # this is a hack to deal with the fact that the parser does not handle "おお" correctly
        # in some cases, like "おおそうじ"
        if "お" in p and "お" in possibilities[i - 1] and i > 0:
            possibilities[i] += ["大"]
            possibilities[i - 1] += [""]
        # similarly, the parser sometimes struggles with words like 伝統 (でんとう), splitting it into
        # でん, と, and う.
        # The hack here is to add the readings for "とう" to "と" and let the う be skipped
        if "と" in p and "う" in possibilities[i + 1] and i + 1 < len(possibilities):
            possibilities[i] += ["とう"] + list(find_kanji_for_kana("とう"))
            possibilities[i] = list(set(possibilities[i]))
            possibilities[i + 1] += [""]
        if "ど" in p and "う" in possibilities[i + 1] and i + 1 < len(possibilities):
            possibilities[i] += ["どう"] + list(find_kanji_for_kana("どう"))
            possibilities[i] = list(set(possibilities[i]))
            possibilities[i + 1] += [""]
        # multi-character syllables like "にゅう" are sometimes split into "に", "ゅ", and "う"
        # we can fix this by adding "にゅう" to the first syllable and letting the next two be skipped
        # this is a hack to deal with the fact that the parser does not handle "にゅう" correctly
        # in some cases, like "入力" (にゅうりょく) or "入院" (にゅういん)
        if "に" in p and "ゅ" in possibilities[i + 1] and "う" in possibilities[i + 2] and i + 2 < len(possibilities):
            print("Found にゅう hack")
            possibilities[i] += ["にゅう"] + list(find_kanji_for_kana("にゅう")+["入"])
            possibilities[i] = list(set(possibilities[i]))
            possibilities[i + 1] += [""]
            possibilities[i + 2] += [""]
        if "り" in p and "ょ" in possibilities[i + 1] and "く" in possibilities[i + 2] and i + 2 < len(possibilities):
            possibilities[i] += ["りょく"] + list(find_kanji_for_kana("りょく"))
            possibilities[i] = list(set(possibilities[i]))
            possibilities[i + 1] += [""]
            possibilities[i + 2] += [""]
        #the real fix for this is to find a better kanji dictionary. JMdict is missing a lot of onyomi,
        # and kanjidic seems to overwhlem the lm and make it produce unexpected results
        # this is a hack to deal with the fact that the parser does not handle "にゅう" correctly
        # in some cases, like "入力" (にゅうりょく) or "入院" (にゅういん)
        if "にゅう" in p:
            possibilities[i] += list(find_kanji_for_kana("にゅう"))+["入"]
            possibilities[i] = list(set(possibilities[i]))
    return possibilities


def top_n_sentences(token_options, model, N=5, beam_width=10):
    """
    token_options: list of list of str, e.g. [["亡い", "ない"], ["か"], ...]
    model: kenlm.Model
    N: number of top completions to return
    beam_width: max partials to keep per step
    Returns: list of (score, sentence) tuples, sorted best-first
    """
    # Each partial: (neg_score_so_far, tokens_list)
    beam = [(0.0, [])]
    for idx, options in enumerate(token_options):
        new_beam = []
        for neg_score, seq in beam:
            for opt in options:
                new_seq = seq + [opt]
                # KenLM: score one sentence so far
                sentence = " ".join(new_seq)
                score = model.score(sentence, bos=True, eos=True)
                new_beam.append((-score, new_seq))
        # Keep top beam_width
        beam = heapq.nsmallest(beam_width, new_beam)
    return [(-neg_score, seq) for neg_score, seq in heapq.nsmallest(N, beam)]


def main():
    # test_sentence = "これはテストぶんです"
    # test_sentence = "このにくをたべたくておいしいです"
    # test_sentence = "こーひーがさめないうちにのんでください"
    # test_sentence = "ここでまってください"
    # test_sentence = "きれいなはなです"
    # test_sentence = "かんがえさせてもらえませんか"
    # test_sentence = "かんがえないようにしなさい"
    # test_sentence = "みてくれてありがとう"
    # test_sentence = "もういちどいってください"
    # test_sentence = "おいしゃさんにきいてください"
    # test_sentence = "あたしにはなしかけないでください"
    test_sentence = "あしたはさむくなるから、あたたかいふくをきてください"
    # test_sentence = "わたしのしゅみはおんがくをきくことです"
    # test_sentence = "あるきながらはなしまんせんか"
    # test_sentence = "あめがふっているので、かさをもっていきます"
    # test_sentence = "きゅうにあめがふりだしたので、かさをもっていなかったわたしはずぶぬれになってしまった。"
    # test_sentence = "どうぞよろしくおねがいいたします。"
    # test_sentence = "おおそうじがにほんてきなでんとうです。"
    # test_sentence = "ことしのなつはとてもあつい"
    # test_sentence = "えきのまえにあるおみせで、あたらしいふくをかいました。"
    # test_sentence = "だいがくせいのときに、れきしにせんこうしました。"
    # test_sentence = "すいせいをみた！"
    # test_sentence = "そこにいくなら、はやくいったほうがいいよ"
    # test_sentence = "いいにくいことをいうのはむずかしい"
    # test_sentence = "きびしすぎると、かんがえがうまくいかないこともある"
    # test_sentence = "おまつりはたのしかったです"
    # test_sentence = "はいってもいいんじゃないの？"
    # test_sentence = "いちばんすきなかしゅはだれですか"
    # test_sentence = "いもうとはうたうのがじょうずです"

    morphemes = tokenizer.tokenize(test_sentence, mode=SplitMode.C)
    print(f"Morphemes for the sentence {test_sentence}: {morphemes}")
    possibilities = getPossibleKanji(morphemes)
    print(f"Possible Kanji for the sentence before augmentation: {possibilities}")
    possibilities = addExtraOptions(morphemes, possibilities)
    print(f"Possible Kanji for the sentence {test_sentence}: {possibilities}")

    total_possibilities = 1
    for p in possibilities:
        total_possibilities *= len(p)
    print("Total possible combinations:", total_possibilities)

    model = kenlm.Model("sentences/jp3.arpa")

    print(f"Calculating top kanji choices for {test_sentence}...")
    top_sentences = top_n_sentences(possibilities, model, N=10, beam_width=10)
    for score, sentence in top_sentences:
        sentence = "".join(sentence)
        print(f"Score: {score:.2f}, Sentence: {sentence}")


if __name__ == "__main__":
    main()
