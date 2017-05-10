import TextStatistics as ts
import pickle

german_feature_vector = pickle.load( open( "out/german_features", "rb" ) )
english_feature_vector = pickle.load( open( "out/english_features", "rb" ) )
spanish_feature_vector = pickle.load( open( "out/spanish_features", "rb" ) )

texts = ts.TextStatistics("Texte/Deutsch/kafka - urteil.txt")
