#!/usr/bin/env python3
"""Repeat the ORIGINAL exhaustive 24,570-rule 200ms search on NEW strictly vetted
CLOSED Kalshi 15m crypto tapes, safely separated from funded/paper systems.

Usage:
  python -B discover_new_closed_windows.py --date 2026-10-18 --start 2030 --end 2100

Date, start and end are America/New_York market OPENING clocks, end inclusive.
Creates a new unique directory under HANDOFF/DISCOVERY_RUNS; refuses overwrite.
This does NOT implement the separate data-first hypothesis miner; see
DISCOVERY_ENGINE_FROM_ZERO.md. NEVER sends trading orders.
"""
import argparse,datetime as dt,gzip,json,hashlib,collections,pathlib,sys,os,time,inspect
from zoneinfo import ZoneInfo
import numpy as np
import requests

HANDOFF=pathlib.Path(__file__).resolve().parents[1]
STUDY=HANDOFF/"engine"
sys.path.insert(0,str(STUDY))
import prepare_native200_grids as prep
import systematic_native200_scan as grid
import stress_native200_candidates as stress
COINS=("ETH","HYPE","BNB","XRP","NEAR","ZEC","DOGE")
FIXED=("YES_55_10_MOVE10_ALIGNED_SPREAD_LE2C_FIRST_180S",
       "NO_40_10_MOVE10_OPPOSED_SPREAD_LE2C_FIRST_180S",
       "NO_35_15_MOVE10_OPPOSED_SPREAD_LE2C_FIRST_180S",
       "YES_60_15_MOVE10_ALIGNED_SPREAD_LE2C_FIRST_180S")
ET=ZoneInfo("America/New_York")
def stamp(h):
 if len(h)!=4 or not h.isdigit() or int(h[:2])>23 or int(h[2:]) not in (0,15,30,45):raise ValueError("HHMM must be quarter hour")
 return int(h[:2])*4+int(h[2:])//15
def sha(path):
 x=hashlib.sha256()
 with path.open("rb") as f:
  for buf in iter(lambda:f.read(1048576),b""):x.update(buf)
 return x.hexdigest()
def files_for(c,tm):
 paths=list((prep.root(c)/"live_stream").glob(
  c.lower()+"_"+tm.strftime("%Y%m%d")+"_"+tm.strftime("%H%M")+"_"+tm.strftime("%Z")+"_*.jsonl.gz"))
 return paths
def raw_integrity(c,tm):
 st=int(tm.timestamp()*1000)
 en=st+900000
 endtm=tm+dt.timedelta(minutes=15)
 ticker="KX"+c+"15M-"+endtm.strftime("%y%b%d%H%M").upper()+"-"+endtm.strftime("%M")
 files=files_for(c,tm-dt.timedelta(minutes=15))
 current=files_for(c,tm)
 o={"coin":c,"hour":tm.strftime("%H%M"),"ticker":ticker,
    "start_ms":st,"prev_file_count":len(files),"curr_file_count":len(current)}
 if len(files)!=1 or len(current)!=1:
  o["integrity_error"]="SOURCE_FILE_COUNT_NOT_EXACTLY_ONE";return o
 o["source_sha256"]={p.name:sha(p) for p in files+current}
 count=collections.Counter();prev_ms=None;metadata_ms=None;strike=None
 first=None;last=None
 for i,fp in enumerate(files+current):
  try:
   with gzip.open(fp,"rt") as f:
    for line in f:
     try:r=json.loads(line)
     except Exception:count["bad_json"]+=1;continue
     ms=int(r.get("received_ms") or 0)
     if ms<=0:continue
     if prev_ms is not None:
      if ms<prev_ms-250:count["backstep_gt250ms"]+=1
      if ms-prev_ms>5000 and ms>=st:count["gap_gt5s"]+=1
     prev_ms=ms
     if i==1:
      first=ms if first is None else min(first,ms)
      last=ms if last is None else max(last,ms)
     kind=r.get("kind")
     if i==1 and kind in ("SEQUENCE_GAP","DISCONNECT_OR_FAILURE","STREAM_ERROR","CONNECTED","SOCKET_CONNECT_ATTEMPT"):count[kind]+=1
     if kind=="TARGET_METADATA" and r.get("ticker")==ticker and r.get("floor_strike") is not None and metadata_ms is None:
      metadata_ms=ms;strike=float(r["floor_strike"])
     elif kind=="TARGET_METADATA" and r.get("ticker")==ticker and r.get("floor_strike") is not None and strike is not None and abs(float(r["floor_strike"])-strike)>1e-8:count["strike_changed"]+=1
  except Exception as exc:o["integrity_error"]=type(exc).__name__+":"+str(exc)[:160]
 o.update(counts=dict(count),
          metadata_lag_s=round((metadata_ms-st)/1000,3) if metadata_ms is not None else None,
          source_first_s=round((first-st)/1000,3) if first else None,
          source_last_s=round((last-st)/1000,3) if last else None,
          strike=strike)
 return o
def quality(raw,q):
 flags=[]
 if raw.get("integrity_error") or q.get("error"):flags.append("RAW_OR_RECONSTRUCTION_FAILURE")
 if raw.get("prev_file_count")!=1 or raw.get("curr_file_count")!=1:flags.append("SOURCE_FILE_MISSING_OR_DUPLICATE")
 if raw.get("metadata_lag_s") is None or raw.get("metadata_lag_s")>40:flags.append("NO_EARLY_CONTEMPORANEOUS_MARKET_STRIKE")
 if q.get("first_valid_sec") is None or q["first_valid_sec"]>50:flags.append("NO_EARLY_CAUSAL_VALID_QUOTE")
 if q.get("coverage_pct",0)<80:flags.append("LESS_THAN80PCT_FRESH_QUOTE_COVERAGE")
 if q.get("count",{}).get("invalidate_clock",0):flags.append("RECONSTRUCTED_CROSS_FILE_CLOCK_INVALIDATIONS")
 for key,n in raw.get("counts",{}).items():
  if n and key in ("bad_json","backstep_gt250ms","gap_gt5s","SEQUENCE_GAP","DISCONNECT_OR_FAILURE","STREAM_ERROR","CONNECTED","SOCKET_CONNECT_ATTEMPT","strike_changed"):
   flags.append("RAW_"+key)
 if q.get("count",{}).get("invalidate_gap",0):flags.append("PREPARE_INVALIDATED_FOR_GAP")
 return flags
def score(xs):
 known=[float(v["pnl"]) for v in xs if v.get("pnl") is not None]
 return {"trades":len(xs),"known":len(known),"positive":sum(x>0 for x in known),
         "negative":sum(x<=0 for x in known),"unresolved":len(xs)-len(known),
         "net":round(sum(known),4),"worst":round(min(known),4) if known else None}
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--date",required=True,help="ISO local Eastern date YYYY-MM-DD")
 ap.add_argument("--start",required=True,help="First market OPEN, Eastern HHMM")
 ap.add_argument("--end",required=True,help="Last market OPEN inclusive, Eastern HHMM")
 a=ap.parse_args()
 date=dt.date.fromisoformat(a.date);lo,hi=stamp(a.start),stamp(a.end)
 if hi<lo or hi-lo>95:ap.error("must run one date and <=96 complete quarter hours")
 opening=[dt.datetime(date.year,date.month,date.day,k//4,(k%4)*15,tzinfo=ET) for k in range(lo,hi+1)]
 last_close=opening[-1]+dt.timedelta(minutes=15)
 if last_close.astimezone(dt.timezone.utc).timestamp()+10>time.time():
  ap.error("REFUSING_OPEN_OR_JUST_CLOSED_MARKET: wait at least 10 seconds AFTER last market closes")
 uid=date.isoformat()+"_"+a.start+"_"+a.end
 OUT=HANDOFF/"DISCOVERY_RUNS"/uid
 if OUT.exists():ap.error("OUTPUT_ALREADY_EXISTS_DO_NOT_OVERWRITE: "+str(OUT))
 OUT.mkdir(parents=True)
 PREP=OUT/"grids";PREP.mkdir()
 prep.OUT=PREP
 # The archived original preparer hardcodes Oct 2026 in two DATE/OUTPUT
 # expressions. Adapt those TWO expressions only at runtime so future
 # dates remain correct; do NOT edit the original study file or its features.
 original=inspect.getsource(prep.prepare)
 dt_pat="datetime.datetime(2026,10,day,"
 path_pat='pth=OUT/(c+"_"+h+".npz" if day==18 else c+"_202610"+str(day)+"_"+h+".npz")'
 if original.count(dt_pat)!=1 or original.count(path_pat)!=1:
  ap.error("PREPARER_VERSION_DRIFT: manually inspect the original source; no unsafe adaptation")
 adapted=original.replace(dt_pat,"datetime.datetime(RUN_YEAR,RUN_MONTH,day,").replace(
  path_pat,'pth=OUT/(c+"_"+RUN_YMD+"_"+h+".npz")')
 scope=dict(prep.__dict__,RUN_YEAR=date.year,RUN_MONTH=date.month,RUN_YMD=date.strftime("%Y%m%d"),OUT=PREP)
 exec(adapted,scope)
 prepare_any_date=scope["prepare"]
 observations=[]
 for market in opening:
  for c in COINS:
   rr=raw_integrity(c,market)
   try:pp=prepare_any_date(c,market.strftime("%H%M"),day=date.day)
   except Exception as ex:pp={"error":type(ex).__name__+":"+str(ex)[:140]}
   flags=quality(rr,pp)
   rec={**rr,"prepared":pp,"quality_flags":flags,
        "accepted":not flags,"official_result":None}
   observations.append(rec)
   print("QA",c,market.strftime("%H%M"),"coverage",pp.get("coverage_pct"),
         "status","PASS" if not flags else ",".join(flags),flush=True)
 (OUT/"quality_report.json").write_text(json.dumps(observations,indent=2,default=str)+"\n")
 passing=[x for x in observations if x["accepted"]]
 http=requests.Session();verified=[]
 for r in passing:
  try:
   response=http.get("https://api.elections.kalshi.com/trade-api/v2/markets/"+r["ticker"],timeout=(3,7))
   mar=response.json().get("market") or {}
   if response.status_code==200 and mar.get("ticker")==r["ticker"] and mar.get("status")=="finalized" and mar.get("result") in ("yes","no"):
    r["official_result"]=mar["result"];verified.append(r)
   else:r["settlement_error"]={"http":response.status_code,"status":mar.get("status"),"result":mar.get("result")}
  except Exception as ex:r["settlement_error"]=type(ex).__name__+":"+str(ex)[:100]
 (OUT/"quality_report.json").write_text(json.dumps(observations,indent=2,default=str)+"\n")
 grid.ORACLES={(r["coin"],r["hour"]):{"status":"CONFIDENT","proxy_yes_wins":r["official_result"]=="yes"} for r in verified}
 def unpack(c,h):
  file=PREP/(c+"_"+date.strftime("%Y%m%d")+"_"+h+".npz")
  with np.load(file,allow_pickle=False) as z:return {key:z[key] for key in ("ask","bid","bps","bid_avg","bid_worst","sizes")}
 grid.unpack=unpack
 sets=[]
 for idx,t in enumerate(opening):
  # Chronological splits are fixed by clock-time BEFORE rules get scored.
  for rec in verified:
   if rec["hour"]!=t.strftime("%H%M"):continue
   try:
    states=grid.evaluate_market(rec["coin"],rec["hour"])
    sets.append({"coin":rec["coin"],"hour":rec["hour"],"clock_group":idx,
                 "official":rec["official_result"],"scenarios":states})
    print("FULLGRID",rec["coin"],rec["hour"],"rule_buys",len(states),flush=True)
   except Exception as ex:
    print("FULLGRID_ERROR",rec["coin"],rec["hour"],type(ex).__name__,str(ex)[:100],flush=True)
 with (OUT/"scenarios_by_market.jsonl").open("w") as f:
  for r in sets:f.write(json.dumps(r,separators=(",",":"),default=str)+"\n")
 # Do NOT market a chosen training/holdout rule as independently validated.
 periods={"TRAIN":set(range(0,max(1,(len(opening)+1)//3))),
          "TEST":set(range(max(1,(len(opening)+1)//3),max(2,(2*len(opening)+1)//3))),
          "HOLDOUT":set(range(max(2,(2*len(opening)+1)//3),len(opening)))}
 allrule=collections.defaultdict(lambda:collections.defaultdict(list))
 allopens=collections.defaultdict(set)
 for rec in sets:
  period=next((k for k,v in periods.items() if rec["clock_group"] in v),"UNASSIGNED")
  for key,value in rec["scenarios"].items():
   allrule[key][period].append(value)
   allopens[key].add(rec["hour"])
 assessments=[]
 for key,z in allrule.items():
  scores={p:score(z.get(p,[])) for p in periods}
  assessment={"rule":key,"distinct_market_openings":len(allopens[key]),**scores}
  assessments.append(assessment)
 train_sorted=sorted(assessments,key=lambda x:(x["TRAIN"]["net"],x["TRAIN"]["positive"]),reverse=True)
 separately_confirmed=[x for x in train_sorted if x["TRAIN"]["trades"]>=8 and x["TRAIN"]["positive"]>=6 and x["TRAIN"]["net"]>0 and
  x["TEST"]["trades"]>=3 and x["TEST"]["net"]>0 and x["HOLDOUT"]["trades"]>=4 and x["HOLDOUT"]["net"]>0 and x["distinct_market_openings"]>=3]
 # More than 24k rules selected among correlated same-window coins; treat ALL selected as exploratory until a genuinely new forward block.
 heldout_len=len(periods["HOLDOUT"]);distinct_len=len(opening)
 expected_benchmark={}
 for key in FIXED:
  vals=[(r["scenarios"][key],r["hour"],r["coin"]) for r in sets if key in r["scenarios"]]
  allx=[x for x,_,_ in vals]
  summary=score(allx)
  summary["distinct_start_times"]=len({h for _,h,_ in vals})
  summary["by_coin"]={c:score([x for x,h,coin in vals if coin==c]) for c in COINS}
  summary["stress"]={}
  for name,delay,slip in stress.STRESSES:
   if name=="BASE2S":continue
   x=[]
   for r in verified:
    book=unpack(r["coin"],r["hour"])
    oracle={"status":"CONFIDENT","proxy_yes_wins":r["official_result"]=="yes"}
    t=stress.eval_one(book,stress.parse(key),delay,slip,oracle)
    if t is not None:x.append({"pnl":t[0]})
   summary["stress"][name]=score(x)
  expected_benchmark[key]=summary
 report={"scope":uid,"remark":"Read-only original finite-grid DISCOVERY on brand-new CLOSED markets; selection on the used holdout invalidates it as independent validation for chosen rules.",
   "theoretical_combinations":24570,"raw_coin_windows":len(observations),"strict_qa_count":len(passing),
   "official_verified":len(verified),"grid_scanned":len(sets),"found_with_trade":len(allrule),
   "chrono_partitions":{p:sorted(v) for p,v in periods.items()},
   "frozen_baselines":expected_benchmark,
   "top_train_exploratory":train_sorted[:100],"three_period_exploratory_count":len(separately_confirmed),
   "three_period_exploratory":separately_confirmed[:100],
   "statistical_warning":"Multiple testing, correlated coins and small sample. No funded fill validation. No auto-promotions."}
 (OUT/"research_summary.json").write_text(json.dumps(report,indent=2,default=str)+"\n")
 print("FINAL",json.dumps({"sample":uid,"raw":len(observations),"qa_pass":len(passing),
   "official":len(verified),"scanned":len(sets),"baseline":{k:v["net"] for k,v in expected_benchmark.items()},"folder":str(OUT)}),flush=True)
if __name__=="__main__":main()
