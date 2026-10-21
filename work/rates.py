import pickle, collections
reg={2022:pickle.load(open('work/reg2022.pkl','rb')),
     2024:pickle.load(open('work/reg2024.pkl','rb')),
     2026:pickle.load(open('work/reg2026.pkl','rb'))}
absn=pickle.load(open('work/abs_prec.pkl','rb'))

NAME={'W':'White','B':'Black','A':'Asian','I':'Am Indian','M':'Two+','P':'Pacific Isl','O':'Other','U':'Undesignated'}

def tot(d,k):
    return sum(v.get(k,0) for v in d.values())

print("EARLY TURNOUT RATE (share of active registered voters voting in the first 6 days)")
print(f"{'race':16}{'2022':>9}{'2024':>9}{'2026':>9}{'26-22':>9}")
for rc in ['W','B','A','I','M','O','U','P']:
    row=[]
    for yr in (2022,2024,2026):
        num=tot(absn[yr]['cty'],rc); den=tot(reg[yr]['cty'],rc)
        row.append(100*num/den if den else 0)
    print(f"{NAME[rc]:16}{row[0]:9.2f}{row[1]:9.2f}{row[2]:9.2f}{row[2]-row[0]:+9.2f}")

print("\nTotal early turnout (same window):")
for yr in (2022,2024,2026):
    num=sum(sum(v.values()) for v in absn[yr]['cty'].values())
    den=sum(sum(v.values()) for v in reg[yr]['cty'].values())
    print(f"  {yr}: {num:,} / {den:,} = {100*num/den:.2f}%")
