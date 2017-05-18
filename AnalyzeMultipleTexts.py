import TextStatistics as ts
from pathlib import Path
import pickle

def get_feature_vector_letters(path):
    p = Path(path)
    files = list(p.glob("*.txt"))
    texts = [ts.TextStatistics(path) for path in files]
    letters_lex = [ts.get_lexical_sorting(item.letters) for item in texts]
    dict={}
    for token in letters_lex:
        for index, l in enumerate(token.labels):
            if l in dict.keys():
                dict[l] = dict[l] + token.relFrequency[index]
            else:
                dict[l] = token.relFrequency[index]
    for letter in dict.keys():
        dict[letter]=dict[letter]/letters_lex.__len__()
    return dict

def get_feature_vector_dblletters(path):
    p = Path(path)
    files = list(p.glob("*.txt"))
    texts = [ts.TextStatistics(path) for path in files]
    letters_lex = [ts.get_lexical_sorting(item.doubleLetters) for item in texts]
    dict={}
    for token in letters_lex:
        for index, l in enumerate(token.labels):
            if l in dict.keys():
                dict[l] = dict[l] + token.relFrequency[index]
            else:
                dict[l] = token.relFrequency[index]
    for letter in dict.keys():
        dict[letter]=dict[letter]/letters_lex.__len__()
    return dict

engl = get_feature_vector_letters("Texte/Englisch")
deut = get_feature_vector_letters("Texte/Deutsch")
span = get_feature_vector_letters("Texte/Spanisch")

pickle.dump( engl, open( "out/english_sl_features", "wb" ) )
pickle.dump( deut, open( "out/german_sl_features", "wb" ) )
pickle.dump( span, open( "out/spanish_sl_features", "wb" ) )

engl = get_feature_vector_dblletters("Texte/Englisch")
deut = get_feature_vector_dblletters("Texte/Deutsch")
span = get_feature_vector_dblletters("Texte/Spanisch")

pickle.dump( engl, open( "out/english_dl_features", "wb" ) )
pickle.dump( deut, open( "out/german_dl_features", "wb" ) )
pickle.dump( span, open( "out/spanish_dl_features", "wb" ) )