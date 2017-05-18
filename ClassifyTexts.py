import TextStatistics as ts
import pickle
from pathlib import Path
import codecs

def load_feature_vectors(param="sl"):
    dict = {}
    if param is "sl":
        dict["german"]=pickle.load( open( "out/german_features", "rb" ) )
        dict["english"] = pickle.load(open("out/english_features", "rb"))
        dict["spanish"] = pickle.load(open("out/spanish_features", "rb"))
    elif param is "dl":
        dict["german"] = pickle.load(open("out/german_dl_features", "rb"))
        dict["english"] = pickle.load(open("out/english_dl_features", "rb"))
        dict["spanish"] = pickle.load(open("out/spanish_dl_features", "rb"))
    return dict

def calc_histogram_intersection(tokens, feature_vectors):
    dict={}
    for feature_vector in feature_vectors:
        dict[feature_vector]=0
        for index, token in enumerate(tokens.labels):
            if token in feature_vectors[feature_vector].keys():
                dict[feature_vector] = dict[feature_vector] + min(feature_vectors[feature_vector][token], tokens.relFrequency[index])
        weight = 0
        for key in feature_vectors[feature_vector]:
            weight = weight + feature_vectors[feature_vector][key]
        dict[feature_vector] = dict[feature_vector]/weight
    return dict

def classify_text_singleletters(path, feature_vectors):
    texts = ts.TextStatistics(path)
    letters = ts.get_lexical_sorting(texts.letters)
    result = calc_histogram_intersection(letters, feature_vectors)

    best_score = 0
    best_label = "none"

    for label in result:
        if result[label] > best_score:
            best_label = label
            best_score = result[label]
    print("The text is probably written in ",best_label,". Result of histogram intersection d=",best_score)
    return best_label

def classify_text_dblletters(path, feature_vectors):
    texts = ts.TextStatistics(path)
    letters = ts.get_lexical_sorting(texts.doubleLetters)
    result = calc_histogram_intersection(letters, feature_vectors)

    best_score = 0
    best_label = "none"

    for label in result:
        if result[label] > best_score:
            best_label = label
            best_score = result[label]
    print("The text is probably written in ",best_label,". Result of histogram intersection d=",best_score)
    return best_label

def classify_unigrams():
    p = Path("Texte/challenge")
    files = list(p.glob("*.unigram.txt"))
    fv = load_feature_vectors()
    labels = [classify_text_singleletters(path, fv) for path in files]

    out = ""
    for index, label in enumerate(labels):
        out = out + str(index)+". "+label+" ("+files[index].__str__()+") \n"
    file = codecs.open("out/unigrams-out.txt", 'w', 'utf-8')
    file.write(out)
    file.close()

def classify_bigrams():
    p = Path("Texte/challenge")
    files = list(p.glob("*.bigram.txt"))
    fv = load_feature_vectors("dl")
    labels = [classify_text_dblletters(path, fv) for path in files]

    out = ""
    for index, label in enumerate(labels):
        out = out + str(index)+". "+label+" ("+files[index].__str__()+") \n"
    file = codecs.open("out/bigrams-out.txt", 'w', 'utf-8')
    file.write(out)
    file.close()

def check_on_testdata(param="sl"):
    p = Path("Test Data")
    files = list(p.glob("*.txt"))

    fv = load_feature_vectors(param)
    if param is "sl":
        labels = [classify_text_singleletters(path, fv) for path in files]
    elif param is "dl":
        labels = [classify_text_dblletters(path, fv) for path in files]

    out = ""
    for index, label in enumerate(labels):
        out = out + str(index) + ". " + label + " (" + files[index].__str__() + ") \n"
    file = codecs.open("out/testdata-out.txt", 'w', 'utf-8')
    file.write(out)
    file.close()

classify_unigrams()
classify_bigrams()
check_on_testdata()
