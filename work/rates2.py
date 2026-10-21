import pickle, collections
reg={y:pickle.load(open(f'work/reg{y}.pkl','rb')) for y in (2022,2024,2026)}
A=pickle.load(open('work/abs_full.pkl','rb'))
def tot(d,k): return sum(v.get(k,0) for v in d.values())

print("BY PARTY (early turnout rate, first 6 days)")
print(f"{'party':10}{'2022':>9}{'2024':>9}{'2026':>9}{'26-22':>9}")
for p in ['DEM','REP','UNA','LIB','GRE']:
    r=[100*tot(A[y]['party'],p)/tot(reg[y]['party'],p) for y in (2022,2024,2026)]
    print(f"{p:10}{r[0]:9.2f}{r[1]:9.2f}{r[2]:9.2f}{r[2]-r[0]:+9.2f}")

print("\nBY AGE (early turnout rate)")
print(f"{'age':10}{'2022':>9}{'2024':>9}{'2026':>9}{'26-22':>9}")
for a in ['<25','25-34','35-44','45-54','55-64','65-74','75+']:
    r=[100*tot(A[y]['age'],a)/tot(reg[y]['age'],a) for y in (2022,2024,2026)]
    print(f"{a:10}{r[0]:9.2f}{r[1]:9.2f}{r[2]:9.2f}{r[2]-r[0]:+9.2f}")

print("\nRACE x PARTY, 2026 early turnout rate (selected)")
for p in ['DEM','REP','UNA']:
    pass
