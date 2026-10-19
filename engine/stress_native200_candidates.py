#!/usr/bin/env python3
"""Zero-risk research-only stress test of SELECTED native200 hypotheses.
Freeze candidates first, then revalue with higher latency and adverse price
slippage, without reranking on their own later outcomes.
"""
from pathlib import Path
import json,math,sys,collections,statistics
import numpy as np
F=Path(__file__).resolve().parent
sys.path.insert(0,str(F))
import systematic_native200_scan as m
CANDIDATES=(
 "NO_80_15_ANY_SPREAD_LE2C_FIRST_180S",
 "NO_80_15_SPOT_FAVORED_AND_ALIGNED_SPREAD_LE2C_FIRST_180S",
 "YES_50_15_MOVE30_OPPOSED_SPREAD_LE2C_SECOND_90S",
 "YES_55_10_MOVE10_ALIGNED_SPREAD_LE2C_FIRST_180S",
 "NO_75_15_MOVE10_30_PERSISTENT_SPREAD_LE2C_FIRST_90S",
)
STRESSES=(("BASE2S",10,0.),("LATENCY4S",20,0.),("LATENCY8S",40,0.),
          ("SLIPPAGE_HALF_CENT_EACH",10,.005),
          ("LATENCY4S_SLIPPAGE_HALF_CENT_EACH",20,.005))
def parse(key):
 for side in ("YES","NO"):
  for l in m.LIMITS:
   for delta in m.TARGETS:
    pref=f"{side}_{l}_{delta}_"
    if not key.startswith(pref):continue
    tail=key[len(pref):]
    for t in m.TIME:
     suf="_"+t
     if not tail.endswith(suf):continue
     tail2=tail[:-len(suf)]
     for b in m.BOOK:
      bs="_"+b
      if not tail2.endswith(bs):continue
      f=tail2[:-len(bs)]
      if f in m.TRAJECTORY:
       return side,l,delta,f,b,t
 raise ValueError(key)
def eval_one(book,info,delay,slip,oracle):
 side,l,delta,fname,bname,tname=info
 i=0 if side=="YES" else 1
 j=m.LIMITS.index(l)
 n=int(book["sizes"][j]);lim=l/100.;goal=(l+delta)/100.
 fs=m.features(book);f,b,t=m.regimes(fs,i)
 sigmask=f[fname]&b[bname]&t[tname]
 sigmask[:m.ENTRY_BEGIN]=False;sigmask[m.ENTRY_END:]=False
 signal=book["ask"][i]
 sigmask &= np.isfinite(signal)&(signal<=lim+1e-6)&(signal>=lim-.07)
 inds=np.flatnonzero(sigmask)
 if len(inds)==0:return None
 s=int(inds[0])
 # Entry after delay, posted ONE limit, stays until 180 sec.
 opp=1-i
 bidavg_opp=book["bid_avg"][opp,:,j]
 last_opp=book["bid_worst"][opp,:,j]
 entryavg=1-bidavg_opp+slip
 worstask=1-last_opp+slip
 cash=n*entryavg+.07*entryavg*(1-entryavg)*n
 buy=np.isfinite(entryavg)&(worstask<=lim+1e-6)&(entryavg>=lim-.07)&(cash<=10.01)&(cash>=8)
 valid=np.flatnonzero(buy[s+delay:m.ENTRY_END])
 if len(valid)==0:return None
 ent=s+delay+int(valid[0])
 ep=float(entryavg[ent]);ec=n*ep+m.fee(ep,n)
 # Exit at higher bid after delay with true L2 q volume available.
 selavg=book["bid_avg"][i,:,j]-slip
 selworst=book["bid_worst"][i,:,j]-slip
 sellable=np.isfinite(selavg)&np.isfinite(selworst)&(selworst>=goal-1e-6)
 indices=np.flatnonzero(sellable[ent+1:m.CUTOFF-delay])
 exidx=None
 for k in indices:
  kk=ent+1+int(k)
  if sellable[kk+delay]:
   exidx=kk+delay;break
 if exidx is not None:
  sp=float(selavg[exidx])
  pnl=round(n*sp-m.fee(sp,n)-ec,4)
  return (pnl,"TARGET",ent*.2,exidx*.2)
 # Preclose if displayed sellable depth can close ALL shares
 aft=np.flatnonzero(np.isfinite(selavg[4450:]))
 if len(aft)>0:
  k=4450+int(aft[0])
  sp=float(selavg[k])
  pnl=round(n*sp-m.fee(sp,n)-ec,4)
  return (pnl,"PRECLOSE",ent*.2,k*.2)
 if oracle is not None and oracle.get("status")=="CONFIDENT":
  won=(bool(oracle["proxy_yes_wins"]) if side=="YES" else not bool(oracle["proxy_yes_wins"]))
  pnl=round((n if won else 0)-ec,4)
  return (pnl,"PROXY_SETTLEMENT",ent*.2,900)
 return (None,"AMBIGUOUS",ent*.2,900)
def oracle_map():
 return m.ORACLES
def run():
 result=[]
 for coin in m.COINS:
  for h in m.WINDOWS:
   src=m.unpack(coin,h)
   period="TRAIN" if h in m.TRAIN else "TEST" if h in m.TEST else "VALIDATION"
   out={"coin":coin,"window":h,"period":period,"candidate_results":{}}
   for key in CANDIDATES:
    tup=parse(key);out['candidate_results'][key]={}
    for label,delay,slip in STRESSES:
     out['candidate_results'][key][label]=eval_one(src,tup,delay,slip,m.ORACLES.get((coin,h)))
   result.append(out)
  print("STRESS_COMPLETE_COIN",coin,flush=True)
 def aggregate(cand,stress,period):
  vals=[r['candidate_results'][cand][stress] for r in result if r['period']==period]
  trades=[v for v in vals if v is not None]
  known=[v for v in trades if v[0] is not None]
  return {"markets":len(vals),"trades":len(trades),"known":len(known),
   "wins":sum(v[0]>0 for v in known),"target_exits":sum(v[1]=="TARGET" for v in known),
   "net":round(sum(v[0] for v in known),3),"worst":round(min((v[0] for v in known),default=0),3),
   "median_hold":round(statistics.median(v[3]-v[2] for v in known),1) if known else None}
 sums={}
 for cand in CANDIDATES:
  sums[cand]={}
  for stress,*_ in STRESSES:
   sums[cand][stress]={p:aggregate(cand,stress,p) for p in ("TRAIN","TEST","VALIDATION")}
   print("SENSITIVITY",cand,stress,sums[cand][stress],flush=True)
 (F/"systematic_native200_stress_results.json").write_text(json.dumps({"candidates":CANDIDATES,"assumptions":STRESSES,
  "groups":sums,"market_trades":result},indent=2)+"\n")
 print("FINISHED_STRESS",flush=True)
if __name__=="__main__":run()
