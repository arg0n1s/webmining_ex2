import TextStatistics as ts
from pathlib import Path
import pickle

def get_feature_vector(path):
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

engl = get_feature_vector("Texte/Englisch")
deut = get_feature_vector("Texte/Deutsch")
span = get_feature_vector("Texte/Spanisch")

pickle.dump( engl, open( "out/english_features", "wb" ) )
pickle.dump( deut, open( "out/german_features", "wb" ) )
pickle.dump( span, open( "out/spanish_features", "wb" ) )