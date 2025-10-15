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
                    elif surface_form.endswith("か") and form.endswith("く"):
                        possible_forms.append(form[:-1] + "か")
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
                    elif surface_form.endswith("し") and form.endswith("い"):
                        possible_forms.append(form[:-1])
                    elif surface_form.endswith("かっ") and form.endswith("い"):
                        possible_forms.append(form[:-1] + "かっ")
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
    # test_sentence = "あしたはさむくなるから、あたたかいふくをきてください"
    test_sentence = "わたしのしゅみはおんがくをきくことです"
    # test_sentence = "あるきながらはなしまんせんか"
    # test_sentence = "あめがふっているので、かさをもっていきます"
    # test_sentence = "きゅうにあめがふりだしたので、かさをもっていなかったわたしはずぶぬれになってしまった。"
    # test_sentence = "どうぞよろしくおねがいいたします。"
    test_sentence = "おおそうじがにほんてきなでんとうです。"
    # test_sentence = "ことしのなつはとてもあつい"
    # test_sentence = "えきのまえにあるおみせで、あたらしいふくをかいました。"
    test_sentence = "だいがくせいのときに、れきしにせんこうしました。"
    # test_sentence = "すいせいをみた！"
    # test_sentence = "そこにいくなら、はやくいったほうがいいよ"
    # test_sentence = "いいにくいことをいうのはむずかしい"
    # test_sentence = "きびしすぎると、かんがえがうまくいかないこともある"
    # test_sentence = "おまつりはたのしかったです"
    # test_sentence = "はいってもいいんじゃないの？"
    # test_sentence = "ここににゅうりょくして"
    test_sentence = "いちばんすきなかしゅはだれですか"
    test_sentence = "いもうとはうたうのがじょうずです"

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
