import pickle, collections
d=pickle.load(open('work/agg.pkl','rb'))

def show(key, order=None):
    print(f"\n--- {key.upper()} (share of in-person early votes, matched 6-day window)")
    vals=set()
    for yr in (2022,2024,2026): vals|=set(d[yr]['demo_win'][key])
    vals=order or sorted(vals, key=lambda v:-d[2026]['demo_win'][key].get(v,0))
    print(f"{'':18}{'2022':>10}{'2024':>10}{'2026':>10}   {'26-22':>7}  {'26-24':>7}")
    for v in vals:
        row=[]
        for yr in (2022,2024,2026):
            c=d[yr]['demo_win'][key]; t=sum(c.values())
            row.append(100*c.get(v,0)/t if t else 0)
        print(f"{str(v)[:17]:18}{row[0]:10.2f}{row[1]:10.2f}{row[2]:10.2f}   {row[2]-row[0]:+7.2f}  {row[2]-row[1]:+7.2f}")

show('race')
show('ethnicity')
show('party',['DEM','REP','UNA','LIB','GRN','OTH'])
show('gender')
show('age',['<25','25-34','35-44','45-54','55-64','65-74','75+','UNK'])

print("\n--- TOTAL in-person early votes in matched 6-day window")
for yr in (2022,2024,2026):
    print(f"  {yr}: {d[yr]['n_win']:>10,}   mail accepted in window: {d[yr]['mail_win']:>9,}")
print("\n2026 as share of 2022:", f"{d[2026]['n_win']/d[2022]['n_win']*100:.1f}%")
print("2026 as share of 2024:", f"{d[2026]['n_win']/d[2024]['n_win']*100:.1f}%")
