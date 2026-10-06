# Run:  python3 papers/verification/order_sensitivity.py   (about 1 minute)
# Compare two readings of the order of the withdrawal-rule (freeze) and the guardrails, on identical random paths.
#  "freeze"    : decide the freeze first, then test the guardrails on the frozen amount (the website's default; reading of p.54 "using the decision rules in effect")
#  "guardrail" : test the guardrails on the inflation-adjusted amount first; the freeze only applies when no guardrail fires (reads Table 5 as a decision tree)
import math, os, sys, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ref_simulator as ref

def run(p, rets, order):
    T=p['T']; A=p['A']; w0=p['w0']; infl=p['infl']
    bal=A; W=0.0; fail=0; cuts=raises=freezes=0; ppsum=0.0; wd_total=0.0; ends=[]
    for t in range(1,T+1):
        i=t-1; planned=A*w0*(1+infl)**i
        if bal<=0: continue
        if t==1: W=A*w0
        else:
            base=W*(1+infl); neg=rets[i-1]<0
            cpr_on=(not p['expire']) or t<=T-15
            if order=='freeze':
                freeze=neg and (base/bal>w0)
                Wn=W if freeze else base
                if freeze: freezes+=1
                cur=Wn/bal
                if cpr_on and cur>1.2*w0: Wn*=0.9; cuts+=1
                elif cur<0.8*w0: Wn*=1.1; raises+=1
                W=Wn
            else:
                cur=base/bal
                if cpr_on and cur>1.2*w0: W=base*0.9; cuts+=1
                elif cur<0.8*w0: W=base*1.1; raises+=1
                elif neg and cur>w0: W=W; freezes+=1
                else: W=base
        if W>=bal:
            ppsum+=bal/planned; wd_total+=bal; fail=fail or t; bal=0
        else:
            ppsum+=W/planned; wd_total+=W; bal=(bal-W)*(1+rets[i])
    return dict(fail=fail,end=bal,pp=ppsum/T,cuts=cuts,raises=raises,freezes=freezes,wd=wd_total)

def paired(f, n=4000):
    p=dict(A=float(f['assets']),w0=float(f['wr0'])/100,infl=float(f['inflation'])/100,T=int(f['years']),expire=True)
    T=p['T']; m=float(f['annualReturn'])/100; s=float(f['volatility'])/100
    sig2=math.log(1+s*s/((1+m)**2)); mu=math.log(1+m)-sig2/2; sig=math.sqrt(sig2)
    nrm=ref.normal_src(ref.mulberry32(20060301))
    A=[];B=[]
    for _ in range(n):
        rets=[math.exp(mu+sig*nrm())-1 for _ in range(T)]
        A.append(run(p,rets,'freeze')); B.append(run(p,rets,'guardrail'))
    return A,B

def med(x): return statistics.median(x)
def summ(R):
    n=len(R)
    return dict(success=sum(1 for r in R if not r['fail'])/n, endMed=med([r['end'] for r in R]), ppMed=med([r['pp'] for r in R]),
                cuts=sum(r['cuts'] for r in R)/n, freezes=sum(r['freezes'] for r in R)/n, raises=sum(r['raises'] for r in R)/n)

base=dict(assets='10000000',wr0='5.3',annualReturn='12',volatility='17',inflation='4.5',years='40')
cases=[
 ("paper-like example: 40y, IWR 5.3%, 12%/17%/4.5%", base),
 ("same, IWR 5.8%", dict(base,wr0='5.8')),
 ("same, IWR 6.5% (aggressive)", dict(base,wr0='6.5')),
 ("page default: 30y, IWR 5%, 7%/18%/2%", dict(assets='10000000',wr0='5',annualReturn='7',volatility='18',inflation='2',years='30')),
 ("30y, IWR 4%, 8%/16%/2.5%", dict(assets='10000000',wr0='4',annualReturn='8',volatility='16',inflation='2.5',years='30')),
]
print(f"{'case':<52}{'order':<8}{'success':>8}{'endMed(萬)':>11}{'PP':>6}{'cuts':>6}{'frz':>6}{'raise':>6}  paths where they differ")
for name,f in cases:
    A,B=paired(f)
    sa,sb=summ(A),summ(B)
    diff=sum(1 for a,b in zip(A,B) if abs(a['wd']-b['wd'])>1e-6)/len(A)
    for tag,s in (('freeze',sa),('guardrail',sb)):
        print(f"{name if tag=='freeze' else '':<52}{tag:<8}{s['success']:>8.2%}{s['endMed']/1e4:>11,.0f}{s['ppMed']:>6.0%}{s['cuts']:>6.1f}{s['freezes']:>6.1f}{s['raises']:>6.1f}  {diff:.0%}" if tag=='freeze' else f"{'':<52}{tag:<8}{s['success']:>8.2%}{s['endMed']/1e4:>11,.0f}{s['ppMed']:>6.0%}{s['cuts']:>6.1f}{s['freezes']:>6.1f}{s['raises']:>6.1f}")
    # size of the effect among paths that differ
    dd=[(b['end']-a['end']) for a,b in zip(A,B) if abs(a['wd']-b['wd'])>1e-6]
    if dd: print(f"{'':<52}  among differing paths: median end-asset change (guardrail-first - freeze-first) = {med(dd)/1e4:,.0f} 萬; P(guardrail-first worse) = {sum(1 for x in dd if x<0)/len(dd):.0%}")
