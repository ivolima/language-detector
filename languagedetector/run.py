# -*- coding: utf-8 -*-
from nltk import word_tokenize, FreqDist
from nltk.util import ngrams
from nltk.corpus import stopwords, europarl_raw
from nltk.tokenize import RegexpTokenizer
import ipdb, pickle, sys

tokenizer = RegexpTokenizer(r'\w+')
languages_corpus = {}
languages_profiles = {}
SUPPORTED_LANGUAGES = ['english', 'german', 'portuguese', 'spanish', 'italian', 'french']

def sanitize(text):
    return ' '.join(tokenizer.tokenize(text.lower()))

def get_languages_rates(tokens):
    languages_rates = {}
    languages = stopwords.fileids()

    for lang in languages:
        languages_rates[lang] = len(set.intersection(set(tokens), set(stopwords.words(lang))))
    return languages_rates

def compare_ngrams_profiles(language_profile, query_profile):
    _ngrams_language_profile = [t[0] for t in language_profile]
    _ngrams_query_profile = [t[0] for t in query_profile]
    cummulative_distance = 0
    max_distance = len(_ngrams_query_profile)
    #ipdb.set_trace()
    for ngram in _ngrams_query_profile:
        _index = _ngrams_query_profile.index(ngram)
        try:
            _language_index = _ngrams_language_profile.index(ngram)
        except ValueError:
            _language_index = max_distance

        partial_distance = abs(_language_index - _index)
        cummulative_distance += partial_distance
    return cummulative_distance

def generate_ngrams_profile(raw_text, profile_size, min_size=2, max_size=3):
    raw_ngrams = []
    text = sanitize(raw_text)
    for n in range(min_size, max_size+1):
        for ngram in ngrams(text, n):
            raw_ngrams.append(''.join(unicode(i) for i in ngram))
    #raw_ngrams = ngrams(sanitize(raw_text), n=ngram_size)
    #ngrams_as_list = [''.join(t) for t in list(raw_ngrams)]
    #fdist = FreqDist(ngrams_as_list)
    fdist = FreqDist(raw_ngrams)
    return fdist.most_common(n=profile_size)

def get_corpus(language):
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

def load_languages_profiles(profile_size):
    for lang in SUPPORTED_LANGUAGES:
        try:
            languages_profiles[lang] = pickle.load(open("profiles/{0}_{1}.pk".format(lang, profile_size), "rb"))
            #print "{0} profile loaded..".format(lang)
        except:
            languages_profiles[lang] = generate_ngrams_profile(get_corpus(lang), profile_size)
            pickle.dump(languages_profiles[lang], open("profiles/{0}_{1}.pk".format(lang, profile_size), "wb"))
            print "{0} profile persisted for future use..".format(lang)

def guess_language(text):
    query_profile = generate_ngrams_profile(text, profile_size=400)
    results = {key:compare_ngrams_profiles(languages_profiles[key], query_profile) for key in languages_profiles}
    #print "##############################################################"
    #print "QUERY PROFILE: {0}".format([l[0] for l in query_profile[0:15]])
    #print "QUERY PROFILE: {0}".format([l[0] for l in query_profile])
    return results, query_profile

def print_languages_profiles(top=15):
    for lang in sorted(languages_profiles, key=languages_profiles.get, reverse=True):
        print "{0}({2}) \t {1}".format(lang, [l[0] for l in languages_profiles[lang][0:top]], len(languages_profiles[lang]))


if __name__ == "__main__":
    print "Starting process..."
    load_languages_profiles(profile_size=200)
    #ipdb.set_trace()
    print "Profiles loaded successfully"
    queries = []

    queries.append(("EN", u'''Fast-forward to 2016 and Harlow has over one million followers on Instagram, she's the face of Spanish fashion label Desigual and she's been shot by fashion photographer and director of online platform SHOWstudio Nick Knight, whose portfolio includes Kate Moss, Lady Gaga and Kanye.'''))
    queries.append(("DE", u'''Langsam gesprochene Nachrichten von Samstag, dem 09. Januar 2016: Nach den massiven Übergriffen in Köln will Bundeskanzlerin Angela Merkel'''))
    queries.append(("IT", u'''Hooligans di estrema destra ma anche un'altra manifestazione anti-razzista in piazza a Colonia, a seguito delle aggressioni avvenute la notte di Capodanno contro le donne, e scontri con la polizia che ha diperso il corteo anti-islam. Mentre le denunce di violenza sulle donne nella notte di Capodanno salgono a 379.'''))
    queries.append(("FR", u'''Alors que le scandale de centaines d’agressions de femmes lors du Nouvel An à Cologne secoue l’Allemagne, la chancelière Angela Merkel s’est prononcée samedi 9 janvier en faveur d’un très net durcissement des règles d’expulsion de demandeurs d’asile condamnés par la justice, l’autorisant même pour ceux condamnés à une peine avec sursis.'''))
    test_set = dict(queries)

    #results, q_profile = guess_language(test_set['EN'])
    print_languages_profiles()
    #for r in sorted(results):
    #    print "{0}: {1}".format(r, results[r])
    #print
    #print "{0} ----> {1}".format("DE", min(results, key=results.get).upper())
    #sys.exit(0)

    for lang, sample in queries:
        print "###############################################################"
        print "TEXT: {0}".format(sample[0:80].encode("utf-8"))
        #print "###############################################################"
        results, q_profile = guess_language(sample)
        print "{0} ----> {1}".format(lang, min(results, key=results.get).upper())
        for lang in sorted(results, key=results.get, reverse=True):
            print "{0}: {1}".format(lang, results[lang])
        #print "##############################################################"
