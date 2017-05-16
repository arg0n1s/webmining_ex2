import urllib.request
import urllib.parse
from bs4 import BeautifulSoup as bs
import pickle
import codecs
from threading import Thread
import ssl
import difflib

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def start_crawl(initial_page, limit=100):

    start = urllib.request.urlopen(initial_page, timeout=0.1, context=ctx)
    soup = bs(start, 'lxml')

    url_queue = {}
    url_cache = {}
    url_out = {}

    for link in soup.find_all('a'):
        potential_link = link.get('href')
        check = urllib.parse.urlparse(potential_link)
        if check.scheme is '' or check.netloc is '':
            potential_link = initial_page + potential_link
        url_queue[potential_link] = potential_link
    url_cache[initial_page]=soup
    url_out[initial_page] = soup

    while url_out.__len__() < limit:
        listOfQueues = []
        threads = []
        for item in url_queue:
            if url_out.__len__() >= limit:
                break;
            t = Thread(target=crawl_thread, args=(item, listOfQueues, url_cache, url_out, limit))
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()
        url_queue = {}
        for next in listOfQueues:
            if next[0] not in url_cache.keys() and next[0] not in url_queue.keys():
                url_queue[next[0]]=next[0]

    '''
    url_out = {}
    url_cache = list(url_cache.items())
    while url_cache.__len__() > 0:
        page = url_cache.pop(0)
        isNew = True
        if page[1] is None:
            continue
        str1 = page[1].prettify()
        for item in url_cache:
            if item[1] is None:
                continue
            str2 = item[1].prettify()
            diff = difflib.SequenceMatcher(lambda x: x == " ", str1, str2)
            if round(diff.ratio(), 3) > 0.6:
                print(diff.ratio(), 3)
                isNew = False
                break
        if isNew:
            url_out[page[0]]=page[0]
    '''
    #pickle.dump(url_cache, open("crawl/result", "wb"))
    return url_out

def crawl_thread(url, listOfQueues, url_cache, url_out, limit):
    crawled_links = {}
    if url_out.__len__() >= limit:
        return
    try:
        page = urllib.request.urlopen(url, timeout=0.1, context=ctx)
        s = bs(page, 'lxml')
        for link in s.find_all('a'):
            potential_link = link.get('href')
            check = urllib.parse.urlparse(potential_link)
            if check.scheme is '' or check.netloc is '':
                potential_link = url + potential_link
            if potential_link not in crawled_links.keys():
                crawled_links[potential_link] = potential_link
                #print(potential_link)

        url_cache[url] =  s
        if type(s) is bs:
            url_out[url] = s
    except Exception as inst:
        #print(inst)
        url_cache[url] = None
    listOfQueues.extend(list(crawled_links.items()))
    print("Visited url: ", url, " Num:", url_out.__len__()," Visited: ", url_cache.__len__())

def save_crawl_as_html(db):
    #db = pickle.load( open( "crawl/result", "rb" ) )
    default_path = "crawl/websites/"
    for item in db:
        path = default_path+str(hash(item))+".html"
        if type(db[item]) is bs:
            file = codecs.open(path, 'w', 'utf-8')
            file.write(db[item].prettify(formatter="html"))
            file.close()

def save_crawl_urls(db):
    #db = pickle.load(open("crawl/result", "rb"))
    default_path = "crawl/"
    path = default_path + "visited_sites.txt"
    urls = ""
    counter = 0
    for item in db:
        counter += 1
        if db[item] is not None and db[item] is not type(None):
            urls += str(counter) + ". Url=" + str(item) + "\n"
        else:
            urls += str(counter) + ". Does not exist/html/php-error!\n"
    file = codecs.open(path, 'w', 'utf-8')
    file.write(urls)
    file.close()

db = start_crawl("http://www.wikipedia.de", 1000)
save_crawl_as_html(db)
save_crawl_urls(db)