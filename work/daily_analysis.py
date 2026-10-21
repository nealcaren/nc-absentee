import pickle, collections, datetime
D=pickle.load(open('work/daily.pkl','rb'))
ED={y:datetime.date.fromisoformat(D[y]['election']) for y in D}

def series(y,party=None):
    ed=ED[y]; s={}
    for dt,n in D[y]['total'].items():
        t=(ed-dt).days
        if party is None: s[t]=n
        else: s[t]=D[y]['party'].get(f"{t}|{party}",0)
    return s

def dayk(y,party=None):
    ed=ED[y]; s={}
    for dt,n in D[y]['total'].items():
        k=(dt-(ed-datetime.timedelta(days=19))).days+1
        s[k]=s.get(k,0)+(n if party is None else D[y]['party'].get(f"{(ed-dt).days}|{party}",0))
    return s

print(f"{'day':>4}{'date26':>12}{'dow':>5}{'2022':>10}{'2024':>10}{'2026':>10}{'26/22 d1':>10}")
S={y:dayk(y) for y in (2022,2024,2026)}
for k in range(1,18):
    dt=ED[2026]-datetime.timedelta(days=20-k)
    v22,v24,v26=S[2022].get(k,0),S[2024].get(k,0),S[2026].get(k,0)
    ratio=f"{v26/S[2022][k]:.2f}x" if k in S[2026] and S[2022].get(k) else ""
    print(f"{k:>4}{dt.isoformat():>12}{dt.strftime('%a'):>5}{v22:>10,}{v24:>10,}{v26:>10,}{ratio:>10}")

print("\nCumulative share of each year's total in-person early vote:")
print(f"{'day':>4}{'2022':>9}{'2024':>9}{'2026*':>9}")
for k in range(1,18):
    a=sum(S[2022].get(i,0) for i in range(1,k+1))/sum(S[2022].values())
    b=sum(S[2024].get(i,0) for i in range(1,k+1))/sum(S[2024].values())
    c=sum(S[2026].get(i,0) for i in range(1,k+1))/sum(S[2026].values()) if k<=6 else None
    cs=f"{c:>8.1%}" if c is not None else f"{'—':>9}"
    print(f"{k:>4}{a:>9.1%}{b:>9.1%}{cs:>9}")

print("\nShare of the 6-day total by day (shape check):")
for y in (2022,2024,2026):
    tot=sum(S[y].get(i,0) for i in range(1,7))
    sh=[S[y].get(i,0)/tot for i in range(1,7)]
    print(f"   {y}: "+"  ".join(f"{100*x:4.1f}" for x in sh))

print("\nDay-of-week mix, share of 6-day total:")
for y in (2022,2024,2026):
    agg=collections.Counter()
    for k in range(1,7):
        dt=ED[y]-(datetime.timedelta(days=20-k))
        agg[dt.strftime('%a')]+=S[y].get(k,0)
    tot=sum(agg.values())
    print(f"   {y}: "+"  ".join(f"{d} {100*agg[d]/tot:4.1f}%" for d in ('Thu','Fri','Sat','Sun','Mon','Tue')))

for y in (2022,2024):
    tot=sum(S[y].values()); c6=sum(S[y].get(i,0) for i in range(1,7))
    print(f"\n{y}: total in-person early {tot:,}, day-6 cumulative {c6:,} = {c6/tot:.1%}")
