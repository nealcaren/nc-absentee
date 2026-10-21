import zipfile, io, csv, collections, pickle, sys
src, enc, out = sys.argv[1], sys.argv[2], sys.argv[3]
z=zipfile.ZipFile(src)
pairs=collections.defaultdict(set)
with z.open(z.namelist()[0]) as fh:
    r=csv.reader(io.TextIOWrapper(fh,encoding=enc,errors='replace'),delimiter='\t')
    hdr=[h.strip() for h in next(r)]
    ix={k:i for i,k in enumerate(hdr)}
    ci,ai,di=ix['county_desc'],ix['precinct_abbrv'],ix['precinct_desc']
    for row in r:
        if len(row)<=max(ci,ai,di): continue
        c=row[ci].strip(); a=row[ai].strip(); d=row[di].strip()
        if d: pairs[c].add((d,a))
    # drop descs that map to multiple abbrv (ambiguous)
    cw={}; amb=0
    for c,s in pairs.items():
        m=collections.defaultdict(set)
        for d,a in s: m[d].add(a)
        cw[c]={d:list(a)[0] for d,a in m.items() if len(a)==1}
        amb+=sum(1 for d,a in m.items() if len(a)>1)
    print(f"{src.split('/')[-1]}: {len(cw)} counties, {sum(len(v) for v in cw.values())} precincts, {amb} ambiguous descs",flush=True)
pickle.dump(cw,open(out,'wb'))
