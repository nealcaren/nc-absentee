import re, collections, datetime

MONTHS={m:i+1 for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'])}
TIME=r'(\d{1,2}):(\d{2})\s*([ap])\.m\.'
HOURS_RE=re.compile(r'^'+TIME+r'\s*-\s*'+TIME+r'$')
DATE_RE=re.compile(r'('+'|'.join(MONTHS)+r')\s+(\d{1,2})')
CITY_RE=re.compile(r',\s*NC\s+\d{5}')
STREET_RE=re.compile(r'^\d')
WEEKDAY=re.compile(r'^(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)')

COUNTIES=set("""ALAMANCE ALEXANDER ALLEGHANY ANSON ASHE AVERY BEAUFORT BERTIE BLADEN BRUNSWICK
BUNCOMBE BURKE CABARRUS CALDWELL CAMDEN CARTERET CASWELL CATAWBA CHATHAM CHEROKEE CHOWAN CLAY
CLEVELAND COLUMBUS CRAVEN CUMBERLAND CURRITUCK DARE DAVIDSON DAVIE DUPLIN DURHAM EDGECOMBE FORSYTH
FRANKLIN GASTON GATES GRAHAM GRANVILLE GREENE GUILFORD HALIFAX HARNETT HAYWOOD HENDERSON HERTFORD
HOKE HYDE IREDELL JACKSON JOHNSTON JONES LEE LENOIR LINCOLN MCDOWELL MACON MADISON MARTIN MECKLENBURG
MITCHELL MONTGOMERY MOORE NASH NEWHANOVER NORTHAMPTON ONSLOW ORANGE PAMLICO PASQUOTANK PENDER
PERQUIMANS PERSON PITT POLK RANDOLPH RICHMOND ROBESON ROCKINGHAM ROWAN RUTHERFORD SAMPSON SCOTLAND
STANLY STOKES SURRY SWAIN TRANSYLVANIA TYRRELL UNION VANCE WAKE WARREN WASHINGTON WATAUGA WAYNE
WILKES WILSON YADKIN YANCEY""".split())

def hours_of(t):
    m=HOURS_RE.match(t)
    if not m: return None
    h1,m1,a1,h2,m2,a2=m.groups()
    h1=int(h1)%12+(12 if a1=='p' else 0); h2=int(h2)%12+(12 if a2=='p' else 0)
    d=(h2+int(m2)/60)-(h1+int(m1)/60)
    return d if 0<d<=24 else None

def days_of(t):
    ds=DATE_RE.findall(t)
    if len(ds)==1: return 1
    if len(ds)>=2:
        a=datetime.date(2026,MONTHS[ds[0][0]],int(ds[0][1])); b=datetime.date(2026,MONTHS[ds[1][0]],int(ds[1][1]))
        return max(0,(b-a).days+1)
    return 0

def parse(path):
    sites=[]; cur=None; cur_site=None
    for l in open(path,encoding='utf-8',errors='replace'):
        l=l.rstrip('\n')
        if any(k in l for k in ('Questions related','CLICK HERE','Voting Sites for','Page ','Dates and Times','Board of Elections Office')): continue
        toks=[t for t in re.split(r' {2,}',l.strip()) if t]
        if not toks: continue
        i=0
        if toks[0] in COUNTIES: cur=toks[0]; i=1
        for t in toks[i:]:
            if HOURS_RE.match(t):
                if cur_site is not None: cur_site['rawhours'].append(t)
            elif WEEKDAY.match(t) or DATE_RE.search(t):
                if cur_site is not None: cur_site['rawdates'].append(t)
            elif t.startswith('*') or CITY_RE.search(t) or STREET_RE.match(t):
                continue
            else:
                cur_site=dict(county=cur,name=t,rawhours=[],rawdates=[]); sites.append(cur_site)
    out=[]
    for s in sites:
        if not s['rawhours'] or not s['rawdates']: continue
        # pair dates and hours positionally
        n=min(len(s['rawhours']),len(s['rawdates']))
        h=sum(days_of(s['rawdates'][k])*hours_of(s['rawhours'][k]) for k in range(n))
        # leftover hours without dates: assume 1 day each
        h+=sum(hours_of(t) or 0 for t in s['rawhours'][n:])
        s['hours']=h
        out.append(s)
    return out

if __name__=='__main__':
    for y,f in [(2022,'ev22.txt'),(2024,'ev24.txt'),(2026,'ev26.txt')]:
        s=parse('/Users/nealcaren/Downloads/'+f)
        ct=collections.Counter(x['county'] for x in s)
        print(f"{y}: {len(s)} sites, {len(ct)} counties, total site-hours {sum(x['hours'] for x in s):,.0f}")
        print("   sites/county top:", ct.most_common(4))
