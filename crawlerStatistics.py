import matplotlib.pyplot as plt
import numpy as np

def parseFile(path):
    startSymbols = ["Url=", "Parent=", "containing "]
    endSymbols = [" //", " ->", " out-going"]
    data = []
    for index, line in enumerate(open(path, 'r')):
        if index is not 0:
            url = extractDataFromLine(line, startSymbols[0], endSymbols[0])
            parent = extractDataFromLine(line, startSymbols[1], endSymbols[1])
            outLinks = extractDataFromLine(line, startSymbols[2], endSymbols[2])
            aLine = [url, parent, int(outLinks)]
            data.append(aLine)
    data = sortList(data, 2)
    return data


def extractDataFromLine(line, startSymbol, endSymbol):
    startIndex = line.index(startSymbol) + len(startSymbol)
    endIndex = line.index(endSymbol)
    data = line[startIndex:endIndex]
    return data


def sortList(list, itemIndex, descending=True):
    return sorted(list, key=lambda item: item[itemIndex], reverse=descending)


def plotURLsOccurences(data):
    """"from file links are already unique -> how to get number of duplicate sites?"""
    websites = {}
    for d in data:
        websites[d[0]] = ((websites[d[0]] + 1) if d[0] in websites else 1)
    print(websites)


def plotUrlsPerSite(data, numSites):
    websites = {}
    """"get unique parent links"""
    for bar in data:
        websites[bar[1]] = bar[2]
    websites = sortList(websites.items(), 1)

    name = []
    numLinks = []

    """name-list and number of out going links as list for plot"""
    for apage in websites:
        name.append(apage[0])
        numLinks.append((apage[1]))

    """the plot"""
    name = name[0:numSites]
    numLinks = numLinks[0:numSites]
    y_pos = np.arange(len(numLinks))
    fig, ax = plt.subplots()
    rects = plt.bar(y_pos, numLinks, align='center', alpha=0.5)
    plt.axis([-0.5, len(name), 0, numLinks[0]+10])
    plt.xticks(y_pos)

    """websites as label for the bars"""
    for index, rect in enumerate(rects):
        nameRect = name[index]
        ax.text(rect.get_x() + rect.get_width() / 2., 1,
                nameRect,
                ha='center', va='bottom', rotation='90', size=10)

    plt.show()


path = "crawl/wiki_de_seb.txt"
d = parseFile(path)
plotUrlsPerSite(d, 20)
plotURLsOccurences(d)