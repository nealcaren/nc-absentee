import zipfile, io, csv, collections, sys
z=zipfile.ZipFile('/Users/nealcaren/Downloads/ncvoter_Statewide.zip')
st=collections.Counter(); race=collections.Counter(); party=collections.Counter(); n=0
prec=collections.defaultdict(set)
with z.open(z.namelist()[0]) as fh:
    r=csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace'),delimiter='\t')
    for row in r:
        n+=1
        st[row['voter_status_desc']]+=1
        race[row['race_code']]+=1; party[row['party_cd']]+=1
        if n<=2000000:
            prec[row['county_desc']].add(row['precinct_desc'])
        if n>=3000000: break
print("rows:",f"{n:,}")
print("status:",st.most_common())
print("race:",race.most_common())
print("party:",party.most_common())
print("ALAMANCE precincts sample:",sorted(prec['ALAMANCE'])[:8])
print("WAKE precincts sample:",sorted(prec['WAKE'])[:8])
