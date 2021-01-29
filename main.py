#!/usr/bin/python
# -*- coding: UTF-8 -*-
from modules import mediawiki as mw
import xml.etree.ElementTree as ET
from mwtemplates import TemplateEditor
from urllib.parse import urlparse
from collections import Counter
import sys, re, requests, logging, time
exit = sys.exit

S = requests.Session()
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s[%(name)s] %(message)s")
log = logging.getLogger("MainScript")

def totable(*args):
    return args

def found(text,l):
    for x in l:
        if x in text:
            return True
    return False

def GetRefList(content):
    reflist = []
    reftaglist = re.findall(r'<ref>(.+?)</ref>', content)
    reftaglist = reftaglist + re.findall(r'<ref name.+?>(.+?)</ref>', content)
    reflist = reflist + reftaglist
    reflist = reflist + re.findall(r'\{\{Cite.+?}}',content)
    reflist = reflist + re.findall(r'\{\{FishBase_species.+?}}',content) # FishBase_species
    reflist = reflist + re.findall(r'\{\{fishBase_species.+?}}',content)
    return [list(dict.fromkeys(reflist)),len(list(dict.fromkeys(reftaglist)))]

def refURL(text):
    if "{{" not in text:
        return False
    te = TemplateEditor(text)
    tps = te.templates
    tp = tps[tps.keys()[0]][0]
    try:
        return str(tp.parameters['url'])
    except KeyError:
        return False

def GetHostNameList(reflist):
    urlist = []
    for v in reflist[0]:
        url = refURL(v)
        if url == False:
            continue
        urlist = urlist + [url]
    hostnames = []
    for z in urlist:
        puri = urlparse(z)
        hostnames = hostnames + [puri.netloc]
    return hostnames

def OneSources(hostnamelist,cont):
    a = dict(Counter(hostnamelist))
    print(len(a))
    if found(cont,totable("單一來源".upper(),"One source".upper(),"单一来源".upper(),"Onesource".upper())):
        return ""
    elif len(a) == "1":
        return "{{subst:Onesource/auto}}\n"
    else:
        return ""

def FootNotes(reflist,cont):
    refs = reflist[0]
    reftags = reflist[1]
    if found(cont,totable("Nofootnotes".upper(),"缺乏注脚".upper(),"缺乏脚注".upper(),"缺少脚注".upper(),"Inline".upper(),"沒有註腳".upper(),"沒有腳註".upper(),"更多引註".upper(),"No footnotes".upper(),"More footnotes".upper())):
        return ""
    elif reftags == 0:
        return "{{subst:No footnotes/auto}}"
    elif reftags <= (len(refs)/2):
        return "{{subst:More footnotes needed/auto}}"
    else:
        return ""

def Unref(reflist,cont):
    refs = reflist[0]
    if found(cont,totable("Unsourced".upper(),"缺少來源的條目".upper(),"Unref".upper(),"Unreference".upper(),"缺乏來源".upper(),"Reference".upper(),"Noreference".upper(),"Noreferences".upper(),"来源".upper(),"沒有來源".upper(),"無來源".upper(),"沒來源".upper(),"缺來源".upper(),"缺少來源".upper(),"Noref".upper(),"No reference".upper(),"No references".upper(),"需要來源".upper())):
        return ""
    elif len(refs) == 0:
        return "{{subst:Unreferenced/auto}}"
    else:
        return ""

# Main Part
def TemplateHandler(reflist,cont):
    ASTR = ""
    HLIST = GetHostNameList(reflist)
    ASTR = ASTR + OneSources(HLIST,cont)
    ASTR = ASTR + FootNotes(reflist,cont)
    ASTR = ASTR + Unref(reflist,cont)
    return ASTR

def PageHandler(title):
    tdata = mw.token(S,"csrf")
    starttimestamp = tdata[1]
    token = tdata[0]
    PAGE = mw.getpage(S,title)
    CONT = PAGE[0]
    TS = PAGE[1]
    if CONT == "":
        log.warning("Page " + title + "Have no content or not exist!")
        return False
    reflist = GetRefList(CONT)
    Templates = TemplateHandler(reflist,CONT.upper())
    if Templates == "":
        log.info("Page " + title + " have no templates. Skipping.")
        return False
    else:
        log.info("Editing " + title)
    EDIT = mw.prependedit(S,token,title,Templates,"Bot add templates",True,TS,starttimestamp,False,True)
    if EDIT[0] == False:
        log.error("error while editing " + title + ": " + EDIT[1])
        log.error(EDIT[2])
        return False
    return True

class CustomError(Exception):
     pass


def fileget(fname):
    try:
        with open(fname,"r") as f:
            return f.read().rstrip('\n')
    except FileNotFoundError:
        log.error("No " + fname)
        return False

def main():
    # mw.setdebug(True)
    uname = fileget("uname.txt")
    passwd = fileget("passwd.txt")
    root = fileget("root.txt")
    if uname == False or passwd == False or root == False:
        exit(3)
    mw.chroot(root)
    token = mw.token(S,"login")[0]
    status = mw.login(S,token,uname,passwd)
    del passwd
    if status[0] == True:
        log.info("Logged in!")
    else:
        log.error("Login Failed.")
        exit(2)
    try:
        if sys.argv[1] != None:
            title = sys.argv[1]
            log.info("Processing " + title)
            PageHandler(title)
            exit(0)
    except IndexError:
        pass
    while True:
        try:
            RAN = mw.random(S,0)
            if RAN[0] == False:
                log.error("Error while getting random pages: " + RAN[1])
                log.error(RAN[2])
                raise CustomError
            title = RAN[2]
            log.info("Processing " + title)
            PageHandler(title)
            log.info("Finished process of " + title)
            raise CustomError
        except CustomError:
            try:
                time.sleep(5)
                continue
            except KeyboardInterrupt:
                log.info("Ctrl-C pressed, exiting")
                exit(0)
        except KeyboardInterrupt:
            log.info("Ctrl-C pressed, exiting")
            exit(0)

if __name__ == '__main__':
    main()
