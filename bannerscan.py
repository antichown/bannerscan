#coding=utf-8

import threading
import requests
import argparse
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


PORTS = (80,443)
PATHS = ('/robots.txt',
         '/admin/',
         '/console/',
         '/uddiexplorer/',
         '/manager/html/',
         '/jmx-console/',
         '/web-console/',
         '/jonasAdmin/',
         '/manager/',
         '/install/',
         '/ibm/console/logon.jsp',
         '/axis2/axis2-admin/',
         '/CFIDE/administrator/index.cfm',
         '/FCKeditor/',
         '/fckeditor/',
         '/fck/',
         '/FCK/',
         '/HFM/',
         '/WEB-INF/',
         '/fckeditor/',
         '/phpMyAdmin/',
         '/Struts2/index.action',
         '/index.action',
         '/phpinfo.php',
         '/info.php',
         '/1.php',
         '/CHANGELOG.txt',
         '/LICENSE.txt',
         '/readme.html',
         '/cgi-bin/',
         '/invoker/',
         '/.svn/',
         '/test/',
         '/CFIDE/',
         '/.htaccess',
         '/.git/'
)

HTML_LOG_TEMPLATE="""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Bannerscan Report</title>
<style type="text/css">
%s
</style>
</head>
<body>
<center><h2>%s</h2></center>
<div class="report-content">
%s
</div>
</body>
</html>
"""
css = """
body{background-color:#FFF;color:#444;font-family:"Droid Serif",Georgia,"Times New Roman",STHeiti,serif;font-size:100%;}
a{color:#3354AA;text-decoration:none;}
a:hover,a:active{color:#444;}
pre,code{background:#F3F3F0;font-family:Menlo,Monaco,Consolas,"Lucida Console","Courier New",monospace;font-size:.92857em;padding:2px 4px;}
code{color:#B94A48;}
pre{overflow:auto;max-height:400px;padding:8px;}
pre code{color:#444;padding:0;}
h1,h2,h3{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;}
textarea{resize:vertical;}.report-meta a,.report-content a,.widget a,a{border-bottom:1px solid#EEE;}.report-meta a:hover,.report-content a:hover,.widget a:hover,a{border-bottom-color:transparent;}#header{padding-top:35px;border-bottom:1px solid#EEE;}#logo{color:#333;font-size:2.5em;}.description{color:#999;font-style:italic;margin:.5em 0 0;}.report{border-bottom:1px solid#EEE;padding:15px 0 20px;}.report-title{font-size:1.4em;margin:.83em 0;}.report-meta{margin-top:-.5em;color:#999;font-size:.92857em;padding:0;}.report-meta li{display:inline-block;padding-left:12px;border-left:1px solid#EEE;margin:0 8px 0 0;}.report-meta li:first-child{margin-left:0;padding-left:0;border:none;}.report-content{line-height:1.5;}.report-content hr,hr{margin:2em auto;width:100px;border:1px solid#E9E9E9;border-width:2px 0 0 0;}
"""


ua = "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6"

headers = dict()
result = dict()


class bannerscan(threading.Thread):
    def __init__(self, ip, timeout, headers):
        self.ip = ip
        self.req = requests
        self.timeout = timeout
        self.headers = headers
        self.per = 0
        threading.Thread.__init__(self)
        
        
    def screen_page(self,url):
        try:
            
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=800x600')
            driver = webdriver.Chrome(executable_path='chromedriver.exe',chrome_options=options)
            driver.get("http://"+url) ##updated as a random test URL
            driver.set_page_load_timeout(5)            
            driver.save_screenshot('img/{}.png'.format(str(url).replace('https://','').replace('http://','')))
            driver.quit
            
            
        except:
            pass
    def run(self):
        result[self.ip] = dict()
        for port in PORTS:
            url_pre = "https://" if port == 443 else "http://"
            site = url_pre + self.ip + ":" + str(port)
            try:
                print ("[*] %s\r" % (site[0:60].ljust(60, " "))),
                resp = requests.head(site,
                                     allow_redirects = False,
                                     timeout=self.timeout,
                                     headers=self.headers
                )
                result[self.ip][port] = dict()
                self.screen_page(self.ip)
            except Exception, e:
                pass

            else:
                result[self.ip][port]["headers"] = resp.headers
                result[self.ip][port]["available"] = list()

                for path in PATHS:
                    try:
                        url = site + path
                        print ("[*] %s\r" % (url[0:60].ljust(60, " "))),
                        resp = self.req.get(url,
                                            allow_redirects = False,
                                            timeout=self.timeout,
                                            headers=self.headers
                        )

                    except Exception, e:
                        pass
                    else:
                        if resp.status_code in [200, 406, 401, 403, 500]:
                            r = re.findall("<title>([\s\S]+?)</title>", resp.content)
                            title = lambda r : r and r[0] or ""
                            result[self.ip][port]["available"].append((title(r), url, resp.status_code))
        

    

def getiplst(host, start=1, end=255):
    iplst = []
    ip_pre = ""
    for pre in host.split('.')[0:3]:
        ip_pre = ip_pre + pre + '.'
    for i in range(start, end):
        iplst.append(ip_pre + str(i))
    return iplst

def retiplst(ip):
    iplst = []
    if ip:
        print "[*] job: %s \r" % ip
        iplst = getiplst(ip)
        return iplst


def retiprangelst(ip):
    ip_list = []
    iptonum = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
    numtoip = lambda x: '.'.join([str(x/(256**i)%256) for i in range(3,-1,-1)])
    if '-' in ip:
        ip_range = ip.split('-')
        ip_start = long(iptonum(ip_range[0]))
        ip_end = long(iptonum(ip_range[1]))
        ip_count = ip_end - ip_start

        for ip_num in range(ip_start,ip_end+1):
            ip_list.append(numtoip(ip_num))
    return ip_list

def ip2int(s):
    l = [int(i) for i in s.split('.')]
    return (l[0] << 24) | (l[1] << 16) | (l[2] << 8) | l[3]

def log(out, path):
    logcnt = ""
    centerhtml = lambda ips: len(ips)>1  and str(ips[0]) + "  -  " + str(ips[-1]) or str(ips[0])
    titlehtml = lambda x : x and "<strong>" + str(x) + "</strong><br />" or ""
    ips = out.keys()
    ips.sort(lambda x, y: cmp(ip2int(x), ip2int(y)))
    for ip in ips:
        titled = False
        if type(out[ip]) == type(dict()):
            for port in out[ip].keys():
                if not titled:
                    if len(out[ip][port]['headers']):
                        logcnt += "<center><h2><a href=http://%s>%s</a><img src=img/%s.png></h2></center>" % (ip,ip,ip)
                        logcnt += "<hr />"
                        titled = True
                logcnt += "PORT: %s <br />" % port
                logcnt += "Response Headers:<pre>"
                for key in out[ip][port]["headers"].keys():
                    logcnt += key + ":" + out[ip][port]["headers"][key] + "\n"
                logcnt += "</pre>"
                for title, url, status_code in out[ip][port]["available"]:
                    logcnt += titlehtml(title) + \
                             "<a href=\"" + url + "\">" + url + " </a> "+ \
                             "Status Code:<code>" + str(status_code) + "</code><br />"
                logcnt += "<br />"
    center = centerhtml(ips)
    logcnt = HTML_LOG_TEMPLATE % ( css, center, logcnt)
    outfile = open(path, "a")
    outfile.write(logcnt)
    outfile.close()

def scan(iplst, timeout, headers, savepath):
    global result
    start = time.time()
    threads = []

    for ip in iplst:
        t = bannerscan(ip,timeout,headers)
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    log(result, savepath)
    result = dict()
    print

def main():
    parser = argparse.ArgumentParser(description='banner scanner')
    group = parser.add_mutually_exclusive_group()

    
    group.add_argument('-r',
                        action="store",
                        dest="iprange",
                        type=str,
    )
    parser.add_argument('-s',
                        action="store",
                        required=True,
                        dest="savepath",
                        type=str,
    )
    parser.add_argument('-t',
                        action="store",
                        required=False,
                        type = int,
                        dest="timeout",
                        default=5
    )

    args = parser.parse_args()
    savepath = args.savepath
    timeout = args.timeout
    iprange = args.iprange

    headers['user-agent'] = ua

    print "[*] starting at %s" % time.ctime()


    if iprange:
        iplst = retiprangelst(iprange)
        scan(iplst, timeout, headers, savepath)

    else:
        parser.print_help()
        exit()

if __name__ == '__main__':
    main()
