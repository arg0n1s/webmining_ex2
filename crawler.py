import urllib.request
import urllib.parse
from bs4 import BeautifulSoup as bs
import pickle
import codecs
from threading import Thread
import ssl
import random
import time

def start_crawl(initial_page, limit=300, numOfThreads=500):

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    queue = []
    url_cache = {}
    url_out = {}

    queue.append(initial_page)

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
        page = urllib.request.urlopen(url, timeout=0.5, context=cert)

        s = bs(page, 'lxml')
        for link in s.find_all('a'):
            potential_link = link.get('href')
            check = urllib.parse.urlparse(potential_link)
            if check.scheme is '' or check.netloc is '':
                potential_link = url + potential_link
            if potential_link not in crawled_links.keys() and potential_link not in url_cache.keys() and queue.__len__()<10000:
                crawled_links[potential_link] = potential_link
                #print(potential_link)

        url_cache[url] =  s
        if type(s) is bs:
            url_out[url] = s
    except Exception as inst:
        #print(inst)
        url_cache[url] = None
    queue.extend(list(crawled_links.keys()))
    #print("Visited url: ", url, " Num:", url_out.__len__()," Visited: ", url_cache.__len__())

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

db = start_crawl("http://www.spiegel.de", 400, 250)
#save_crawl_as_html(db)
save_crawl_urls(db)