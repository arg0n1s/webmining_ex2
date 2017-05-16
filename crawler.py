import urllib.request
import urllib.parse
from bs4 import BeautifulSoup as bs
import pickle
import codecs
from threading import Thread

def start_crawl(initial_page):
    start = urllib.request.urlopen(initial_page)
    soup = bs(start, 'lxml')

    url_queue = {}
    url_cache = {}

    for link in soup.find_all('a'):
        potential_link = link.get('href')
        check = urllib.parse.urlparse(potential_link)
        if check.scheme is '' or check.netloc is '':
            potential_link = initial_page + potential_link
        url_queue[potential_link] = potential_link
    url_cache[initial_page]=soup.prettify()

    while url_cache.__len__() <= 200:
        listOfQueues = []
        threads = []
        for item in url_queue:
            t = Thread(target=crawl_thread, args=(item, listOfQueues, url_cache))
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()
        url_queue = {}
        for next in listOfQueues:
            if next[0] not in url_cache.keys() and next[0] not in url_queue.keys():
                url_queue[next[0]]=next[0]
    pickle.dump(url_cache, open("crawl/result", "wb"))

def crawl_thread(url, listOfQueues, url_cache):
    crawled_links = {}
    try:
        page = urllib.request.urlopen(url, timeout=0.1)
        s = bs(page, 'lxml')

        for link in s.find_all('a'):
            potential_link = link.get('href')
            check = urllib.parse.urlparse(potential_link)
            if check.scheme is '' or check.netloc is '':
                potential_link = url + potential_link
            if potential_link not in crawled_links.keys():
                crawled_links[potential_link] = potential_link
                #print(url)

        url_cache[url] =  s.prettify()
    except Exception as inst:
        print(inst)
        url_cache[url] = None
    listOfQueues.extend(list(crawled_links.items()))
    print(url_cache.__len__())



def save_crawl_as_html():
    db = pickle.load( open( "crawl/result", "rb" ) )
    default_path = "crawl/websites/"
    for item in db:
        path = default_path+str(hash(item))+".html"
        file = codecs.open(path, 'w', 'utf-8')
        if db[item] is not None:
            file.write(db[item])
        file.close()

def save_crawl_urls():
    db = pickle.load(open("crawl/result", "rb"))
    default_path = "crawl/"
    path = default_path + "visited_sites.txt"
    urls = ""
    counter = 0
    for item in db:
        counter += 1
        if db[item] is not None:
            urls += str(counter) + ". Url=" + item + "\n"
        else:
            urls += str(counter) + ". Does not exist/html/php-error!\n"
    file = codecs.open(path, 'w', 'utf-8')
    file.write(urls)
    file.close()

start_crawl("http://www.spiegel.de")
#save_crawl_as_html()
save_crawl_urls()