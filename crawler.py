import urllib.request
import urllib.parse
from bs4 import BeautifulSoup as bs
import pickle
import codecs
from threading import Thread
import ssl
import random
import time

class Page:

    def __init__(self, url, parent, content):
        self.url = url
        self.parent = parent
        self.content = content
        self.children = []
        self.num_of_children = 0

    def __str__(self):
        return self.url+" -> containing " + str(self.num_of_children) + " out-going links"

    def __repr__(self):
        return self.__str__()

    def add_child(self, child):
        self.children.append(child)
        self.num_of_children += 1

class Crawler:

    def __init__(self, num_of_threads=350, min_visited_pages=300):
        self.num_of_threads = num_of_threads
        self.min_visited_pages = min_visited_pages
        self.threading_active = True

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.cert = ctx

        self.queue = []
        self.url_cache = {}
        self.url_out = {}
        self.active_threads = []
        self.waiting_threads = []

    def new_crawl(self, initial_page):

        self.queue = []
        self.url_cache = {}
        self.url_out = {}

        self.queue.append([initial_page, None])

        self.threads = []

        watcher = Thread(target=self.__thread_watcher)
        watcher.start()
        creator = Thread(target=self.__thread_creator)
        creator.start()
        dispatcher = Thread(target=self.__thread_dispatcher)
        dispatcher.start()

        while self.url_out.__len__() < self.min_visited_pages:
            print("Num of act. Threads: ", self.active_threads.__len__(), " Num of waiting Threads: ", self.waiting_threads.__len__())
            print("Queue size: ", self.queue.__len__(), " Url Cache size: ", self.url_cache.__len__(), " Url out size: ", self.url_out.__len__())
            time.sleep(0.5)

        self.threading_active = False

        for thread in self.threads:
            thread.join()

        dispatcher.join()
        creator.join()
        watcher.join()


        print("Queue size: ", self.queue.__len__(), " Url Cache size: ", self.url_cache.__len__(), " Url out size: ",
              self.url_out.__len__())

    def __thread_watcher(self):
        thresh = self.num_of_threads*0.7
        while self.threading_active:
            if self.active_threads.__len__()>thresh:
                active = []
                for thread in self.active_threads:
                    if thread.is_alive():
                        active.append(thread)
                self.active_threads = active
            time.sleep(0.1)

    def __thread_creator(self):
        while self.threading_active:
            if self.waiting_threads.__len__() < self.num_of_threads and self.queue.__len__() > 0 and self.url_out.__len__() < self.min_visited_pages:
                index = random.randint(0,self.queue.__len__()-1)
                t = Thread(target=self.__crawl_thread, args=(self.queue.pop(index),))
                self.waiting_threads.append(t)

    def __thread_dispatcher(self):
        while self.threading_active:
            if self.active_threads.__len__() < self.num_of_threads and self.waiting_threads.__len__()>0 and self.url_out.__len__() < self.min_visited_pages:
                t = self.waiting_threads.pop()
                self.active_threads.append(t)
                t.start()

    def __crawl_thread(self, url):
        crawled_links = {}

        try:
            page = urllib.request.urlopen(url[0], timeout=0.5, context=self.cert)

            s = bs(page,
                   "html.parser")  # this should use lxml as parser but its a pain in the ass to install on windows
            for link in s.find_all('a'):
                potential_link = link.get('href')
                check = urllib.parse.urlparse(potential_link)
                if check.scheme is '' or check.netloc is '':
                    potential_link = url[0] + potential_link
                if potential_link not in crawled_links.keys() and potential_link not in self.url_cache.keys():
                    crawled_links[potential_link] = url[0]
                    # print(potential_link)

            self.url_cache[url[0]] = s
            if type(s) is bs:
                if url[1] in self.url_out.keys():
                    self.url_out[url[0]] = Page(url[0], self.url_out[url[1]], s)
                    self.url_out[url[1]].add_child(self.url_out[url[0]])
                else:
                    self.url_out[url[0]] = Page(url[0], None, s)

        except Exception as inst:
            # print(inst)
            self.url_cache[url[0]] = None
        self.queue.extend(list(crawled_links.items()))
        #random.shuffle(self.queue)
        # print("Visited url: ", url, " Num:", url_out.__len__()," Visited: ", url_cache.__len__())

    def save_crawl_urls(self, default_path = "crawl/"):
        path = default_path + "visited_sites.txt"
        urls = ""
        counter = 0
        for item in self.url_out:
            counter += 1
            urls += str(counter) + ". Url=" + item + " // Parent=" + str(self.url_out[item].parent) + "\n"
        file = codecs.open(path, 'w', 'utf-8')
        file.write(urls)
        file.close()
'''
def start_crawl(initial_page, limit=300, numOfThreads=500):

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    queue = []
    url_cache = {}
    url_out = {}

    queue.append([initial_page, None])

    threads = []

    while url_out.__len__() < limit:
        active = []
        for thread in threads:
            if thread.is_alive():
                active.append(thread)
        threads = active
        print("Num of Threads: ", threads.__len__(), "-->pre")
        random.shuffle(queue)
        while queue.__len__()>0 and threads.__len__()<=numOfThreads and url_out.__len__() < limit:
            t = Thread(target=crawl_thread, args=(queue.pop(), queue, url_cache, url_out, limit, ctx))
            t.start()
            threads.append(t)
        print("Num of Threads: ", threads.__len__(), "-->post")
        print("Queue size: ",queue.__len__(), " Url Cache size: ",url_cache.__len__(), " Url out size: " ,url_out.__len__())
        current = url_out.__len__()
        random.shuffle(queue)

        while url_out.__len__()-current < 1:
            time.sleep(0.1)

    for thread in threads:
        thread.join()

    print("Queue size: ", queue.__len__(), " Url Cache size: ", url_cache.__len__(), " Url out size: ",
          url_out.__len__())
    #pickle.dump(url_cache, open("crawl/result", "wb"))
    return url_out



def crawl_thread(url, queue, url_cache, url_out, limit, cert):
    crawled_links = {}

    try:
        page = urllib.request.urlopen(url[0], timeout=0.5, context=cert)

        s = bs(page, "html.parser") # this should use lxml as parser but its a pain in the ass to install on windows
        for link in s.find_all('a'):
            potential_link = link.get('href')
            check = urllib.parse.urlparse(potential_link)
            if check.scheme is '' or check.netloc is '':
                potential_link = url[0] + potential_link
            if potential_link not in crawled_links.keys() and potential_link not in url_cache.keys() and queue.__len__()<10000:
                crawled_links[potential_link] = url[0]
                #print(potential_link)

        url_cache[url[0]] =  s
        if type(s) is bs:
            if url[1] in url_out.keys():
                url_out[url[0]] = Page(url[0], url_out[url[1]], s)
                url_out[url[1]].add_child(url_out[url[0]])
            else:
                url_out[url[0]] = Page(url[0], None, s)

    except Exception as inst:
        #print(inst)
        url_cache[url[0]] = None
    queue.extend(list(crawled_links.items()))
    #print("Visited url: ", url, " Num:", url_out.__len__()," Visited: ", url_cache.__len__())

def save_crawl_as_html(db):
    #db = pickle.load( open( "crawl/result", "rb" ) )
    default_path = "crawl/websites/"
    for item in db:
        path = default_path+str(hash(item))+".html"
        if type(db[item].content) is bs:
            file = codecs.open(path, 'w', 'utf-8')
            file.write(db[item].content.prettify(formatter="html"))
            file.close()

def save_crawl_urls(db):
    #db = pickle.load(open("crawl/result", "rb"))
    default_path = "crawl/"
    path = default_path + "visited_sites.txt"
    urls = ""
    counter = 0
    for item in db:
        counter += 1
        urls += str(counter) + ". Url=" + item + " // Parent=" + str(db[item].parent) + "\n"
    file = codecs.open(path, 'w', 'utf-8')
    file.write(urls)
    file.close()
'''

#db = start_crawl("http://www.spiegel.de", 100, 250)
#save_crawl_as_html(db)
#save_crawl_urls(db)

c = Crawler()
c.new_crawl("http://www.spiegel.de")
c.save_crawl_urls()
