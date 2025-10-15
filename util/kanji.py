import xml.etree.ElementTree as ET
from util.jpUtil import hiragana_to_katakana


JMDICT_PATH = "dict/JMdict_e.xml"
tree = ET.parse(JMDICT_PATH)
root = tree.getroot()

KANJIDIC_PATH = "dict/kanjidic2.xml"
kanjidic_tree = ET.parse(KANJIDIC_PATH)
kanjidic_root = kanjidic_tree.getroot()

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