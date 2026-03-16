import pytest
from main import reinflect_verb, reinflect_i_adjective, reinflect_na_adjective


class TestVerbReinflection:
    """Test cases for verb reinflection patterns."""

    def test_irregular_suru_verbs(self):
        """Test する-verb conjugations."""
        assert reinflect_verb("し", "する") == "し"
        assert reinflect_verb("して", "する") == "して"
        assert reinflect_verb("した", "する") == "した"
        assert reinflect_verb("すれ", "する") == "すれ"
        assert reinflect_verb("しよう", "する") == "しよう"
        assert reinflect_verb("さ", "する") == "さ"

        # With kanji
        assert reinflect_verb("し", "為る") == "し"
        assert reinflect_verb("して", "為る") == "して"

    def test_irregular_kuru_verbs(self):
        """Test くる-verb conjugations."""
        assert reinflect_verb("き", "くる") == "き"
        assert reinflect_verb("きて", "くる") == "きて"
        assert reinflect_verb("きた", "くる") == "きた"
        assert reinflect_verb("くれ", "くる") == "くれ"
        assert reinflect_verb("こよう", "くる") == "こよう"

        # With kanji
        assert reinflect_verb("来", "来る") == "き"
        assert reinflect_verb("きて", "来る") == "きて"

    def test_irregular_iku_verbs(self):
        """Test いく special case (いって not いいて)."""
        assert reinflect_verb("いって", "いく") == "いって"
        assert reinflect_verb("いった", "いく") == "いった"

    def test_ichidan_verbs(self):
        """Test る-verb (ichidan) conjugations."""
        # 食べる
        assert reinflect_verb("たべ", "たべる") == "たべ"  # masu-stem
        assert reinflect_verb("たべて", "たべる") == "たべて"  # te-form
        assert reinflect_verb("たべた", "たべる") == "たべた"  # past
        assert reinflect_verb("たべれ", "たべる") == "たべれ"  # imperative
        assert reinflect_verb("たべよう", "たべる") == "たべよう"  # volitional
        assert reinflect_verb("たべば", "たべる") == "たべば"  # conditional
        assert reinflect_verb("たべない", "たべる") == "たべない"  # negative
        assert reinflect_verb("たべられる", "たべる") == "たべられる"  # passive/potential
        assert reinflect_verb("たべさせる", "たべる") == "たべさせる"  # causative
        assert reinflect_verb("たべている", "たべる") == "たべている"  # progressive
        assert reinflect_verb("たべてある", "たべる") == "たべてある"  # state
        assert reinflect_verb("たべておく", "たべる") == "たべておく"  # preparation

        # 見る
        assert reinflect_verb("み", "みる") == "み"
        assert reinflect_verb("みて", "みる") == "みて"
        assert reinflect_verb("みた", "みる") == "みた"

    def test_godan_u_verbs(self):
        """Test う-ending godan verbs."""
        # 買う
        assert reinflect_verb("かい", "かう") == "かい"  # i-form
        assert reinflect_verb("かった", "かう") == "かった"  # past
        assert reinflect_verb("かって", "かう") == "かって"  # te-form
        assert reinflect_verb("かえば", "かう") == "かえば"  # conditional
        assert reinflect_verb("かおう", "かう") == "かおう"  # volitional
        assert reinflect_verb("かわない", "かう") == "かわない"  # negative
        assert reinflect_verb("かわれる", "かう") == "かわれる"  # passive
        assert reinflect_verb("かわせる", "かう") == "かわせる"  # causative
        assert reinflect_verb("かえ", "かう") == "かえ"  # imperative

    def test_godan_ku_verbs(self):
        """Test く-ending godan verbs."""
        # 書く
        assert reinflect_verb("かき", "かく") == "かき"  # i-form
        assert reinflect_verb("かいた", "かく") == "かいた"  # past
        assert reinflect_verb("かいて", "かく") == "かいて"  # te-form
        assert reinflect_verb("かけば", "かく") == "かけば"  # conditional
        assert reinflect_verb("かこう", "かく") == "かこう"  # volitional
        assert reinflect_verb("かかない", "かく") == "かかない"  # negative

    def test_godan_gu_verbs(self):
        """Test ぐ-ending godan verbs."""
        # 泳ぐ
        assert reinflect_verb("およぎ", "およぐ") == "およぎ"  # i-form
        assert reinflect_verb("およいだ", "およぐ") == "およいだ"  # past
        assert reinflect_verb("およいで", "およぐ") == "およいで"  # te-form

    def test_godan_su_verbs(self):
        """Test す-ending godan verbs."""
        # 話す
        assert reinflect_verb("はなし", "はなす") == "はなし"  # i-form
        assert reinflect_verb("はなした", "はなす") == "はなした"  # past
        assert reinflect_verb("はなして", "はなす") == "はなして"  # te-form

    def test_godan_tsu_verbs(self):
        """Test つ-ending godan verbs."""
        # 立つ
        assert reinflect_verb("たち", "たつ") == "たち"  # i-form
        assert reinflect_verb("たった", "たつ") == "たった"  # past
        assert reinflect_verb("たって", "たつ") == "たって"  # te-form

    def test_godan_nu_verbs(self):
        """Test ぬ-ending godan verbs."""
        # 死ぬ
        assert reinflect_verb("しに", "しぬ") == "しに"  # i-form
        assert reinflect_verb("しんだ", "しぬ") == "しんだ"  # past
        assert reinflect_verb("しんで", "しぬ") == "しんで"  # te-form

    def test_godan_bu_verbs(self):
        """Test ぶ-ending godan verbs."""
        # 飛ぶ
        assert reinflect_verb("とび", "とぶ") == "とび"  # i-form
        assert reinflect_verb("とんだ", "とぶ") == "とんだ"  # past
        assert reinflect_verb("とんで", "とぶ") == "とんで"  # te-form

    def test_godan_mu_verbs(self):
        """Test む-ending godan verbs."""
        # 読む
        assert reinflect_verb("よみ", "よむ") == "よみ"  # i-form
        assert reinflect_verb("よんだ", "よむ") == "よんだ"  # past
        assert reinflect_verb("よんで", "よむ") == "よんで"  # te-form

    def test_godan_ru_verbs(self):
        """Test る-ending godan verbs (not ichidan)."""
        # 作る
        assert reinflect_verb("つくり", "つくる") == "つくり"  # i-form
        assert reinflect_verb("つくった", "つくる") == "つくった"  # past
        assert reinflect_verb("つくって", "つくる") == "つくって"  # te-form

    def test_kudasai_pattern(self):
        """Test ください pattern."""
        assert reinflect_verb("いってください", "いう") == "いってください"
        assert reinflect_verb("たべてください", "たべる") == "たべてください"

    def test_sokuon_ending(self):
        """Test っ ending pattern."""
        assert reinflect_verb("いっ", "いう") == "いっ"
        assert reinflect_verb("かっ", "かう") == "かっ"

    def test_no_match_returns_none(self):
        """Test that unrecognized patterns return None."""
        assert reinflect_verb("xyz", "abc") is None
        assert reinflect_verb("", "verb") is None


class TestIAdjectiveReinflection:
    """Test cases for i-adjective reinflection."""

    def test_basic_i_adjective(self):
        """Test basic i-adjective forms."""
        # 高い
        assert reinflect_i_adjective("たかい", "たかい") == "たかい"  # basic form
        assert reinflect_i_adjective("たかく", "たかい") == "たかく"  # ku-form
        assert reinflect_i_adjective("たかかった", "たかい") == "たかかった"  # past
        assert reinflect_i_adjective("たかくない", "たかい") == "たかくない"  # negative
        assert reinflect_i_adjective("たかくなかった", "たかい") == "たかくなかった"  # past negative
        assert reinflect_i_adjective("たかければ", "たかい") == "たかければ"  # conditional
        assert reinflect_i_adjective("たかかったら", "たかい") == "たかかったら"  # past conditional

    def test_irregular_ii_yoi(self):
        """Test irregular いい/よい adjective."""
        # いい
        assert reinflect_i_adjective("よく", "いい") == "よく"  # ku-form
        assert reinflect_i_adjective("よかった", "いい") == "よかった"  # past
        assert reinflect_i_adjective("よければ", "いい") == "よければ"  # conditional
        assert reinflect_i_adjective("よかったら", "いい") == "よかったら"  # past conditional
        assert reinflect_i_adjective("よくなかった", "いい") == "よくなかった"  # past negative

        # よい
        assert reinflect_i_adjective("よく", "よい") == "よく"
        assert reinflect_i_adjective("よかった", "よい") == "よかった"

        # 良い
        assert reinflect_i_adjective("よく", "良い") == "よく"
        assert reinflect_i_adjective("よかった", "良い") == "よかった"

    def test_special_nai(self):
        """Test special ない handling."""
        assert reinflect_i_adjective("ない", "ない") == "ない"

    def test_shi_form(self):
        """Test し form (adverbial)."""
        assert reinflect_i_adjective("たかし", "たかい") == "たかし"
        assert reinflect_i_adjective("うつくし", "うつくしい") == "うつくし"

    def test_katta_form(self):
        """Test かっ form (te-form connection)."""
        assert reinflect_i_adjective("たかかっ", "たかい") == "たかかっ"
        assert reinflect_i_adjective("おもしろかっ", "おもしろい") == "おもしろかっ"

    def test_no_match_returns_none(self):
        """Test unrecognized patterns return None."""
        assert reinflect_i_adjective("xyz", "たかい") is None
        assert reinflect_i_adjective("たかい", "xyz") is None  # not ending in い


class TestNaAdjectiveReinflection:
    """Test cases for na-adjective reinflection."""

    def test_basic_na_adjective(self):
        """Test basic na-adjective forms."""
        # きれい
        assert reinflect_na_adjective("きれい", "きれい") == "きれい"  # basic form
        assert reinflect_na_adjective("きれいだった", "きれい") == "きれいだった"  # past
        assert reinflect_na_adjective("きれいでした", "きれい") == "きれいでした"  # polite past
        assert reinflect_na_adjective("きれいで", "きれい") == "きれいで"  # te-form

    def test_conditional_forms(self):
        """Test conditional forms."""
        assert reinflect_na_adjective("きれいなら", "きれい") == "きれいなら"  # conditional
        assert reinflect_na_adjective("きれいだったら", "きれい") == "きれいだったら"  # past conditional

    def test_negative_forms(self):
        """Test negative forms."""
        assert reinflect_na_adjective("きれいじゃない", "きれい") == "きれいじゃない"  # negative
        assert reinflect_na_adjective("きれいではない", "きれい") == "きれいではない"  # formal negative
        assert reinflect_na_adjective("きれいじゃなかった", "きれい") == "きれいじゃなかった"  # past negative
        assert reinflect_na_adjective("きれいではなかった", "きれい") == "きれいではなかった"  # formal past negative

    def test_adverbial_form(self):
        """Test adverbial に form."""
        assert reinflect_na_adjective("きれいに", "きれい") == "きれいに"
        assert reinflect_na_adjective("しずかに", "しずか") == "しずかに"

    def test_various_na_adjectives(self):
        """Test with various na-adjectives."""
        # 便利
        assert reinflect_na_adjective("べんり", "べんり") == "べんり"
        assert reinflect_na_adjective("べんりだった", "べんり") == "べんりだった"
        assert reinflect_na_adjective("べんりで", "べんり") == "べんりで"
        assert reinflect_na_adjective("べんりに", "べんり") == "べんりに"

        # 静か
        assert reinflect_na_adjective("しずか", "しずか") == "しずか"
        assert reinflect_na_adjective("しずかだった", "しずか") == "しずかだった"

    def test_fallback_behavior(self):
        """Test fallback to dictionary form."""
        # Unrecognized patterns should return dictionary form
        assert reinflect_na_adjective("xyz", "きれい") == "きれい"
        assert reinflect_na_adjective("", "しずか") == "しずか"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_strings(self):
        """Test behavior with empty strings."""
        assert reinflect_verb("", "") is None
        assert reinflect_verb("surface", "") is None
        assert reinflect_verb("", "dict") is None

        assert reinflect_i_adjective("", "たかい") is None
        assert reinflect_i_adjective("surface", "") is None

    def test_identical_surface_and_dictionary(self):
        """Test when surface and dictionary forms are identical."""
        assert reinflect_verb("する", "する") is None  # No special handling for identical
        assert reinflect_i_adjective("たかい", "たかい") == "たかい"  # Should work for adjectives
        assert reinflect_na_adjective("きれい", "きれい") == "きれい"

    def test_complex_compound_verbs(self):
        """Test compound verbs with する."""
        # 勉強する -> 勉強し
        assert reinflect_verb("べんきょうし", "べんきょうする") == "べんきょうし"
        assert reinflect_verb("べんきょうして", "べんきょうする") == "べんきょうして"
        assert reinflect_verb("べんきょうした", "べんきょうする") == "べんきょうした"

    def test_long_adjectives(self):
        """Test longer adjective forms."""
        # おもしろい
        assert reinflect_i_adjective("おもしろい", "おもしろい") == "おもしろい"
        assert reinflect_i_adjective("おもしろく", "おもしろい") == "おもしろく"
        assert reinflect_i_adjective("おもしろかった", "おもしろい") == "おもしろかった"
        assert reinflect_i_adjective("おもしろくない", "おもしろい") == "おもしろくない"


if __name__ == "__main__":
    pytest.main([__file__])
