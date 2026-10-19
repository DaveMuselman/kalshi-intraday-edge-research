#!/usr/bin/env python3
"""Prepare causal 200ms contract-book grids from recorded WebSocket streams.
Coin samples: ETH/XRP/DOGE ~200ms, BNB/HYPE/NEAR/ZEC ~1sec; holding
last observed coin value at intermediate ticks, with a <=1500ms freshness
requirement. NOT all coins have 200ms underlying measurements.
Book is reconstructed from warmup previous-window snapshot+all subsequent
deltas, invalidated on errors or discontinuities; all observations as-of-tick.
No trading API, no paper strategy access or changes.
"""
import json,gzip,sys,math,datetime,os
import numpy as np
from pathlib import Path
from zoneinfo import ZoneInfo
from collections import Counter
ROOT=Path(os.environ.get("KALSHI_ARCHIVE_ROOT", str(Path(__file__).resolve().parents[1]/"data")))
F=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(__file__).resolve().parent))
from book_tape import OrderBook
COINS=("ETH","HYPE","BNB","XRP","NEAR","ZEC","DOGE")
HOURS=("0800","0815","0830","0845","0900","0915","0930","0945","1000","1015","1030","1045",
       "1100","1115","1130","1145","1200","1215","1230","1245")
# Q is the fixed whole share count for each buy limit at worst price+fee.
LIMITS=np.arange(20,81,5,dtype=np.int32)
SIZES=np.asarray([int((10-.001)/(p/100+.07*(p/100)*(1-p/100))) for p in LIMITS],dtype=int)
TICK_S=0.2
N=4500
OUT=F/"prepared_native200"
OUT.mkdir(exist_ok=True)
def root(c):
 return ROOT/c
def quotes(levels):
    """Return for all target sizes a top-2c weighted bid average and lowest
    reached bid, or NaN for not enough actual displayed volume."""
    av=np.full(len(SIZES),np.nan,dtype=np.float32)
    worst=np.full(len(SIZES),np.nan,dtype=np.float32)
    if not levels:return av,worst
    first=max(levels)
    allpx=[];allqty=[]
    for price in sorted(levels,reverse=True):
        if price<first-200:break # $0.02 book walking max
        qty=float(levels[price])
        if qty<=0:continue
        allpx.append(price/10000.)
        allqty.append(qty)
    if not allpx:return av,worst
    cumq=np.cumsum(allqty);cumval=np.cumsum(np.asarray(allpx)*np.asarray(allqty))
    for j,n in enumerate(SIZES):
        ix=int(np.searchsorted(cumq,n,side="left"))
        if ix>=len(cumq):continue
        prevq=float(cumq[ix-1]) if ix else 0.
        prevval=float(cumval[ix-1]) if ix else 0.
        v=prevval+(n-prevq)*allpx[ix]
        av[j]=v/n
        worst[j]=allpx[ix]
    return av,worst
def prepare(c,h,day=18):
    st=datetime.datetime(2026,10,day,int(h[:2]),int(h[2:]),tzinfo=ZoneInfo("America/New_York"))
    start=int(st.timestamp()*1000);end=start+900000
    clos=st+datetime.timedelta(minutes=15)
    ticker="KX"+c+"15M-"+clos.strftime("%y%b%d%H%M").upper()+"-"+clos.strftime("%M")
    prevdt=st-datetime.timedelta(minutes=15)
    files=[]
    for objdt in (prevdt,st):
        date=objdt.strftime('%Y%m%d');hour=objdt.strftime('%H%M');zone=objdt.strftime('%Z')
        found=list((root(c)/"live_stream").glob(f"{c.lower()}_{date}_{hour}_{zone}_*.jsonl.gz"))
        if len(found)!=1:raise ValueError("MISSING_ARCHIVE "+c+" "+date+"_"+hour)
        files+=found
    ask=np.full((2,N),np.nan,np.float32);bid=np.full((2,N),np.nan,np.float32)
    bps=np.full(N,np.nan,np.float32);depth=np.full((2,N),np.nan,np.float32)
    bid_av=np.full((2,N,len(SIZES)),np.nan,np.float32)
    bid_worst=np.full((2,N,len(SIZES)),np.nan,np.float32)
    ob=OrderBook();strike=None;strikeat=None;coin=None;coinat=None;lastms=0;tick=start+200
    counts=Counter();valid=0;first_valid=None
    def take(tm):
        nonlocal valid,first_valid
        ix=(tm-start)//200-1
        if not (0<=ix<N):return
        if (strike is None or strikeat is None or strikeat>tm
            or coin is None or coinat is None or tm-coinat>1500
            or not ob.has_snapshot or ob.invalid
            or not ob.sides["yes"] or not ob.sides["no"]
            or tm-ob.last_update_ms>1800 or tm<ob.last_update_ms):return
        y=max(ob.sides["yes"]);n=max(ob.sides["no"])
        if y<=0 or n<=0 or y>=10000 or n>=10000:return
        yb=y/10000.;nb=n/10000.
        if yb+nb>=1 or yb<.01 or nb<.01:return
        bid[0,ix]=yb;bid[1,ix]=nb
        ask[0,ix]=1-nb;ask[1,ix]=1-yb
        depth[0,ix]=float(ob.sides["yes"][y])
        depth[1,ix]=float(ob.sides["no"][n])
        bps[ix]=10000*(coin/strike-1)
        for side,i in (("yes",0),("no",1)):
            bid_av[i,ix],bid_worst[i,ix]=quotes(ob.sides[side])
        valid+=1
        if first_valid is None:first_valid=tm
    for f in files:
        with gzip.open(f,"rt") as inp:
            for line in inp:
                try:o=json.loads(line)
                except ValueError:counts["bad_json"]+=1;continue
                ms=int(o.get("received_ms") or 0)
                if ms<=0:continue
                if ms<lastms:
                    counts["clock_backstep"]+=1
                    if lastms-ms>250:
                        ob.invalid=True;ob.has_snapshot=False;counts["invalidate_clock"]+=1
                    ms=lastms
                if ms-lastms>5000 and lastms and ms>=start:
                    ob.invalid=True;ob.has_snapshot=False;counts["invalidate_gap"]+=1
                while tick<ms and tick<end:
                    take(tick);tick+=200
                lastms=ms
                kind=o.get("kind")
                if kind=="TARGET_METADATA" and o.get("ticker")==ticker and o.get("floor_strike") is not None and strike is None:
                    strike=float(o["floor_strike"]);strikeat=ms
                if kind in ("SEQUENCE_GAP","DISCONNECT_OR_FAILURE","STREAM_ERROR","CONNECTED","SOCKET_CONNECT_ATTEMPT"):
                    ob.invalid=True;ob.has_snapshot=False
                    counts["invalidate_"+str(kind)]+=1
                    continue
                if kind!="RECEIVED":continue
                p=o.get("payload") or {};msg=p.get("msg") or {};typ=p.get("type")
                if typ=="orderbook_snapshot" and msg.get("market_ticker")==ticker:
                    ob.snapshot(msg,ms);counts["snapshots"]+=1
                elif typ=="orderbook_delta" and msg.get("market_ticker")==ticker:
                    ob.delta(msg,ms);counts["deltas"]+=1
                elif typ in ("cfbenchmarks_value_5hz","cfbenchmarks_value") and msg.get("index_id")==c+"USD_RTI":
                    # Use newest observed spot, prioritizing 5Hz.
                    v=msg.get("value_usd") or msg.get("value")
                    if v is not None:coin=float(v);coinat=ms;counts["coin_ticks"]+=1
                if tick>=end:break
        if tick>=end:break
    while tick<end:take(tick);tick+=200
    # IMPORTANT: save only recorded top-2c book quantities, no lookahead.
    pth=OUT/(c+"_"+h+".npz" if day==18 else c+"_202610"+str(day)+"_"+h+".npz")
    np.savez_compressed(pth,ask=ask,bid=bid,bps=bps,depth=depth,
       bid_avg=bid_av,bid_worst=bid_worst,limits=LIMITS,sizes=SIZES)
    return {"coin":c,"hour":h,"ticker":ticker,"file":str(pth),"first_valid_sec":(first_valid-start)/1000 if first_valid else None,
       "200ms_rows":N,"valid_rows":valid,"coverage_pct":round(valid/N*100,2),
       "snapshot_count":counts["snapshots"],"deltas":counts["deltas"],
       "coin_ticks":counts["coin_ticks"],"invalid_updates":ob.invalid_updates,
       "count":dict(counts)}
if __name__=="__main__":
 summary=[]
 for c in COINS:
  for h in HOURS:
   try:
    rec=prepare(c,h);summary.append(rec)
    if h in ("0945","1045","1245"):
     print("PREP",c,h,"coverage",rec["coverage_pct"],"first",rec["first_valid_sec"],
       "snap",rec["snapshot_count"],"invalid",rec["invalid_updates"],flush=True)
   except Exception as ex:
    print("FAIL",c,h,str(ex),flush=True)
    summary.append({"coin":c,"hour":h,"error":str(ex)})
   tmp=OUT/"index.json.tmp";tmp.write_text(json.dumps(summary,indent=2)+"\n");os.replace(tmp,OUT/"index.json")
 print("COMPLETE",len(summary),"PREPARED",sum("error" not in s for s in summary),flush=True)
