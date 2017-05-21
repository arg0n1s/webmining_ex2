import codecs
import matplotlib.pyplot as plt
import numpy as np

class TokenStatistic:

    def __init__(self, data=[], count=0):
        self.labels = [item[0] for item in data]
        self.absFrequency = [item[1] for item in data]
        self.relFrequency = [item[2] for item in data]
        self.tokenCount = count

def get_lexical_sorting(token):
    alist = []
    for index, item in enumerate(token.labels):
        alist.append([item, token.absFrequency[index], token.relFrequency[index]])
    alist = sorted(alist, key=lambda item: item[0])
    return TokenStatistic(alist, token.tokenCount)

class TextStatistics:

    def __init__(self, path, text=None):
        self.text = []
        self.words = TokenStatistic()
        self.letters = TokenStatistic()
        self.doubleLetters = TokenStatistic()
        self.update_statistics(path, text)

    def update_statistics(self, path, text):
        if path is None and not text is None:
            self.text = text
        else:
            self.__parse_text_file(path)

        self.__extract_letters()
        self.__extract_words()
        self.__calc_token_statistics()

    def plot_statistics(self):
        f, (plt1, plt2, plt3) = plt.subplots(3, 2, figsize=(18, 10), frameon=True, subplotpars=None, tight_layout=True)
        plt1[0].set_title("words - abs. frequency")
        plt1[1].set_title("words - rel. frequency")
        plt2[0].set_title("letters - abs. frequency")
        plt2[1].set_title("letters - rel. frequency")
        plt3[0].set_title("dbl.letters - abs. frequency")
        plt3[1].set_title("dbl.letters - rel. frequency")

        rect0 = plt1[0].bar(np.arange(30), self.words.absFrequency[0:30], clip_on=True,
                                 color='#00c0c0')
        rect1 = plt1[1].bar(np.arange(30), self.words.relFrequency[0:30], clip_on=True,
                                 color='#00c0c0')

        self.__autolabel(self.words.labels, rect0, plt1[0])
        self.__autolabel(self.words.labels, rect1, plt1[1])

        rect0 = plt2[0].bar(np.arange(self.letters.labels.__len__()), self.letters.absFrequency, clip_on=True,
                            color='#00c0c0')
        rect1 = plt2[1].bar(np.arange(self.letters.labels.__len__()), self.letters.relFrequency, clip_on=True,
                            color='#00c0c0')

        self.__autolabel(self.letters.labels, rect0, plt2[0])
        self.__autolabel(self.letters.labels, rect1, plt2[1])

        rect0 = plt3[0].bar(np.arange(self.doubleLetters.labels.__len__()), self.doubleLetters.absFrequency, clip_on=True,
                            color='#00c0c0')
        rect1 = plt3[1].bar(np.arange(self.doubleLetters.labels.__len__()), self.doubleLetters.relFrequency, clip_on=True,
                            color='#00c0c0')

        self.__autolabel(self.doubleLetters.labels, rect0, plt3[0])
        self.__autolabel(self.doubleLetters.labels, rect1, plt3[1])

        plt.show()

    def __autolabel(self, labels, rects, ax):
        for index, rect in enumerate(rects):
            label = labels[index]
            ax.text(rect.get_x() + rect.get_width() / 2., rect.get_height() + rect.get_height() * 0.05,
                    label,
                    ha='center', va='bottom', rotation='90', weight='bold')

    def __parse_text_file(self, path):
        self.text = codecs.open(path, 'r', 'utf-8').read()

    def __extract_letters(self):
        string = ''.join([c if c.isalpha() else '' for c in self.text]).lower()
        dict = {}
        for char in string:
            if char in dict.keys():
                dict[char] = dict[char] + 1
            else:
                dict[char] = 1
        letters = sorted(dict.items(), key=lambda item: item[1], reverse=True)
        self.letters.labels = [item[0] for item in letters]
        self.letters.absFrequency = [item[1] for item in letters]

        listOfDoubleLetters = {}
        '''
        for i, item in enumerate(letters):
            seq = ''.join(item[0] + item[0])
            counter = 0
            index = string.find(seq, 0)
            while index >= 0:
                counter = counter + 1
                index = string.find(seq, index + 1)
            if counter > 0:
                listOfDoubleLetters.append([seq, counter])
        '''
        for i in range(0,string.__len__(),2):
            if i+1 <string.__len__():
                seq = ''.join(string[i] + string[i+1])
                if seq in listOfDoubleLetters.keys():
                    listOfDoubleLetters[seq] = listOfDoubleLetters[seq] + 1
                else:
                    listOfDoubleLetters[seq] = 1
            else:
                break

        listOfDoubleLetters = sorted(listOfDoubleLetters.items(), key=lambda item: item[1], reverse=True)
        self.doubleLetters.labels = [item[0] for item in listOfDoubleLetters]
        self.doubleLetters.absFrequency = [item[1] for item in listOfDoubleLetters]

    def __extract_words(self):
        listOfWords = ''.join([c if c.isalnum() and not c.isnumeric() else ' ' for c in self.text]).lower().split()
        dict = {}
        for word in listOfWords:
            if word in dict.keys():
                dict[word] = dict[word] + 1
            else:
                dict[word] = 1
        words = sorted(dict.items(), key=lambda item: item[1], reverse=True)
        self.words.labels = [item[0] for item in words]
        self.words.absFrequency = [item[1] for item in words]

    def __calc_token_statistics(self):
        self.words.tokenCount = sum(self.words.absFrequency)
        self.letters.tokenCount = sum(self.letters.absFrequency)
        self.doubleLetters.tokenCount = sum(self.doubleLetters.absFrequency)
        self.words.relFrequency = [item / self.words.tokenCount for item in self.words.absFrequency]
        self.letters.relFrequency = [item / self.letters.tokenCount for item in self.letters.absFrequency]
        self.doubleLetters.relFrequency = [item / self.doubleLetters.tokenCount for item in self.doubleLetters.absFrequency]