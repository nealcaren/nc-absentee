import pickle
A=pickle.load(open('work/abs_full.pkl','rb'))
H=pickle.load(open('work/history2.pkl','rb'))
def e6(y,p): return sum(v.get(p,0) for v in A[y]['party'].values())

print("Two-party (D+R) early votes, first 6 days")
for y in (2022,2024,2026):
    d,r=e6(y,'DEM'),e6(y,'REP')
    print(f"  {y}:  DEM {d:>8,}  REP {r:>8,}   D-R {d-r:>+9,}   D share of D+R {100*d/(d+r):.1f}%")

print("\nWhere the rest of the vote came from (post-day-6), two-party only")
post={}
for y in (2022,2024):
    dT,rT=H[y]['tot']['DEM'],H[y]['tot']['REP']
    d6,r6=e6(y,'DEM'),e6(y,'REP')
    pd,pr=dT-d6,rT-r6
    post[y]=(pd,pr)
    print(f"  {y}:  post-day-6  DEM {pd:>9,}  REP {pr:>9,}   R share of post = {100*pr/(pd+pr):.1f}%")
    print(f"        final D-R registration margin = {dT-rT:+,}  ({100*(dT-rT)/(dT+rT):+.2f} pts)")

print("\n2026 BREAK-EVEN: R share of remaining two-party votes needed to tie")
d6,r6=e6(2026,'DEM'),e6(2026,'REP')
lead=d6-r6
for N in (2_600_000,2_800_000,3_000_000,3_200_000):
    rem=N-d6-r6
    need=0.5+lead/(2*rem)
    print(f"  if final D+R = {N/1e6:.1f}M: remaining {rem/1e6:.2f}M -> R needs {100*need:.1f}%")

print("\nImplied outcome if R repeats its historical post-day-6 share")
for s in (0.514,0.515,0.530,0.545):
    for N in (2_800_000,3_000_000):
        rem=N-d6-r6
        dm=lead+rem*(1-2*s)
        print(f"  R share {100*s:.1f}%, final D+R {N/1e6:.1f}M -> D-R registration margin {100*dm/N:+.1f} pts")

print("\nCalibration: registration margin vs actual two-party vote")
print("  2022: registration R+0.76  ->  actual R+4.07   (R shift +3.3)")
print("  2024: registration R+2.17  ->  actual R+3.83   (R shift +1.7)")
