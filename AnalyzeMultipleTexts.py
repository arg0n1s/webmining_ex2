import TextStatistics as ts
from pathlib import Path

p = Path("Texte/Deutsch/")
files = list(p.glob("*.txt"))
texts = [ts.TextStatistics(path) for path in files]
[print(item.letters.relFrequency) for item in texts]
[print(item.letters.labels) for item in texts]
