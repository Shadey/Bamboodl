import time,os,json,socket,concurrent.futures,sys
from urllib.error import *
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen
def chandl(link,host,base=None):
    special = ["b","sp","v","pol"]
    board = urlparse(link).path.split("/")[1]
    link = link.split("#")[0].replace("html","json").strip()
    if "json" not in link: link += ".json"
    if host == "boards.4chan.org":
        base = "http://i.4cdn.org/{}/".format(board)
    elif board in special:
        base = "http://`8ch.net/{}/src/".format(board)
    elif host == "lainchan.org":
        base = "http://lainchan.org/{}/src/".format(board)
    else:
        base = "https://media.8ch.net/{}/src/".format(board)
    try:
        jsondata = json.loads(urlopen(Request(link, headers={'User-Agent': "Mozilla 5.0"}),timeout=30).read().decode("UTF-8"))
        for post in jsondata["posts"]:
            if "tim" in post:
                filename = "{}{}".format(post["tim"],post["ext"])
                src = "{}{}".format(base,filename)
                folder = "{}/{}-{}".format(host,board,jsondata["posts"][0]["no"])
                os.makedirs(folder,exist_ok=True)
                dlfile(src,"{}/{}".format(folder,filename))
            if "extra_files" in post:
                for epost in post["extra_files"]:                       
                    filename = "{}{}".format(epost["tim"],epost["ext"])
                    src = "{}{}".format(base,filename)
                    folder = "{}/{}-{}".format(host,board,jsondata["posts"][0]["no"])
                    os.makedirs(folder,exist_ok=True)
                    dlfile(src,"{}/{}".format(folder,filename))
        print("All done")
    except(ValueError,KeyError,TypeError) as err:
        print("Parsing Error:",err)
    except socket.timeout:
        print("Thread timed out")
    except (HTTPError,URLError) as err:
        print("Thread 404ed")
        deadlinks.append(link)
def watch(f):
    starttime = time.time()
    f.seek(0,2)
    while True:
        lines = f.readlines()
        if not lines:
            if int((time.time()- starttime)) >= 500:
                starttime = time.time()
                time.sleep(0.1)
                main()
        yield [line for line in lines if check(line)]
def check(url):
    parsed = urlparse(url)
    if (parsed.scheme == "https" or parsed.scheme == "http") and parsed.netloc in hosts and parsed.path != "":
        if not url in deadlinks:return True
    print("Not valid",url)
    return False
def dlfile(src,filename):
    try:
        if os.path.isfile(filename): return
        with urlopen(Request(src,headers={"User-Agent": "Mozilla 5.0"}),timeout=300) as resp ,open(filename,"wb") as f:
            print("Downloading",src)
            f.write(resp.read())
            print("Finished",src)
    except (IOError,OSError) as error:
        print("File Error:",error)
    except socket.timeout:
        print("File",src,"timed out")
        
def download(lines):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for line in lines:
            for host,func in hosts.items():
                if host == urlparse(line).netloc:
                    print("Starting on",line)
                    pool.submit(func,line,host)
def main():
    for host in hosts: os.makedirs(host,exist_ok=True)
    f = open("new.txt","w+")
    download([line for line in f.readlines() if check(line)])
    for lines in watch(f):
        download(lines)
    
if __name__ == '__main__':
    hosts ={"boards.4chan.org":chandl,
            "8ch.net":chandl,
            "lainchan.org":chandl
    }
    deadlinks = []
    try:
        print("Waiting for changes to new.txt")
        main()
    except KeyboardInterrupt:
        f  = open("new.txt")
        newlines = [line for line in f.readlines() if check(line)]
        os.remove("new.txt")
        new = open("new.txt","w+")
        for line in newlines:print(line,file=new)
        print("Closing")
