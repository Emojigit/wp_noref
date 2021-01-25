from modules import mediawiki as mw
import xml.etree.ElementTree as ET
from mwtemplates import TemplateEditor
from urllib.parse import urlparse
from collections import Counter
import sys, re, requests
exit = sys.exit

S = requests.Session()

def GetRefList(content):
    reflist = []
    reftaglist = re.findall(r'<ref>(.+?)</ref>', content)
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
    for v in reflist:
        url = refURL(v)
        if url == False:
            continue
        urlist = urlist + [url]
    hostnames = []
    for z in urlist:
        puri = urlparse(z)
        hostnames = hostnames + [puri.netloc]
    return hostnames

def OneSources(hostnamelist):
    a = dict(Counter(hostnamelist))
    print(len(a))
    if len(a) == "1":
        return "{{subst:Onesource/auto}}\n"
    else:
        return ""

def FootNotes(reflist):
    refs = reflist[0]
    reftags = reflist[1]
    if reftags == 0:
        return "{{subst:No footnotes/auto}}"
    elif reftags <= (len(refs)/2):
        return "{{subst:More footnotes needed/auto}}"
    else:
        return ""

def Unref(reflist):
    refs = reflist[0]
    if len(refs) == 0:
        return "{{subst:Unreferenced/auto}}"
    else:
        return ""

# Main Part
def PageHandler(name):
