from sudachipy import Dictionary, SplitMode
import xml.etree.ElementTree as ET
import kenlm
import heapq

from util.jpUtil import hiragana_to_katakana

# todo: clean up this code, it is a mess

tokenizer = Dictionary().create()

JMDICT_PATH = "dict/JMdict_e.xml"
tree = ET.parse(JMDICT_PATH)
root = tree.getroot()

KANJIDIC_PATH = "dict/kanjidic2.xml"
kanjidic_tree = ET.parse(KANJIDIC_PATH)
kanjidic_root = kanjidic_tree.getroot()

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
]


def find_kanji_for_kana(reading):
    results = set()
    # results = find_kanji_for_kana_in_kanjidic(hiragana_to_katakana(reading))
    for entry in root.findall("entry"):
        readings = [
            r.text for r_ele in entry.findall("r_ele") for r in r_ele.findall("reb")
        ]
        if reading in readings:
            kanjis = [
                k.text for k_ele in entry.findall("k_ele") for k in k_ele.findall("keb")
            ]
            if kanjis:
                results.update(kanjis)
    return results


def find_kanji_for_kana_in_kanjidic(reading, reading_types=("ja_on", "ja_kun")):
    results = set()
    for char in kanjidic_root.findall("character"):
        kanji = char.findtext("literal")
        rm = char.find("reading_meaning")
        if rm is not None:
            for group in rm.findall("rmgroup"):
                for rd in group.findall("reading"):
                    rtype = rd.attrib.get("r_type")
                    if rtype in reading_types and rd.text == reading:
                        results.add(kanji)
    return results


def isVerbDictForm(verb):
    return verb.endswith(("う", "く", "す", "つ", "ぬ", "む", "ゆ", "る", "ぐ"))


def getPossibleKanji(morphemes):
    possibilities = []
    for c in morphemes:
        if c.part_of_speech()[0] in posToCheck:
            surface_form = c.surface()
            print(c.surface(), c.dictionary_form())
            kanji_forms = find_kanji_for_kana(c.dictionary_form())

            if surface_form != c.dictionary_form():
                kanji_forms = kanji_forms.union(find_kanji_for_kana(c.surface()))

            possible_forms = []
            for form in kanji_forms:
                # perform basic reinflection for verbs. I am so glad the verbs
                # in this language are regular
                if "動詞" in c.part_of_speech():
                    if len(form) < len(surface_form) and len(form) > 1:
                        print(
                            "Unsure how to reinflect surface form",
                            surface_form,
                            "given",
                            form,
                        )
                    if surface_form.endswith("ん") and form.endswith("む"):
                        possible_forms.append(form[:-1] + "ん")
                    elif surface_form.endswith("い") and (
                        form.endswith("ぐ") or form.endswith("く")
                    ):
                        possible_forms.append(form[:-1] + "い")
                    elif surface_form.endswith("き") and form.endswith("く"):
                        possible_forms.append(form[:-1] + "き")
                    elif surface_form.endswith("り") and form.endswith("る"):
                        possible_forms.append(form[:-1] + "り")
                    elif surface_form.endswith("し") and form.endswith("す"):
                        possible_forms.append(form[:-1] + "し")
                    elif surface_form.endswith("さい"):
                        possible_forms.append(form[:-2] + "さい")
                    elif surface_form.endswith("っ"):
                        possible_forms.append(form[:-1] + "っ")
                    elif surface_form.endswith("え"):
                        possible_forms.append(form[:-1])
                    elif surface_form.endswith("れ") and form.endswith("る"):
                        possible_forms.append(form[:-1])
                    elif surface_form == "し":
                        possible_forms.append("し")
                    elif surface_form.endswith("け") and form.endswith("る"):
                        possible_forms.append(form[:-1])
                    elif surface_form.endswith("い") and form.endswith("う"):
                        possible_forms.append(form[:-1] + "い")
                    else:
                        possible_forms.append(form[: len(surface_form)])
                # い-Adjectives
                elif "形容詞" in c.part_of_speech():
                    if surface_form == "ない":
                        possible_forms.append(form)
                    if surface_form.endswith("い") and form.endswith("い"):
                        possible_forms.append(form)
                    elif surface_form.endswith("く"):
                        possible_forms.append(form[:-1] + "く")
                    else:
                        print(
                            "Unsure how to reinflect surface form ",
                            surface_form,
                            " given ",
                            form,
                        )
                # な-Adjectives
                elif "形状詞" in c.part_of_speech():
                    print(possible_forms)
                    possible_forms.append(form)
                else:
                    possible_forms.append(form)

            possible_forms = sorted(list(set(possible_forms)))
            if c.surface() not in possible_forms:
                possible_forms.append(c.surface())
            print("Inflected forms:", possible_forms)

            print("Surface form:", c.surface(), c.dictionary_form())
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
        # if we find two adjavent "お" options, we can add an extra "大" option to the second and
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
                new_beam.append((-score, new_seq))  # negative for min-heap
        # Keep top beam_width
        beam = heapq.nsmallest(beam_width, new_beam)
    # At end, return top N results, sorted best score first
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
    # test_sentence = "あしたはさむくなるから、あたたかいふくをきてください"
    # test_sentence = "わたしのしゅみはおんがくをきくことです"
    # test_sentence = "あるきながらはなしまんせんか"
    # test_sentence = "あめがふっているので、かさをもっていきます"
    # test_sentence = "きゅうにあめがふりだしたので、かさをもっていなかったわたしはずぶぬれになってしまった。"
    # test_sentence = "どうぞよろしくおねがいいたします。"
    test_sentence = "おおそうじがにほんてきなでんとうです。"
    test_sentence = "ことしのなつはとてもあつい"
    test_sentence = "えきのまえにあるおみせで、あたらしいふくをかいました。"
    # test_sentence = "だいがくせいのときに、れきしにせんこうしました。"
    # test_sentence = "すいせいをみた！"
    # test_sentence = "そこにいくなら、はやくいったほうがいいよ"
    # test_sentence = "いいにくいことをいうのはむずかしい"

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
