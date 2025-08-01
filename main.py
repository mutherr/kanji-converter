from sudachipy import Dictionary, SplitMode
import xml.etree.ElementTree as ET
import kenlm
import heapq

# todo: clean up this code, it is a mess

tokenizer = Dictionary().create()

JMDICT_PATH = "dict/JMdict_e.xml"
tree = ET.parse(JMDICT_PATH)
root = tree.getroot()

posToCheck = [
    "普通名詞",
    "名詞",
    "形容詞",
    "形容動詞",
    "名詞的",
    "動詞",
    "形状詞",
    "代名詞",
]


def find_kanji_for_kana(reading):
    results = set()
    for entry in root.findall("entry"):
        # Readings (r_ele) can be multiple
        readings = [
            r.text for r_ele in entry.findall("r_ele") for r in r_ele.findall("reb")
        ]
        if reading in readings:
            # Kanji elements (k_ele) - may be multiple, or absent (kana-only)
            kanjis = [
                k.text for k_ele in entry.findall("k_ele") for k in k_ele.findall("keb")
            ]
            if kanjis:
                results.update(kanjis)

    return results


def isVerbDictForm(verb):
    return verb.endswith(("う", "く", "す", "つ", "ぬ", "む", "ゆ", "る", "ぐ"))


def getPossibleKanji(sentence):
    morphemes = tokenizer.tokenize(sentence, mode=SplitMode.C)

    possibilities = []
    for c in morphemes:
        if c.part_of_speech()[0] in posToCheck:
            surface_form = c.surface()
            kanji_forms = find_kanji_for_kana(c.dictionary_form())

            possible_forms = []
            for form in kanji_forms:
                # perform basic reinflection for verbs. I am so glad the verbs
                # in this language are regular
                if "動詞" in c.part_of_speech():
                    # if we know we need a verb, we can ignore non-verb options
                    if not isVerbDictForm(form):
                        continue

                    if len(form) < len(surface_form):
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
    test_sentence = "あるきながらはなしまんせんか"

    possibilities = getPossibleKanji(test_sentence)
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
