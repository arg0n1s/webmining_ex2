import TextStatistics as ts
import pickle

def load_feature_vectors():
    dict = {}
    dict["german"]=pickle.load( open( "out/german_features", "rb" ) )
    dict["english"] = pickle.load(open("out/english_features", "rb"))
    dict["spanish"] = pickle.load(open("out/spanish_features", "rb"))
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

def classify_text(path, feature_vectors):
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



fv = load_feature_vectors()
classify_text("Texte/Deutsch/goethe - faust.txt", fv)
classify_text("Texte/Deutsch/kafka - urteil.txt", fv)
classify_text("Texte/Deutsch/kafka-verwandlung.txt", fv)
classify_text("Texte/Deutsch/kant - vernunft.txt", fv)
classify_text("Texte/Deutsch/nietzsche - zaratustra.txt", fv)
