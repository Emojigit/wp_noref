ilist = {
    "ones":"{{subst:Onesource/auto}}",
    "inline":"{{subst:No footnotes/auto}}",
    "moreiline":"{{subst:More footnotes needed/auto}}",
    "noref":"{{subst:Unreferenced/auto}}",
}

def wtget(wtlist):
    RSTR = ""
    for x in wtlist:
        try:
            RSTR = RSTR + ilist[x]
        except KeyError:
            continue
    return RSTR
