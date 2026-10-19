#!/usr/bin/env python3
"""Read-only systematic finite-grid search with strict chronological split.
All scenarios: single early order, $8-$10 spend, limit sales / expiry proxy.
Entry features computed using only <=signal 200ms book+stale-checked coin tape.
Entry/exit hypothetical, exchange queue fills NOT verified.
"""
from pathlib import Path
import sys,json,os,math,statistics,collections
import numpy as np
F=Path(__file__).resolve().parent
DATA=F/"prepared_native200"
COINS=("ETH","HYPE","BNB","XRP","NEAR","ZEC","DOGE")
TRAIN=("0800","0815","0830","0845","0900","0915","0930","0945")
TEST=("1000","1015","1030","1045")
VALID=("1100","1115","1130","1145","1200","1215","1230","1245")
WINDOWS=TRAIN+TEST+VALID
LIMITS=list(range(20,81,5));TARGETS=(5,10,15)
TICKS=4500;ENTRY_BEGIN=200;ENTRY_END=900;CUTOFF=4425;DELAY=10
# broad deterministic feature family, not "every conceivable" real-number function
TRAJECTORY=(
 "ANY","SPOT_FAVORED","SPOT_UNFAVORED","CLOSE_5BP","CLOSE_12BP","FAR_12BP",
 "MOVE10_ALIGNED","MOVE10_OPPOSED","MOVE10_QUIET","MOVE10_STRONG",
 "MOVE30_ALIGNED","MOVE30_OPPOSED","MOVE10_30_PERSISTENT",
 "STILL_UNFAVORED_BUT_RECOVERING","SPOT_FAVORED_AND_ALIGNED")
BOOK=(
 "ANY","QUOTE_5S_DROPPED3","QUOTE_5S_DROPPED6",
 "QUOTE_5S_ROSE3","QUOTE_5S_QUIET",
 "BOOK_MOVE5_AND_SPOT_QUIET","SPREAD_LE2C")
TIME=("FIRST_90S","SECOND_90S","FIRST_180S")
# For a fixed coin/limit/side, no future data used to choose entry.
# Multiple exit limits compare separate hypothetical outcomes, never compound.
def fee(p,n):
 return math.ceil(max(0.,.07*p*(1-p)*n)*10000-1e-9)/10000
def lag(a,count):
 z=np.full(a.shape,np.nan,np.float32)
 z[count:]=a[:-count]
 return z
def features(book):
 bps=book["bps"];bid=book["bid"];ask=book["ask"]
 fs={}
 m10=bps-lag(bps,50);m30=bps-lag(bps,150);m5=bps-lag(bps,25)
 quote5=bid-lag(bid,25)
 fs["m10"]=m10;fs["m30"]=m30;fs["m5"]=m5;fs["quote5"]=quote5
 fs["bid"]=bid;fs["ask"]=ask;fs["bps"]=bps
 fs["spread"]=ask-bid
 return fs
def regimes(fs,side):
 d=fs["bps"];m10=fs["m10"];m30=fs["m30"];m5=fs["m5"]
 sg=1 if side==0 else -1
 D=d*sg;M10=m10*sg;M30=m30*sg
 b5=fs["quote5"][side];spread=fs["spread"][side]
 f={
 "ANY":np.isfinite(d),
 "SPOT_FAVORED":D>=2,
 "SPOT_UNFAVORED":D<=-2,
 "CLOSE_5BP":abs(d)<=5,
 "CLOSE_12BP":abs(d)<=12,
 "FAR_12BP":abs(d)>=12,
 "MOVE10_ALIGNED":M10>=1,
 "MOVE10_OPPOSED":M10<=-1,
 "MOVE10_QUIET":abs(m10)<=1.5,
 "MOVE10_STRONG":abs(m10)>=3,
 "MOVE30_ALIGNED":M30>=2,
 "MOVE30_OPPOSED":M30<=-2,
 "MOVE10_30_PERSISTENT":(M10>=.7)&(M30>=2),
 "STILL_UNFAVORED_BUT_RECOVERING":(D<=-2)&(M10>=.7),
 "SPOT_FAVORED_AND_ALIGNED":(D>=2)&(M10>=.7),
 }
 b={
 "ANY":np.isfinite(b5),
 "QUOTE_5S_DROPPED3":b5<=-.03,
 "QUOTE_5S_DROPPED6":b5<=-.06,
 "QUOTE_5S_ROSE3":b5>=.03,
 "QUOTE_5S_QUIET":abs(b5)<=.02,
 "BOOK_MOVE5_AND_SPOT_QUIET":(abs(b5)>=.06)&(abs(m5)<=2.),
 "SPREAD_LE2C":spread<=.02,
 }
 t=np.arange(TICKS)
 times={"FIRST_90S":t<450,"SECOND_90S":(t>=450)&(t<900),
       "FIRST_180S":t<900}
 return f,b,times
def oracle_map():
 # Complete raw index 60-sec proxy map already computed using earlier archive
 # and later validation. Close-to-target ambiguous inputs stay unknown.
 out={}
 p=F/"coin_regime_settlement_proxy_results.json"
 if p.exists():
  obj=json.loads(p.read_text())
  for x in obj["coin_windows"]:
   out[(x["coin"],x["window"])]=x["oracle"]
 p=F/"third_block_validation_results.json"
 if p.exists():
  obj=json.loads(p.read_text())
  for x in obj["markets"]:
   out[(x["coin"],x["hour_ed"])]=x["oracle"]
 return out
ORACLES=oracle_map()
def next_candidates(mask):
 # next valid index at time i, or sentinel if none.
 out=np.minimum.accumulate(np.where(mask,np.arange(TICKS),TICKS)[::-1])[::-1]
 return out
def unpack(c,h):
 x=np.load(DATA/(c+"_"+h+".npz"))
 q={k:x[k] for k in ("ask","bid","bps","bid_avg","bid_worst","sizes")}
 return q
def evaluate_market(c,h):
 q=unpack(c,h);q_sizes=q["sizes"]
 fs=features(q)
 oracle=ORACLES.get((c,h),{})
 verified=oracle.get("status")=="CONFIDENT"
 settlement_yes=oracle.get("proxy_yes_wins") if verified else None
 outcome={}
 for side in range(2):
  f,b,t=regimes(fs,side)
  opposite=1-side
  for j,limit_c in enumerate(LIMITS):
   limit=limit_c/100
   n=int(q_sizes[j])
   # Model actual BUY at opposite-side BID levels. Worst level
   # must remain within BUY limit and average order cost >=$8.
   bid_avg_opp=q["bid_avg"][opposite,:,j]
   bid_worst_opp=q["bid_worst"][opposite,:,j]
   entry_avg=1-bid_avg_opp;entry_worst=1-bid_worst_opp
   buy_cost=entry_avg*n + .07*entry_avg*(1-entry_avg)*n
   able=np.isfinite(entry_avg)&(entry_worst<=limit+1e-7)&(entry_avg>=limit-.07-1e-7)&(buy_cost>=8)&(buy_cost<=10.01)
   # True resting order, no duplicate BUY, limit set by first signal.
   buy_next=next_candidates(able)
   actual_exit={}
   for delta_c in TARGETS:
    goal=(limit_c+delta_c)/100
    if goal>=1:continue
    worst=q["bid_worst"][side,:,j]
    sellable=np.isfinite(worst)&(worst>=goal-1e-7)
    # After a target signal, quote must remain executable 2s later
    settleable=np.zeros(TICKS,dtype=bool)
    settleable[:-DELAY]=sellable[:-DELAY]&sellable[DELAY:]
    settleable[CUTOFF:]=False
    actual_exit[delta_c]=next_candidates(settleable)
   # Time 890s to close (last 10s) recorded market-book sell if possible.
   prec_possible=np.isfinite(q["bid_avg"][side,4450:4500,j])
   preidx=int(np.flatnonzero(prec_possible)[0]+4450) if np.any(prec_possible) else None
   for base,fb in f.items():
    if not np.any(fb[ENTRY_BEGIN:ENTRY_END]):continue
    for bookname,bb in b.items():
     ready=fb&bb&np.isfinite(q["ask"][side])&(q["ask"][side]<=limit+1e-7)&(q["ask"][side]>=limit-.07-1e-7)
     if not np.any(ready[ENTRY_BEGIN:ENTRY_END]):continue
     for timename,tt in t.items():
      selected=ready&tt
      selected[:ENTRY_BEGIN]=False
      selected[ENTRY_END:]=False
      which=np.flatnonzero(selected)
      if not len(which):continue
      sig=int(which[0])
      entry_tick=int(buy_next[sig+DELAY]) if sig+DELAY<TICKS else TICKS
      if entry_tick>=ENTRY_END:continue
      avgentry=float(entry_avg[entry_tick])
      actual_cost=round(n*avgentry+fee(avgentry,n),4)
      if actual_cost>10.02 or actual_cost<8:continue
      for delta_c,nxt in actual_exit.items():
       next_sell=int(nxt[entry_tick+1]) if entry_tick+1<TICKS else TICKS
       if next_sell<TICKS:
        exit_tick=next_sell+DELAY
        avg_sell=float(q["bid_avg"][side,exit_tick,j])
        cash=n*avg_sell-fee(avg_sell,n)
        pnl=round(cash-actual_cost,4)
        reason="LIMIT_EXIT"
       elif preidx is not None and preidx>entry_tick:
        exit_tick=preidx
        avg_sell=float(q["bid_avg"][side,preidx,j])
        cash=n*avg_sell-fee(avg_sell,n)
        pnl=round(cash-actual_cost,4)
        reason="PRECLOSE_EXIT"
       elif verified:
        exit_tick=TICKS
        side_won=(settlement_yes if side==0 else not settlement_yes)
        pnl=round((n if side_won else 0)-actual_cost,4)
        reason="PROXY_SETTLEMENT"
       else:
        exit_tick=TICKS;reason="AMBIGUOUS_EXPIRY";pnl=None
       ident=f"{['YES','NO'][side]}_{limit_c}_{delta_c}_{base}_{bookname}_{timename}"
       outcome[ident]={"pnl":pnl,"status":reason,
          "entry_s":round(entry_tick*.2,1),"exit_s":round(exit_tick*.2,1),
          "spot_bps":round(float(q["bps"][sig]),2),
          "m10_bps":round(float(fs["m10"][sig]),2),
          "quote5_change_c":round(float(fs["quote5"][side,sig])*100,2),
          "contract_ask":round(avgentry,4),"qty":n,"spent":actual_cost,
          "side":["YES","NO"][side],"target":(limit_c+delta_c)/100}
 return outcome
def aggregate(results,keys,period):
 # Each unique market has <=1 simulated purchase per scenario.
 scores=[]
 markets=[w for w in results if w[2]==period]
 for key in keys:
  seq=[z[3][key] for z in markets if key in z[3]]
  successes=[x for x in seq if x["pnl"] is not None]
  n=len(successes)
  pnl=round(sum(x["pnl"] for x in successes),3)
  nwin=sum(x["pnl"]>0 for x in successes)
  losses=sum(x["pnl"]<=0 for x in successes)
  mark={x["status"] for x in seq}
  scores.append((key,n,pnl,nwin,losses))
 return {s[0]:{"n":s[1],"net":s[2],"wins":s[3],"losses":s[4]} for s in scores}
def main():
 output=[];seen=set()
 for coin in COINS:
  for hour in WINDOWS:
   period="TRAIN" if hour in TRAIN else "TEST" if hour in TEST else "VALIDATION"
   try:
    scenarios=evaluate_market(coin,hour)
    seen.update(scenarios)
    output.append((coin,hour,period,scenarios))
    if hour in ("0945","1045","1245"):
     print("SCAN",coin,hour,period,"strategies_filled",len(scenarios),flush=True)
   except Exception as e:
    print("ERROR",coin,hour,type(e).__name__,str(e),flush=True)
    output.append((coin,hour,period,{}))
 keys=sorted(seen)
 print("STRATEGIES",len(keys),"MARKETS",len(output),flush=True)
 agg={p:aggregate(output,keys,p) for p in ("TRAIN","TEST","VALIDATION")}
 ranked=[]
 for key in keys:
  tr=agg["TRAIN"][key]
  if tr["n"]<8 or tr["wins"]<6 or tr["net"]<=0:continue
  # Must beat all paper risk accounting, not cherry-pick only wins.
  te=agg["TEST"][key];va=agg["VALIDATION"][key]
  ranked.append((tr["net"],key,tr,te,va))
 ranked.sort(reverse=True)
 print("TRAIN_POSITIVE_N8_AND_6WINS",len(ranked))
 both=[r for r in ranked if r[3]["net"]>0 and r[3]["n"]>=3 and r[4]["net"]>0 and r[4]["n"]>=4]
 print("ALL_THREE_PERIOD_POSITIVE",len(both))
 for record in sorted(both,key=lambda a:a[2]["net"]+a[3]["net"]+a[4]["net"],reverse=True)[:24]:
  print("THREE",record,flush=True)
 for row in ranked[:20]:
  print("TOP_TRAIN",row,flush=True)
 export={
  "WARNING":"This is a systematic finite grid, not literally all possible algorithms; quotes are not exchange-verified fills. Outcome proxies near strike uncertain.",
  "universe":{"coins":COINS,"train":TRAIN,"test":TEST,"confirmation":VALID,
   "book_step_ms":200,"spot_native_cadence_differs_by_coin":True,
   "entry_s":[40,180],"shares_at_max_limit_budget_dollars":10,
   "targets_profit_per_contract_cents":TARGETS,
   "fixed_side":["YES","NO"],"limits_cents":LIMITS,
   "trajectory_filters":TRAJECTORY,"book_filters":BOOK,"timing_filters":TIME},
  "count_unique_scenarios_with_any_fill":len(keys),
  "train_eligible":len(ranked),"positive_all_three":len(both),
  "train_top50":[{"key":k,"train":tr,"test":te,"confirmation":va} for _,k,tr,te,va in ranked[:50]],
  "three_period_survivors":[{"key":k,"train":tr,"test":te,"confirmation":va} for _,k,tr,te,va in both],
  "per_market_counts":[{"coin":c,"window":h,"period":p,"num_scenarios":len(v)} for c,h,p,v in output],
 }
 path=F/"systematic_native200_results.json"
 path.write_text(json.dumps(export,indent=2)+"\n")
 # detailed scenario market outcomes only for top25 and three-period survivors.
 finalists={r[1] for r in ranked[:25]}|{r[1] for r in both}
 trace=[]
 for coin,h,p,scen in output:
  trace.append({"coin":coin,"window":h,"period":p,"trades":{k:scen[k] for k in finalists if k in scen}})
 (F/"systematic_native200_traces.json").write_text(json.dumps(trace,indent=2)+"\n")
 print("DONE_OUTPUTS",path,flush=True)
if __name__=="__main__":main()
