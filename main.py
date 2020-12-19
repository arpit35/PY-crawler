from bs4 import BeautifulSoup
import requests
import MySQLdb as sql
import time
import warnings

print("starting")

warnings.filterwarnings('ignore')

db = sql.connect("localhost", "root", "arpit", "website")
cursor = db.cursor()
db.autocommit(True)

print("connected to database")

url = "http://www.example.com"
extension = ".com"
print("scrapping url -",url)

r = requests.head(url)
cursor.execute("insert ignore into urls(urls,status,status_code)     
values(%s,'pending',%s)", [url, r.status_code])

cursor.execute("select status from urls where status ='pending' limit 1")
result = str(cursor.fetchone())

while (result != "None"):

cursor.execute("select urls from urls where status ='pending' limit 1")
result = str(cursor.fetchone())

s_url = result[2:-3]

cursor.execute("update urls set status = 'done' where urls= %s ", [s_url])

if "https" in url:
    url1 = url[12:]
else:
    url1 = url[11:]
zone = 0
while True:

    try:
        r = requests.get(s_url,timeout=60)
        break

    except:
        if s_url == "":

            print("done")
            break
        elif zone >= 4:
            print("this url is not valid -",s_url)
            break
        else:
            print("Oops!  may be connection was refused.  Try again...",s_url)
            time.sleep(0.2)
            zone = zone + 1

soup = BeautifulSoup(r.content.lower(), 'lxml')

links = soup.find_all("a")

for x in links:
    a = x.get('href')
    if a is not None and a != "":

        if a != "" and a.find("\n") != -1:
            a = a[0:a.find("\n")]

        if a != "" and a[-1] == "/":
            a = a[0:-1]

        if a != "":
            common_extension = [',',' ',"#",'"','.mp3',"jpg",'.wav','.wma','.7z','.deb','.pkg','.rar','.rpm','.tar','.zip','.bin','.dmg','.iso','.toast','.vcd','.csv','.dat','.log','.mdb','.sav','.sql','.apk','.bat','.exe','.jar','.py','.wsf','.fon','.ttf','.bmp','.gif','.ico','.jpeg','.png','.part','.ppt','.pptx','.class','.cpp','.java','.swift','.ods','.xlr','.xls','.xlsx','.bak','.cab','.cfg','.cpl','.dll','.dmp','.icns','.ini','.lnk','.msi','.sys','.tmp','.3g2','.3gp','.avi','.flv','.h264','.m4v','.mkv','.mov','.mp4','.mpg','.vob','.wmv','.doc','.pdf','.txt']
            for ext in common_extension:
                if ext in a:
                    a = ""
                    break

        if a != "":
            if a[0:5] == '/http':
                a = a[1:]
            if a[0:6] == '//http':
                a = a[2:]

            if a[0:len(url1) + 12] == "https://www." + url1:
                cursor.execute("insert ignore into urls(urls,status,status_code) values(%s,'pending',%s)",
                               [a, r.status_code])
            elif a[0:len(url1) + 11] == "http://www." + url1:
                cursor.execute("insert ignore into urls(urls,status,status_code) values(%s,'pending',%s)",
                               [a, r.status_code])
            elif a[0:len(url1) + 8] == "https://" + url1:
                cursor.execute("insert ignore into urls(urls,status,status_code) values(%s,'pending',%s)",
                               [url + (a[(a.find(extension + "/")) + 4:]), r.status_code])
            elif a[0:len(url1) + 7] == "http://" + url1:
                cursor.execute("insert ignore into urls(urls,status,status_code) values(%s,'pending',%s)",
                               [url + (a[(a.find(extension + "/")) + 4:]), r.status_code])
            elif a[0:2] == "//" and a[0:3] != "///" and "." not in a and "http" not in a and "www." not in a:
                cursor.execute("insert ignore into urls(urls,status,status_code) values(%s,'pending',%s)",
                               [url + a[1:], r.status_code])
            elif a[0:1] == "/" and a[0:2] != "//" and "." not in a and "http" not in a and "www." not in a:
                cursor.execute("insert ignore into urls(urls,status,status_code) values(%s,'pending',%s)",
                               [url + a[0:], r.status_code])
            elif 'http' not in a and 'www.' not in a and "." not in a and a[0] != "/":
                cursor.execute("insert ignore into urls(urls,status,status_code) values(%s,'pending',%s)",
                               [url + '/' + a, r.status_code])

cursor.execute("alter table urls drop id")
cursor.execute("alter table urls add id int primary key not null  
auto_increment first")
print("new id is created")
