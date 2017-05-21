import urllib.request
import urllib.parse
from bs4 import BeautifulSoup as bs
import pickle
import codecs
from threading import Thread
import ssl
import random
import time
from joblib import Parallel, delayed
import multiprocessing


def calc_jaccard_index(page1, page2):
    if page1.set_of_shingles.__len__() < 1 or page2.set_of_shingles.__len__() < 1:
        return 0
    return (page1.set_of_shingles & page2.set_of_shingles).__len__() / (
        page1.set_of_shingles | page2.set_of_shingles).__len__()


def load_crawl_from_disk(default_path="crawl/", filename="result"):
    crawl = pickle.load(open(default_path + filename, "rb"))
    crawl.reinit_cert()
    return crawl


class Page:
    def __init__(self, url, parent, host, content):
        self.url = url
        self.parent = parent
        self.host = host
        self.content = content
        self.children = []
        self.num_of_children = 0
        self.set_of_shingles = set()

    def __str__(self):
        return self.url + " -> containing " + str(self.num_of_children) + " out-going links"

    def __repr__(self):
        return self.__str__()

    def add_child(self, child):
        self.children.append(child)
        self.num_of_children += 1

    def extract_shingles(self, words_per_shingle=3):
        clean_text = bs(self.content, "html.parser").get_text()
        wordList = ''.join([c if c.isalpha() else ' ' for c in clean_text]).lower().split()
        shingles = []
        for index, word in enumerate(wordList):
            if index + words_per_shingle < wordList.__len__():
                shingles.append(' '.join(wordList[index:index + words_per_shingle]))
            else:
                break
        self.set_of_shingles = set(shingles)

class Crawler:
    def __init__(self, num_of_threads=250, min_visited_pages=300):
        self.num_of_threads = num_of_threads
        self.min_visited_pages = min_visited_pages
        self.threading_active = True

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.cert = ctx

        self.queue = {}
        self.probed_urls = {}
        self.visited_urls = {}
        self.unique_urls = {}
        self.active_threads = []
        self.waiting_threads = []

        self.hyperlink_count = {}
        self.host_visits = {}

    def reinit_cert(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.cert = ctx

    def new_crawl(self, initial_page):

        self.queue = {}
        self.probed_urls = {}
        self.visited_urls = {}

        self.hyperlink_count = {}
        self.host_visits = {}

        initial = []
        initial.append([initial_page, None])
        self.queue[urllib.parse.urlparse(initial_page).hostname] = initial

        self.hyperlink_count[initial_page] = 1
        self.host_visits[urllib.parse.urlparse(initial_page).hostname] = 1

        self.threads = []

        watcher = Thread(target=self.__thread_watcher)
        watcher.start()
        creator = Thread(target=self.__thread_creator)
        creator.start()
        dispatcher = Thread(target=self.__thread_dispatcher)
        dispatcher.start()

        while self.visited_urls.__len__() < self.min_visited_pages:
            print("THREAD STATUS --> Num of act. Threads: ", self.active_threads.__len__(),
                  " Num of waiting Threads: ", self.waiting_threads.__len__())
            print("CRAWL STATUS  --> Queue size: ", self.queue.__len__(), " Url Cache size: ",
                  self.probed_urls.__len__(), " Url out size: ", self.visited_urls.__len__())
            time.sleep(0.5)

        self.threading_active = False

        for thread in self.active_threads:
            thread.join()

        dispatcher.join()
        creator.join()
        watcher.join()

        print("Finished! --> Queue size: ", self.queue.__len__(), " Url Cache size: ", self.probed_urls.__len__(),
              " Url out size: ",
              self.visited_urls.__len__())

    def remove_similar_pages(self, threshold=0.7):
        print("removing similar pages ...")

        self.unique_urls = {}
        for index, url in enumerate(self.visited_urls):
            unique = True
            for url2 in self.unique_urls:
                jacInd = calc_jaccard_index(self.visited_urls[url], self.unique_urls[url2])
                if jacInd >= threshold:
                    unique = False
                    unique = False
            if unique:
                self.unique_urls[url] = self.visited_urls[url]
            print("Progress: ", 100.0 * index / (self.visited_urls.__len__() - 1))
        print("Finished! --> Queue size: ", self.queue.__len__(), " Url Cache size: ", self.probed_urls.__len__(),
              " Url out size: ",
              self.visited_urls.__len__(),
              " Url unique size: ",
              self.unique_urls.__len__())

    def __thread_watcher(self):
        thresh = int(self.num_of_threads * 0.7)
        while self.threading_active:
            if self.active_threads.__len__() > thresh:
                active = []
                for thread in self.active_threads:
                    if thread.is_alive():
                        active.append(thread)
                self.active_threads = active
            time.sleep(0.1)

    def __thread_creator(self):
        while self.threading_active:
            if self.waiting_threads.__len__() < self.num_of_threads and self.queue.__len__() > 0 and self.visited_urls.__len__() < self.min_visited_pages:
                keySet = list(self.queue.keys())
                rndKey = keySet[random.randint(0, keySet.__len__() - 1)]
                if self.queue[rndKey].__len__() <= 0:
                    continue
                index = random.randint(0, self.queue[rndKey].__len__() - 1)
                t = Thread(target=self.__crawl_thread, args=(self.queue[rndKey].pop(index),))
                self.waiting_threads.append(t)

    def __thread_dispatcher(self):
        while self.threading_active:
            if self.active_threads.__len__() < self.num_of_threads and self.waiting_threads.__len__() > 0 and self.visited_urls.__len__() < self.min_visited_pages:
                t = self.waiting_threads.pop()
                self.active_threads.append(t)
                t.start()

    def __crawl_thread(self, url):
        crawled_links = {}
        ordered_by_host = {}
        # try to establish a connection to web host
        try:
            page = urllib.request.urlopen(url[0], timeout=0.5, context=self.cert)
            # parse web content
            s = bs(page,
                   "html.parser")  # this should use lxml as parser but its a pain in the ass to install on windows
            # extract hyperlinks
            for link in s.find_all('a'):
                potential_link = link.get('href')
                # check if link is empty
                if potential_link is "":
                    continue
                check = urllib.parse.urlparse(potential_link)
                # check if link is completely broken
                if check.scheme is '' and check.netloc is '':
                    continue
                # check for relative links
                if check.netloc is '':
                    potential_link = url[0] + "/" + potential_link
                # check for syntactical correctness
                check = urllib.parse.urlparse(potential_link)
                if check.scheme is '' or check.netloc is '':
                    continue
                # statistics crap
                if not potential_link in self.hyperlink_count.keys():
                    self.hyperlink_count[potential_link] = 1
                self.hyperlink_count[potential_link] += 1
                # extract hostname from hyperlink
                hostname = check.hostname
                # if hyperlink not yet probed or in enqueued -> enqueue
                if potential_link not in crawled_links.keys() and potential_link not in self.probed_urls.keys():
                    crawled_links[potential_link] = url[0]
                    # order hyperlinks by corresponding hostname
                    if not hostname in ordered_by_host.keys():
                        ordered_by_host[hostname] = {}
                    ordered_by_host[hostname][potential_link] = url[0]
            # remember already probed urls
            self.probed_urls[url[0]] = url[1]
            # if probing was successful add to visited urls
            if type(s) is bs:
                # extract hostname of visited page for statistics crap
                current_hostname = urllib.parse.urlparse(url[0])
                # count host visits
                if not current_hostname in self.host_visits.keys():
                    self.host_visits[current_hostname] = 1
                self.host_visits[current_hostname] += 1
                # build a crawl tree, navigating the crawl might be useful at some point
                if url[1] in self.visited_urls.keys():
                    self.visited_urls[url[0]] = Page(url[0], self.visited_urls[url[1]], current_hostname, str(s))
                    self.visited_urls[url[1]].add_child(self.visited_urls[url[0]])
                else:
                    self.visited_urls[url[0]] = Page(url[0], None, current_hostname, str(s))
                # extract shingles for later usage
                self.visited_urls[url[0]].extract_shingles(3)
        # remember hyperlinks that caused a connection error
        except Exception as inst:
            self.probed_urls[url[0]] = None
        # expand the ordered queue by the recently found hyperlinks
        for host in ordered_by_host:
            if not host in self.queue.keys():
                self.queue[host] = []
            self.queue[host].extend(list(ordered_by_host[host].items()))

    def save_crawl_urls(self, default_path="crawl/", filename="visited_sites.txt"):
        path = default_path + filename
        urls = ""
        counter = 0
        for item in self.visited_urls:
            counter += 1
            urls += str(counter) + ". Url= " + item + " // Parent=" + str(self.visited_urls[item].parent) + "\n"

        file = codecs.open(path, 'w', 'utf-8')
        file.write(urls)
        file.close()

    def save_crawl_to_disk(self, default_path="crawl/", filename="result"):
        self.cert = None
        self.active_threads = []
        self.waiting_threads = []
        pickle.dump(self, open(default_path + filename, "wb"))

# c = Crawler( 250, 400)
# c.new_crawl("http://www.wikipedia.de")
# c.save_crawl_urls("crawl/", "wiki_de.txt")
# c.save_crawl_to_disk("crawl/", "wiki_new")
# c = load_crawl_from_disk("crawl/", "wiki_new")
# c.remove_similar_pages()
