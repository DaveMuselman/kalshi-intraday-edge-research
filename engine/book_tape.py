#!/usr/bin/env python3
"""Convert read-only ETH WebSocket archives into time-causal 200ms L2 replay tape.
No network, no credentials, no Hunter imports. No fictional quotes.
Records freshness, sequence continuity, quote ladder for buying/selling 5 shares.
"""
import sys,os,glob,gzip,json,math,collections,pathlib,datetime as dt,decimal,argparse
D=decimal.Decimal
DIR=pathlib.Path(__file__).resolve().parent
STEP_MS=200
def tick(s):
 return int((D(str(s))*D("10000")).to_integral_value())
def px(t):
 return D(int(t))/D(10000)
def good_qty(v):
 return float(D(str(v)))
class OrderBook:
 def __init__(self):
  self.sides={"yes":{},"no":{}}
  self.has_snapshot=False
  self.last_sequence=None
  self.invalid=False
  self.invalid_updates=0
  self.last_update_ms=0
 def snapshot(self,msg,ms):
  sides={}
  for side in ("yes","no"):
   target={}
   for p,q in msg.get(side+"_dollars_fp",[]):
    key=tick(p); qty=good_qty(q)
    if key and qty>0:target[key]=qty
   sides[side]=target
  self.sides=sides
  self.has_snapshot=True
  self.invalid=False
  self.last_update_ms=ms
 def delta(self,msg,ms):
  if not self.has_snapshot or self.invalid:return
  side=msg.get("side")
  if side not in self.sides:
   self.invalid=True;self.invalid_updates+=1;return
  p=tick(msg.get("price_dollars",0))
  q=good_qty(msg.get("delta_fp",0))
  old=self.sides[side].get(p,0)
  value=round(old+q,6)
  if value<-.0001:
   self.invalid=True;self.invalid_updates+=1
   return
  if value<=.000001:self.sides[side].pop(p,None)
  else:self.sides[side][p]=value
  self.last_update_ms=ms
 def best(self,side):
  x=self.sides[side]
  if not x:return None
  return max(x)
 def level_qty(self,side,price):
  return self.sides[side].get(price,0)
 def sweep(self,side,action,qty):
  """Return (weighted_value, levels, avg_price, total_top_depth).
  action=BUY: consumes opposing side's bids, transformed $1-bid
  action=SELL: consumes same side's bids.
  Invalid or insufficient depth returns None, NEVER a fabricated fill.
  """
  if not self.has_snapshot or self.invalid or qty<=0:return None
  source=self.sides["no" if side=="YES" and action=="BUY" else
                    "yes" if side=="NO" and action=="BUY" else side.lower()]
  if not source:return None
  remaining=qty;levels=[];value=D("0")
  for tick_value in sorted(source,reverse=True):
   depth=source[tick_value]
   if depth<=0:continue
   take=min(remaining,depth)
   p=(D(10000-tick_value) if action=="BUY" else D(tick_value))/D(10000)
   if p<=0 or p>=1:continue
   value+=D(str(take))*p
   levels.append([str(p),round(take,4),round(depth,4)])
   remaining-=take
   if remaining<1e-6:break
  if remaining>1e-6:return None
  return (round(float(value),6),levels,round(float(value/D(str(qty))),6))
 def view(self,coin_price,coin_age,ms,market_target,target_available_ms):
  if not self.has_snapshot or self.invalid:return None
  if coin_price is None or coin_age is None or coin_age>1500:return None
  if market_target is None or target_available_ms is None or ms<target_available_ms:return None
  if not self.sides["yes"] or not self.sides["no"]:return None
  y=max(self.sides["yes"]);n=max(self.sides["no"])
  yi=self.sides["yes"][y];ni=self.sides["no"][n]
  if not (0<y<10000 and 0<n<10000):return None
  # ETH contract uses ~730 USD units, but ETH-derived features expect
  # ~2450 USD. Preserve *basis-point magnitude* causally by normalizing
  # ETH live price and strike with the already known live market strike.
  # This is experimental cross-asset transfer, NOT identical ETH behavior.
  scale=2450.0/float(market_target)
  return {"ms":ms,"eth":coin_price*scale,"target":market_target*scale,
          "eth_usd":coin_price,"eth_strike_usd":market_target,
          "normalization_scale":scale,"eth_age_ms":coin_age,
          "book_age_ms":ms-self.last_update_ms,
          "y_bid":y/10000,"y_ask":(10000-n)/10000,
          "n_bid":n/10000,"n_ask":(10000-y)/10000,
          "y_bid_depth":yi,"n_bid_depth":ni,
          "yes_levels":[[p,round(q,4)] for p,q in sorted(self.sides["yes"].items(),reverse=True)[:60]],
          "no_levels":[[p,round(q,4)] for p,q in sorted(self.sides["no"].items(),reverse=True)[:60]],
          "buy5_yes":self.sweep("YES","BUY",5),
          "sell5_yes":self.sweep("YES","SELL",5),
          "buy5_no":self.sweep("NO","BUY",5),
          "sell5_no":self.sweep("NO","SELL",5)}

def iter_archive(paths):
 for path in sorted(paths):
  try:
   with gzip.open(path,"rt",encoding="utf-8") as f:
    for line in f:
     if not line.strip():continue
     try:
      obj=json.loads(line)
      yield obj
     except json.JSONDecodeError:continue
  except (EOFError,OSError) as ex:
   print("INCOMPLETE_ARCHIVE",path.name,type(ex).__name__,file=sys.stderr)
def derive_window_ticker(outname):
 # extract NY time from eth_<YYYYMMDD>_<HHMM>_EDT or EST
 pieces=outname.split("_")
 if len(pieces)<4:raise ValueError("Unexpected archive name")
 ymd,hm,zone=pieces[1],pieces[2],pieces[3]
 from zoneinfo import ZoneInfo
 eastern=dt.datetime.strptime(ymd+hm,"%Y%m%d%H%M").replace(tzinfo=ZoneInfo("America/New_York"))
 close=eastern+dt.timedelta(minutes=15)
 return "KXETH15M-"+close.strftime("%y%b%d%H%M").upper()+"-"+close.strftime("%M")
def build(files,out,origin=None):
 # files should be from one 15min window; file session segments lexically sorted
 objs=iter_archive(files)
 first=next(objs,None)
 if first is None:return None
 allobjs=__import__("itertools").chain([first],objs)
 ticker=derive_window_ticker((origin or files[0]).name)
 from zoneinfo import ZoneInfo
 parts=(origin or files[0]).name.split("_")
 start=int(dt.datetime.strptime(parts[1]+parts[2],"%Y%m%d%H%M").replace(
   tzinfo=ZoneInfo("America/New_York")).timestamp()*1000)
 close=start+900000
 book=OrderBook();eth=None;eth_received=None;target=None;target_at=None
 # When multiple capture runs overlap the same window, choose last received per timestamp
 # and require new snapshot after any reconnect and any sequence discontinuity.
 sids={};bad_seq=0;restarts=0;book_snapshots=0;updates=0;cf=0
 processed=0;valid=0;first_good=None;last_good=None
 timestamp_regressions=0;maximum_clock_backstep_ms=0
 grid=start+STEP_MS
 previous_ms=None
 samples=[]
 last_file_start=None
 def maybe_sample(limit):
  nonlocal grid,valid,first_good,last_good
  while grid<=limit and grid<=close and len(samples)<=4501:
   current=book.view(eth,None if eth_received is None else grid-eth_received,grid,target,target_at)
   if current:
    samples.append(current)
    valid+=1
    if first_good is None:first_good=grid
    last_good=grid
   else:
    reason=("no_snapshot" if not book.has_snapshot else
      "book_invalid" if book.invalid else
      "eth_unavailable" if eth is None else
      "eth_stale" if eth_received is None or grid-eth_received>1500 else
      "target_unavailable" if target is None or target_at is None else
      "target_not_yet_observed" if grid<target_at else
      "empty_book" if not book.sides["yes"] or not book.sides["no"] else
      "out_of_range_top_bid" if book.best("yes")>=10000 or book.best("no")>=10000 else
      "other")
    samples.append({"ms":grid,"invalid":True,"reason":reason})
   grid+=STEP_MS
 for obj in allobjs:
  if obj.get("kind")=="ROTATION":continue
  if obj.get("kind")=="TARGET_METADATA":
   if obj.get("ticker")==ticker and obj.get("floor_strike") is not None:
    target=float(obj["floor_strike"])
    v=int(obj["received_ms"])
    target_at=v if target_at is None else min(target_at,v)
   continue
  if obj.get("kind") in ("SEQUENCE_GAP","DISCONNECT_OR_FAILURE","STREAM_ERROR"):
   bad_seq+=1;book.invalid=True;continue
  if obj.get("kind") in ("CONNECTED","SOCKET_CONNECT_ATTEMPT"):
   book.invalid=True;book.has_snapshot=False;restarts+=1
   continue
  if obj.get("kind")!="RECEIVED":continue
  msg=obj.get("payload") or {};m=msg.get("msg") or {};kind=msg.get("type")
  ms=int(obj.get("received_ms") or 0)
  if ms<=0:continue
  if previous_ms is not None and ms<previous_ms:
   # Preserve Kalshi sequence/order when host clock makes a small backward
   # adjustment. Discarding one delta breaks all later book liquidity.
   step=previous_ms-ms
   timestamp_regressions+=1
   maximum_clock_backstep_ms=max(maximum_clock_backstep_ms,step)
   if step>250:
    bad_seq+=1
    book.invalid=True;book.has_snapshot=False
   ms=previous_ms
  if previous_ms is not None and ms-previous_ms>5000:
   book.invalid=True;book.has_snapshot=False
  # Read previous-window book snapshots to seed the new window at opening.
  maybe_sample(ms-1)
  previous_ms=ms
  sid=msg.get("sid");seq=msg.get("seq")
  if kind in ("orderbook_snapshot","orderbook_delta") and m.get("market_ticker")==ticker:
   if sid is not None and isinstance(seq,int):
    last=sids.get(sid)
    if last is not None and seq!=last+1:
     # sequence numbers are channel-wide, even when carrying next window;
     # use recorder's SEQUENCE_GAP event as source of true gap.
     pass
    sids[sid]=seq
   if kind=="orderbook_snapshot":
    book.snapshot(m,ms);book_snapshots+=1
   else:book.delta(m,ms);updates+=1
  elif kind in ("cfbenchmarks_value_5hz","cfbenchmarks_value"):
   if m.get("index_id")=="ETHUSD_RTI":
    reported=int(m.get("source_ts_ms") or ms)
    if reported>ms+3000:continue
    candidate=m.get("value_usd") or m.get("value")
    if candidate is not None:
     eth=float(candidate)
     eth_received=ms
     cf+=1
  processed+=1
 maybe_sample(close)
 eligible=(first_good is not None and first_good<=start+180000 and
           last_good is not None and last_good>=close-120000 and
           bad_seq==0 and book_snapshots>=1 and
           valid/max(1,len(samples))>=.80)
 output={"market":ticker,"window_start_ms":start,"window_close_ms":close,
        "sample_interval_ms":STEP_MS,"fully_covered":eligible,
        "eligibility_rule":">=80% valid 200ms samples; target known within 180s; valid until final 120s for early-flatten traders; no sequence gaps",
        "coverage_pct":round(valid/max(1,len(samples))*100,2),"first_good_ms":first_good,"last_good_ms":last_good,
        "target":target,"target_observed_ms":target_at,"snapshot_count":book_snapshots,
        "book_deltas":updates,"cf_points":cf,"disconnect_or_sequence_gaps":bad_seq,
        "receive_time_regressions":timestamp_regressions,
        "max_local_clock_backstep_ms":maximum_clock_backstep_ms,
        "processed_messages":processed,"raw_files":[str(x) for x in files],
        "critical_warning":"RESEARCH QUOTE-BASED EXECUTION; NO ACTUAL BROKER ORDER; RELY ONLY ON COMPLETE SNAPSHOT-AND-DELTA EPOCHS",
        "samples":samples}
 with gzip.open(out,"wt",encoding="utf-8",compresslevel=5) as f:
  json.dump(output,f,separators=(",",":"))
 print("BOOK_TAPE_DONE",json.dumps({k:v for k,v in output.items() if k!="samples"}),flush=True)
 return output
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--window",default=None,help="NY day+start HHMM e.g. 20261015_1645")
 args=ap.parse_args()
 src=DIR/"live_stream"
 files=sorted(src.glob("eth_*.jsonl.gz"))
 if args.window:files=[x for x in files if x.name.startswith("eth_"+args.window+"_")]
 else:
  if files:
   prefix="_".join(files[-1].name.split("_")[:4])
   files=[x for x in files if x.name.startswith(prefix+"_")]
 if not files:raise SystemExit("NO_ARCHIVES")
 origin=files[0]
 # Previous window records contain the future market's initial snapshot.
 # Without it we cannot know the initial full book from later deltas.
 from zoneinfo import ZoneInfo
 chunks=origin.name.split("_")
 eastern=dt.datetime.strptime(chunks[1]+chunks[2],"%Y%m%d%H%M").replace(tzinfo=ZoneInfo("America/New_York"))
 prior=eastern-dt.timedelta(minutes=15)
 prior_prefix="eth_"+prior.strftime("%Y%m%d_%H%M_%Z")+"_"
 warmup=[x for x in sorted(src.glob("eth_*.jsonl.gz")) if x.name.startswith(prior_prefix)]
 chunks=origin.name.split("_")
 key="_".join(chunks[:3])+"_"+chunks[3].split(".")[0]
 dest=DIR/("book_tape_"+key+".json.gz")
 build(warmup+files,dest,origin=origin)
if __name__=="__main__":main()
