# -*- coding: utf-8 -*-
from nltk import word_tokenize, FreqDist
from nltk.util import ngrams
from nltk.corpus import stopwords, europarl_raw
from nltk.tokenize import RegexpTokenizer
import ipdb, pickle, sys, os

languages_corpus = {}

class LanguageDetector:
    """
    """

    def __init__(self, method='ngrams', profile_size=200):
        """
        """
        self.method = method
        self.profile_size = profile_size
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.supported_languages = [
                                    'english',
                                    'german',
                                    'portuguese',
                                    'spanish',
                                    'italian',
                                    'french'
                                    ]
        self.profiles = self.load_languages_profiles(self.profile_size)

    def get_corpus(self, language):
        if language == 'english':
            return europarl_raw.english.raw()
        if language == 'german':
            return europarl_raw.german.raw()
        if language == 'portuguese':
            return europarl_raw.portuguese.raw()
        if language == 'spanish':
            return europarl_raw.spanish.raw()
        if language == 'italian':
            return europarl_raw.italian.raw()
        if language == 'french':
            return europarl_raw.french.raw()

    def load_languages_profiles(self, profile_size=200):
        """
        Parameters
        ----------
        profile_size : int, optional (default=200)

        Returns
        -------
        profiles : dict
        """
        profiles = {}
        current_dir = os.path.dirname(__file__)
        for lang in self.supported_languages:
            try:
                profiles[lang] = pickle.load(open(os.path.join(current_dir, "profiles/{0}_{1}.pk".format(lang, profile_size)), "rb"))
                #print "{0} profile loaded..".format(lang)
            except:
                profiles[lang] = self.generate_ngrams_profile(self.get_corpus(lang), profile_size)
                pickle.dump(profiles[lang], open(os.path.join(current_dir, "profiles/{0}_{1}.pk".format(lang, profile_size)), "wb"))
                print "{0} profile persisted for future use..".format(lang)
        return profiles

    def sanitize_text(self, text):
        """
        It reads incoming text, gets rid of punctuation and returns resulting text sanitized.

        Parameters
        ---------
        text : unicode

        Returns
        ------
        sanitized_text : unicode
        """
        sanitized_text = ' '.join(self.tokenizer.tokenize(text.lower()))
        return sanitized_text

    def guess_language(self, text):
        """
        Parameters
        ----------
        text : unicode

        Returns
        -------
        results : dict

        query_profile : FreqDist object
        """
        query_profile = self.generate_ngrams_profile(text, self.profile_size)
        results = {key:self.compare_ngrams_profiles(self.profiles[key], query_profile) for key in self.profiles}
        #print "##############################################################"
        #print "QUERY PROFILE: {0}".format([l[0] for l in query_profile[0:15]])
        #print "QUERY PROFILE: {0}".format([l[0] for l in query_profile])
        return results, query_profile

    def generate_ngrams_profile(self, text, profile_size, min_size=2, max_size=3):
        """
        It reads incoming text, generates all possible N-grams, with sizes ranging between min_size and max_size and counts the occurrences of all N-grams.

        Parameters
        ----------
        text : unicode

        profile_size : int

        min_size : int, optional (default=2)

        max_size : int, optional (default=3)

        Returns
        -------
        ngram_profile : FreqDist object

        """
        raw_ngrams = []
        text = self.sanitize_text(text)
        for n in range(min_size, max_size+1):
            for ngram in ngrams(text, n):
                raw_ngrams.append(''.join(unicode(i) for i in ngram))
        fdist = FreqDist(raw_ngrams)
        ngram_profile = fdist.most_common(n=profile_size)
        return ngram_profile

    def compare_ngrams_profiles(self, language_profile, query_profile):
        """
        It takes two N-gram profiles and calculates a simple rank-order statistic we call the “out-of-place” measure.
        This measure determines how far out of place an N-gram in one profile is from its place in the other profile.

        Parameters
        ----------
        language_profile : FreqDist object

        query_profile : FreqDist object

        Returns
        -------
        cumulative_distance : int
        """
        _ngrams_language_profile = [t[0] for t in language_profile]
        _ngrams_query_profile = [t[0] for t in query_profile]
        cummulative_distance = 0
        max_distance = len(_ngrams_query_profile)
        for ngram in _ngrams_query_profile:
            _index = _ngrams_query_profile.index(ngram)
            try:
                _language_index = _ngrams_language_profile.index(ngram)
            except ValueError:
                _language_index = max_distance

            partial_distance = abs(_language_index - _index)
            cummulative_distance += partial_distance
        return cummulative_distance

