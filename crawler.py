import urllib.request
import urllib.parse
from bs4 import BeautifulSoup as bs
import pickle
import codecs

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

    while url_cache.__len__() <= 10:
        new_queue = {}
        for item in url_queue:
            try:
                page = urllib.request.urlopen(item, timeout=0.5)
                s = bs(page, 'lxml')

                for link in s.find_all('a'):
                    potential_link = link.get('href')
                    check = urllib.parse.urlparse(potential_link)
                    if check.scheme is '' or check.netloc is '':
                        potential_link = item + potential_link
                    if potential_link not in url_queue.keys() and potential_link not in new_queue.keys():
                        new_queue[potential_link] = potential_link
                print(item)
                url_cache[item]=s.prettify()
                if url_cache.__len__() > 10:
                    break;
            except Exception as inst:
                print(inst)
        url_queue = new_queue
    print(url_cache.__len__())
    pickle.dump(url_cache, open("crawl/result", "wb"))

def save_crawl_as_html():
    db = pickle.load( open( "crawl/result", "rb" ) )
    default_path = "crawl/websites/"
    for item in db:
        path = default_path+str(hash(item))+".html"
        file = codecs.open(path, 'w', 'utf-8')
        file.write(db[item])
        file.close()
#start_crawl("http://www.spiegel.de")
#save_crawl_as_html()
