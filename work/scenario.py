import pickle
A=pickle.load(open('work/abs_full.pkl','rb'))
def e6(y,p): return sum(v.get(p,0) for v in A[y]['party'].values())
d6,r6=e6(2026,'DEM'),e6(2026,'REP'); lead=d6-r6
N=2_900_000; rem=N-d6-r6
print(f"2026 banked: D {d6:,}  R {r6:,}  lead {lead:,}   assumed final D+R {N:,}  remaining {rem:,}\n")
print(f"{'R share of remaining':>22}{'D-R registration':>20}{'after hist. correction':>26}")
for s in (0.500,0.515,0.530,0.540,0.545,0.550):
    dm=lead+rem*(1-2*s); pts=100*dm/N
    print(f"{100*s:>21.1f}%{pts:>+19.1f}{pts-3.3:>+13.1f} to {pts-1.7:>+6.1f}")
print("\nbreak-even R share = %.2f%%" % (100*(0.5+lead/(2*rem))))
print("\nIf 2026 final totals merely repeat 2022 (D 1,283,989 / R 1,303,697):")
print(f"  R would need {100*(1303697-r6)/((1303697-r6)+(1283989-d6)):.1f}% of remaining two-party votes")
