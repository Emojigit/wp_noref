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

def AllRedir(names):
    for a in names:
        RE = mw.redirects(S,a)
        if RE[0] == False:
            continue
        RLST = RLST + RE[2]
        RLST = RLST + [a]
    return RLST

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

def ListRMIndex(lst,prefix):
    RLST = []
    for a in lst:
        RLST = RLST + [remove_prefix(a, prefix)]
    return RLST

def TemplateNames(title):
    ared = AllRedir(mw.prefixsearch(S,title))
    rmpfix = ListRMIndex(ared,"Template:")
    # found(cont,rmpfix)
    return rmpfix


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

tps = {
    "ones": TemplateNames("Template:Onesource"),
    "nfoot": TemplateNames("Template:No footnotes"),
    "mfoot": TemplateNames("Template:More footnotes needed"),
    "noref": TemplateNames("Template:Unreferenced"),
}

def OneSources(hostnamelist,cont):
    a = dict(Counter(hostnamelist))
    print(len(a))
    if found(cont,tps["ones"]):
        return ""
    elif len(a) == "1":
        return "{{subst:Onesource/auto}}\n"
    else:
        return ""

def FootNotes(reflist,cont):
    refs = reflist[0]
    reftags = reflist[1]
    if found(cont,tps["nfoot"] + tps["mfoot"]):
        return ""
    elif reftags == 0:
        return "{{subst:No footnotes/auto}}"
    elif reftags <= (len(refs)/2):
        return "{{subst:More footnotes needed/auto}}"
    else:
        return ""

def Unref(reflist,cont):
    refs = reflist[0]
    if found(cont,tps["noref"]):
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
    delay = 0
    try:
        delay = int(fileget("delay.txt"))
        if delay == 0:
            raise FileNotFoundError
    except FileNotFoundError:
        log.warning("delay.txt not found! using 5 seconds as the delay.")
        delay = 5
    except ValueError:
        log.error("Invalid int in delay.txt!")
        exit(3)
    finally:
        log.info("got delay.txt with " + str(delay) + " seconds delay")
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
                time.sleep(delay)
                continue
            except KeyboardInterrupt:
                log.info("Ctrl-C pressed, exiting")
                exit(0)
        except KeyboardInterrupt:
            log.info("Ctrl-C pressed, exiting")
            exit(0)

if __name__ == '__main__':
    main()
