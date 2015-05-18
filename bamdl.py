import time,os,json,socket
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen
def chandl(link,host):
    base = ""
    special = ["b","sp","v","pol"]
    board = urlparse(link).path.split("/")[1]
    link = link.split("#")[0].replace("html","json").strip()
    if "json" not in link: link += ".json"
    if host == "4chan.org":
        base = "http://i4cdn.org/{}/".format(board)
    elif board in special:
        base = "http://`8ch.net/{}/src/".format(board)
    else:
        base = "https://media.8ch.net/{}/src/".format(board)
    try:
        jsondata = json.loads(urlopen(Request(link, headers={'User-Agent': "Mozilla 5.0"}),timeout=30).read().decode("UTF-8"))
        print(jsondata["posts"])
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
        print("Json timed out")
    except Exception as et:
        print("Something strange happened ",et)
        
    
def watch(f):
    f.seek(0,2)
    while True:
        lines = f.readlines()
        if not lines:
            time.sleep(0.1)
            continue
        for line in lines: yield line
def check(url):
    parsed = urlparse(url)
    if (parsed.scheme == "https" or parsed.scheme == "http") and parsed.netloc in hosts and parsed.path != "":
        return True
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
    except Exception as err:
        print("Something strange some happened",error)
        
def download(link):
    thread = urlparse(link)
    for host,func in hosts.items():
        if host == thread.netloc:
            func(link,host)
def main():
    for host in hosts: os.makedirs(host,exist_ok=True)
    f = open("chicken.txt")
    for line in watch(f):
        print(line)
        download(line) if check(line) else print("Not valid")

hosts ={"4chan.org":chandl,"8ch.net":chandl} 
main()