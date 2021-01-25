import requests
URL = ["https://zh.wikipedia.org/w/api.php"]
def chroot(root):
    URL[0] = root
DEBUG = [False]
def setdebug(status=None):
    if status != None:
        DEBUG[0] = status
    return DEBUG

def debugctl(DATA):
    if DEBUG[0] == True:
        print("[DEBUG] printing request result:")
        print(DATA)
        print("------")

def token(S,ttype):
    PARAMS_0 = {
        'action':"query",
        'meta':"tokens",
        'type':ttype,
        'format':"json",
        'curtimestamp':True,
    }
    R = S.get(url=URL[0], params=PARAMS_0)
    DATA = R.json()
    debugctl(DATA)
    LOGIN_TOKEN = DATA['query']['tokens'][ttype+'token']
    return [LOGIN_TOKEN,DATA["curtimestamp"]]

def login(S,token,uname,passwd): # require "login" type token
    PARAMS_1 = {
        'action':"login",
        'lgname':uname,
        'lgpassword':passwd,
        'lgtoken':token,
        'format':"json"
    }
    R = S.post(URL[0], data=PARAMS_1)
    DATA = R.json()
    debugctl(DATA)
    status = DATA["login"]["result"]
    if status == "Success":
        return [True,DATA["login"]["lgusername"]]
    else:
        return [False,status]

def getpage(S,title): # no token required
    PARAMS = {
        "action":"query",
        "prop":"revisions",
        "titles":title,
        "rvslots":"*",
        "rvprop":"content|timestamp",
        "formatversion":"2",
        'format':"json"
    }
    R = S.get(URL[0], params=PARAMS)
    DATA = R.json()
    debugctl(DATA)
    TS = "1970-01-01T00:00:01+00:00"
    try:
        TS = DATA["query"]["pages"][0]["revisions"][0]["timestamp"]
    except KeyError:
        pass
    try:
        try:
            tmp = DATA["query"]["pages"][0]["missing"]
            return ["",TS]
        except KeyError:
            tmp = DATA["query"]["pages"]["-1"]["missing"]
            return ["",TS]
    except TypeError:
        return [DATA["query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"],TS]


def edit(S,token,title,content,summary,bot,basetimestamp,starttimestamp,minor=False): # csrf token required
    PARAMS_3 = {
        "action": "edit",
        "title": title,
        "token": token,
        "format": "json",
        "text": content,
        "summary":"Noref Bot : "+summary,
        "bot":bot,
        "headers":{'Content-Type': 'multipart/form-data'},
        "basetimestamp":basetimestamp,
        "starttimestamp":starttimestamp,
    }
    if minor == True:
        z = PARAMS_3.copy()
        z.update({"minor":True})
        PARAMS_3 = z
    R = S.post(URL[0], data=PARAMS_3)
    DATA = R.json()
    debugctl(DATA)
    try:
        if DATA["edit"]["result"] == "Success":
            return [True,"Success",""]
        else:
            raise KeyError
    except KeyError:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]

def whoami(S):
    PARAMS = {
        "action": "query",
        "format": "json",
        "meta": "userinfo",
    }
    R = S.get(URL[0], params=PARAMS)
    DATA = R.json()
    debugctl(DATA)
    return DATA["query"]["userinfo"]

def logout(S,token): #require csrf token
    PARAMS_3 = {
        "action": "logout",
        "token": token,
        "format": "json"
    }
    R = S.post(URL[0], data=PARAMS_3)
    DATA = R.json()
    debugctl(DATA)
    if DATA == {}:
        return [True,"Success",""]
    else:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]

def revisions(S,title):
    PARAMS = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvprop": "timestamp|user|comment|content|tags|ids",
        "rvslots": "main",
        "formatversion": "2",
        "format": "json",
        "rvlimit":500,
    }
    R = S.get(url=URL[0], params=PARAMS)
    DATA = R.json()
    debugctl(DATA)
    PAGES = DATA["query"]["pages"]
    try:
        tmp = PAGES[0]["missing"]
        return [False,PAGES]
    except KeyError:
        return [True,PAGES]

def rollback(S,token,title,username): #rollback token required
    PARAMS_6 = {
        "action": "rollback",
        "format": "json",
        "title": title,
        "user": username,
        "token": token,
    }
    R = S.post(URL[0], data=PARAMS_6)
    DATA = R.json()
    debugctl(DATA)
    try:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]
    except KeyError:
        return [True,"Success",""]

def undo(S,token,title,id,bot,minor=False,reason=""): # csrf token required
    PARAMS_3 = {
        "action": "edit",
        "title": title,
        "token": token,
        "format": "json",
        "undo": id,
        "summary":"Undo edit [[Special:PermanentLink/" + str(id) + "|" + str(id) + "]] via [[User:Emojiwiki/TextWikiPlus|TextWikiPlus]]: " + reason,
        "bot":bot,
        "headers":{'Content-Type': 'multipart/form-data'},
    }
    if minor == True:
        z = PARAMS_3.copy()
        z.update({"minor":True})
        PARAMS_3 = z
    R = S.post(URL[0], data=PARAMS_3)
    DATA = R.json()
    debugctl(DATA)
    try:
        if DATA["edit"]["result"] == "Success":
            return [True,"Success",""]
        else:
            raise KeyError
    except KeyError:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]

def random(S,ns):
    PARAMS = {
        "action":"query",
        "list":"random",
        "rnlimit":1,
        "utf8":"",
        "format":"json",
        "rnnamespace":ns,
    }
    R = S.get(url=URL[0], params=PARAMS)
    DATA = R.json()
    debugctl(DATA)
    try:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]
    except KeyError:
        return [True,"Success",DATA["query"]["random"][0]["title"]]
        # print(DATA["query"]["random"][0]["title"])

def nsinfo(S):
    PARAMS = {
        "action": "query",
        "meta": "siteinfo",
        "formatversion": "2",
        "format": "json",
        "siprop":"namespaces",
    }
    R = S.get(url=URL[0], params=PARAMS)
    DATA = R.json()
    debugctl(DATA)
    try:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]
    except KeyError:
        return [True,"Success",DATA["query"]["namespaces"]]

def wikiinfo(S):
    PARAMS = {
        "action": "query",
        "meta": "siteinfo",
        "formatversion": "2",
        "format": "json",
        "siprop":"general",
    }
    R = S.get(url=URL[0], params=PARAMS)
    DATA = R.json()
    debugctl(DATA)
    try:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]
    except KeyError:
        INFO = DATA["query"]["general"]
        return [True,"Success",INFO]

def exinfo(S):
    PARAMS = {
        "action": "query",
        "meta": "siteinfo",
        "formatversion": "2",
        "format": "json",
        "siprop":"extensions",
    }
    R = S.get(url=URL[0], params=PARAMS)
    DATA = R.json()
    debugctl(DATA)
    try:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]
    except KeyError:
        return DATA["query"]["extensions"]

def getimage(S,iname):
    PARAMS = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "titles": iname,
        "iiprop":"URL[0]",
    }
    R = S.get(url=URL[0], params=PARAMS)
    DATA = R.json()
    debugctl(DATA)
    PAGES = next(iter(DATA["query"]["pages"].values()))
    IURL[0] = ""
    try:
        IURL[0] = PAGES["imageinfo"][0]["URL[0]"]
    except:
        return [False,b""]
    return [True,S.get(IURL[0]).content]

def userinfo(S,uname):
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "users",
        "ususers": uname,
        "usprop": "blockinfo|cancreate|centralids|editcount|emailable|gender|groupmemberships|groups|implicitgroups|registration|rights",
        "utf8": "",
    }
    R = S.get(url=URL[0], params=PARAMS)
    DATA = R.json()
    debugctl(DATA)
    try:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]
    except KeyError:
        USER = DATA["query"]["users"][0]
        try:
            ERR = USER["invalid"]
            return [False,"invalid",""]
        except KeyError:
            try:
                ERR = USER["missing"]
                return [False,"missing",""]
            except KeyError:
                return [True,"Success",USER]

def emailuser(S,token,target,subj,text): # csrf token required
    PARAMS_3 = {
        "action": "emailuser",
        "target": target,
        "subject": subj,
        "text": text + "\n\nThis email was sent from https://zhwp.org/U:Emojiwiki/TextWikiPlus \nIf you found any bugs, please report them.",
        "token": token,
        "format": "json"
    }
    R = S.post(URL[0], data=PARAMS_3)
    DATA = R.json()
    debugctl(DATA)
    try:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]
    except KeyError:
        return [False,"Success",""]

def usercontribs(S,uname):
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "usercontribs",
        "ucuser": uname,
        "uclimit": 50
    }
    R = S.get(url=URL[0], params=PARAMS)
    DATA = R.json()
    try:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]
    except KeyError:
        return [True,DATA["query"]["usercontribs"]]

def prependedit(S,token,title,prependtext,summary,bot,basetimestamp,starttimestamp,minor=False,nocreate=False): # csrf token required
    PARAMS_3 = {
        "action": "edit",
        "title": title,
        "token": token,
        "format": "json",
        "prependtext": prependtext,
        "summary":"Noref Bot : "+summary,
        "bot":bot,
        "headers":{'Content-Type': 'multipart/form-data'},
        "basetimestamp":basetimestamp,
        "starttimestamp":starttimestamp,
    }
    if minor == True:
        z = PARAMS_3.copy()
        z.update({"minor":True})
        PARAMS_3 = z
    R = S.post(URL[0], data=PARAMS_3)
    DATA = R.json()
    debugctl(DATA)
    try:
        if DATA["edit"]["result"] == "Success":
            return [True,"Success",""]
        else:
            raise KeyError
    except KeyError:
        return [False,DATA["error"]["code"],DATA["error"]["info"]]
