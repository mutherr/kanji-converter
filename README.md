# How it works

Candidate kanji-containing sentences are generated as follows:

The sentence is first run through the `sudachipy` parser to split the sequence up into morphemes. As an example, `もういちどいってください` would be split into the sequence `['もう', 'いち', 'ど', 'いっ', 'て', 'ください']`.

Candidate kanji for each morpheme are taken from the JMDict dictionary by colelcting all entries with the given morpheme as a possible reading.

Importantly, this gives us back the kanji forms in their dictionary for (ex: 言う rather than 言っ as we need to reconstuct the example sentence), so basic rule-based reinflection is performed for verbs and い adjectives.

These possibilities are then formed into a reporesentation of all possible kanji or hiragana forms called a lattice, where the i-th entry stores all the ways the i-th morpheme could be represented. For the example sentence, this is:

```
[['もう'],
 ['一', '位地', '位置', '壱', '壹', '市', '弌', '逸', '１', 'いち'],
 ['努', '土', '度', '弩', '笯', '途', 'ど'],
 ['云っ', '結っ', '言っ', '謂っ', 'いっ'],
 ['て'],
 ['下さい', 'ください']]
```

We then determine the top-k (by default 10) most likely assignments using standard beam-search decoding with a beam size of 10. The sentences are scored by a trigram language model estimated using KenLM and a corpus of 246,339 sentences extracted from Tatoeba.

For the example sentence, this gives us (in descending likelihood):

```
Score: -14.50, Sentence: もう一度言ってください
Score: -15.09, Sentence: もう一度いってください
Score: -15.55, Sentence: もういちど言ってください
Score: -16.14, Sentence: もういちどいってください
Score: -16.28, Sentence: もう１度言ってください
Score: -16.86, Sentence: もう一度結ってください
Score: -16.87, Sentence: もう１度いってください
Score: -17.28, Sentence: もう一度言って下さい
Score: -17.43, Sentence: もう一度云ってください
Score: -18.06, Sentence: もう一度いって下さい
```

# Installation

Install the `uv` package manager, then run `uv sync`.

## A note on installation with Homebrew python

When installing via `uv`, you may need to set the paths manually if using Homebrew python.
This will often manifest as the program reporting a missing `Python.h`file while building.

```
export CPPFLAGS="-I/home/linuxbrew/.linuxbrew/include/python3.12" (adjust for your version of python, 3.12 is the latest stable at time of writing.)
export LDFLAGS="-L/home/linuxbrew/.linuxbrew/lib"
uv sync
```

Installing based on system python should be fine, as the headers should already be in your path.
