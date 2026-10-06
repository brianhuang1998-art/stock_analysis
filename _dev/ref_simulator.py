# Independent reference implementation of the dynamic-withdrawal simulation (written from the rules, not copied from the page's JS).
# Used to check retirement_dynamic_withdrawal.html and by _dev/order_sensitivity.py. Includes a port of the page's random number generator
# (mulberry32 + Box-Muller), so with the same seed it reproduces the page's 4,000 random paths.
# Independent reference implementation written from the rules (not copied from the page's JS)
import json, math, re, sys
M=0xFFFFFFFF
def mulberry32(seed):
    st={'a':seed & M}
    def rnd():
        st['a']=(st['a']+0x6D2B79F5)&M
        a=st['a']
        t=((a ^ (a>>15))*(1|a))&M
        t=((t+(((t ^ (t>>7))*(61|t))&M))&M) ^ t
        return ((t ^ (t>>14))&M)/4294967296
    return rnd
def normal_src(rnd):
    def n():
        u=0.0
        while u==0: u=rnd()
        return math.sqrt(-2*math.log(u))*math.cos(2*math.pi*rnd())
    return n

def pct(sorted_list,q):
    pos=(len(sorted_list)-1)*q
    lo=math.floor(pos); hi=math.ceil(pos)
    return sorted_list[lo]+(sorted_list[hi]-sorted_list[lo])*(pos-lo)

def run(p, rets, dynamic):
    T=p['T']; A=p['A']; w0=p['w0']; infl=p['infl']
    cap = min(infl,0.06) if p['cap6'] else infl
    bal=A; W=0.0
    out=dict(start=[0]*T,wd=[0]*T,wr=[1]*T,end=[0]*T,frozen=[0]*T,adj=[0]*T,fail=0,pp=0.0)
    ppsum=0.0
    for t in range(1,T+1):
        i=t-1
        planned=A*w0*(1+infl)**i
        if bal<=0:
            continue
        out['start'][i]=bal
        if t==1:
            W=A*w0
        elif not dynamic:
            W=planned
        else:
            adj=W*(1+cap)
            neg=rets[i-1]<0
            cpr_on = (not p['expire']) or (t<=T-15)
            if p.get('order','freeze')=='guardrail':
                cur=adj/bal                       # guardrails first, on the inflation-adjusted amount
                if cpr_on and cur>w0*1.2:
                    W=adj*0.9; out['adj'][i]=-1
                elif cur<w0*0.8:
                    W=adj*1.1; out['adj'][i]=1
                else:
                    freeze = neg and ((not p['modified']) or (cur>w0))
                    W = W if freeze else adj
                    out['frozen'][i]=1 if freeze else 0
            else:
                freeze = neg and ((not p['modified']) or (adj/bal>w0))   # freeze first, guardrails on the frozen amount
                W = W if freeze else adj
                out['frozen'][i]=1 if freeze else 0
                cur=W/bal
                if cpr_on and cur>w0*1.2:
                    W*=0.9; out['adj'][i]=-1
                elif cur<w0*0.8:
                    W*=1.1; out['adj'][i]=1
        out['wr'][i]=W/bal
        if W>=bal:
            out['wd'][i]=bal; out['end'][i]=0; ppsum+=bal/planned
            if not out['fail']: out['fail']=t
            bal=0
        else:
            out['wd'][i]=W; ppsum+=W/planned
            bal=(bal-W)*(1+rets[i]); out['end'][i]=bal
    out['pp']=ppsum/T
    out['ppLast']=out['wd'][T-1]/(A*w0*(1+infl)**(T-1))
    out['cuts']=sum(1 for x in out['adj'] if x==-1); out['raises']=sum(1 for x in out['adj'] if x==1); out['freezes']=sum(out['frozen'])
    return out

def summarize(runs,T):
    n=len(runs); years=[]
    for i in range(T):
        col=lambda k: sorted(r[k][i] for r in runs)
        s,w,r_,e=col('start'),col('wd'),col('wr'),col('end')
        years.append(dict(startMed=pct(s,.5),wdMed=pct(w,.5),wrMed=pct(r_,.5),wrLo=pct(r_,.1),wrHi=pct(r_,.9),
            endMed=pct(e,.5),endLo=pct(e,.1),endHi=pct(e,.9),
            cutShare=sum(1 for r in runs if r['adj'][i]==-1)/n,raiseShare=sum(1 for r in runs if r['adj'][i]==1)/n,frozenShare=sum(1 for r in runs if r['frozen'][i]==1)/n))
    ends=sorted(r['end'][T-1] for r in runs); pps=sorted(r['pp'] for r in runs); ppl=sorted(r['ppLast'] for r in runs)
    okr=[r for r in runs if not r['fail']]; ppsok=sorted(r['pp'] for r in okr); pplok=sorted(r['ppLast'] for r in okr)
    return dict(years=years,success=sum(1 for r in runs if not r['fail'])/n,endMed=pct(ends,.5),endLo=pct(ends,.1),ppMed=(pct(ppsok,.5) if okr else None),ppLastMed=(pct(pplok,.5) if okr else None),ppAllMed=pct(pps,.5),ppLastAllMed=pct(ppl,.5),
        cuts=sum(r['cuts'] for r in runs)/n,raises=sum(r['raises'] for r in runs)/n,freezes=sum(r['freezes'] for r in runs)/n,
        lastWdMed=years[T-1]['wdMed'],failYear=(runs[0]['fail'] if n==1 else 0))

def simulate(f):
    assets=float(f['assets'])
    if f.get('goal')=='spend':
        assets=float(f['monthlySpend'])*(1+float(f['inflation'])/100)**int(f['yearsToRetire'])*12/(float(f['wr0'])/100)
    p=dict(A=assets,w0=float(f['wr0'])/100,infl=float(f['inflation'])/100,T=int(f['years']),
           modified=f['freezeMode']=='modified',cap6=f['inflCap']=='6',expire=f['cprExpire']=='yes',order=f.get('order','freeze'))
    T=p['T']; ret=float(f['annualReturn'])/100
    dyn=[];fix=[]
    if f['mode']=='stress':
        sy=int(f['stressYears']); sr=float(f['stressReturn'])/100
        rets=[sr if i<sy else ret for i in range(T)]
        dyn.append(run(p,rets,True)); fix.append(run(p,rets,False))
    else:
        m=ret; s=float(f['volatility'])/100
        sig2=math.log(1+s*s/((1+m)*(1+m))); mu=math.log(1+m)-sig2/2; sig=math.sqrt(sig2)
        nrm=normal_src(mulberry32(20060301))
        for k in range(4000):
            rets=[math.exp(mu+sig*nrm())-1 for _ in range(T)]
            dyn.append(run(p,rets,True)); fix.append(run(p,rets,False))
    return summarize(dyn,T),summarize(fix,T),dyn,fix

def rel(a,b):
    if a==b: return 0.0
    return abs(a-b)/max(1e-9,abs(a),abs(b))

