import argparse
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
from deltalake import DeltaTable,write_deltalake
from lab.common import *
def compare():
 pq.write_table(events(),Path('parquet_baseline/events.parquet')); print('[PARQUET] rows=',pq.read_table('parquet_baseline/events.parquet').num_rows)
 if not exists(EVENTS): write_deltalake(EVENTS,events(),mode='overwrite',storage_options=OPTIONS)
 print('[DELTA] data files are Parquet plus _delta_log transaction metadata'); show(EVENTS)
def write_demo():
 ensure_bucket(); write_deltalake(EVENTS,events(),mode='overwrite',storage_options=OPTIONS); dt=DeltaTable(EVENTS,storage_options=OPTIONS); print('[WRITE] version=',dt.version(),'rows=',dt.to_pyarrow_table().num_rows); print('[SCHEMA]',dt.schema().json())
def schema_test():
 dt=DeltaTable(EVENTS,storage_options=OPTIONS); v=dt.version(); n=dt.to_pyarrow_table().num_rows
 bad=pa.table({'event_id':['BAD'],'customer_id':['C999'],'amount':pa.array([100],type=pa.int64()),'event_date':['2026-10-04'],'unexpected_column':['bad']})
 try: write_deltalake(EVENTS,bad,mode='append',storage_options=OPTIONS); print('[SCHEMA] UNEXPECTED ACCEPT')
 except Exception as e: print(f'[SCHEMA] REJECTED {type(e).__name__}: {e}')
 after=DeltaTable(EVENTS,storage_options=OPTIONS); print(f'[SCHEMA] version_before={v} version_after={after.version()} rows_before={n} rows_after={after.to_pyarrow_table().num_rows}')
def travel():
 write_deltalake(EVENTS,events(),mode='overwrite',storage_options=OPTIONS); v=DeltaTable(EVENTS,storage_options=OPTIONS).version()
 new=pa.table({'event_id':['E004'],'customer_id':['C003'],'amount':pa.array([7000],type=pa.int64()),'event_date':['2026-10-03']}); write_deltalake(EVENTS,new,mode='append',storage_options=OPTIONS)
 cur=DeltaTable(EVENTS,storage_options=OPTIONS); print(f'[TIME-TRAVEL] old_version={v} current_version={cur.version()}'); show(EVENTS,v); show(EVENTS); print('[NOTE] reading history is not rollback')
def merge():
 src=pa.table({'event_id':['E002','E004'],'customer_id':['C002','C003'],'amount':pa.array([20000,7000],type=pa.int64()),'event_date':['2026-10-01','2026-10-03']})
 dt=DeltaTable(EVENTS,storage_options=OPTIONS); metrics=dt.merge(src,predicate='target.event_id = source.event_id',source_alias='source',target_alias='target').when_matched_update_all().when_not_matched_insert_all().execute(); print('[MERGE]',metrics); show(EVENTS)
def scd1():
 src=pa.table({'customer_id':['C001','C003'],'name':['Ayu Putri','Citra'],'city':['Sidoarjo','Surabaya']}); dt=DeltaTable(DIM1,storage_options=OPTIONS)
 print('[SCD1]',dt.merge(src,predicate='target.customer_id = source.customer_id',source_alias='source',target_alias='target').when_matched_update_all().when_not_matched_insert_all().execute()); show(DIM1)
def scd2():
 dt=DeltaTable(DIM2,storage_options=OPTIONS); src=[{'customer_id':'C001','name':'Ayu Putri','city':'Sidoarjo'},{'customer_id':'C003','name':'Citra','city':'Surabaya'}]
 current={r['customer_id']:r for r in dt.to_pyarrow_table().to_pylist() if r['is_current']}; changes=[r for r in src if r['customer_id'] not in current or current[r['customer_id']]['name']!=r['name'] or current[r['customer_id']]['city']!=r['city']]
 for r in changes:
  if r['customer_id'] in current: dt.update(updates={'valid_to':"'2026-10-04'",'is_current':'false'},predicate=f"customer_id = '{r['customer_id']}' AND is_current = true")
 if changes:
  rows=[{**r,'valid_from':'2026-10-05','valid_to':'9999-12-31','is_current':True} for r in changes]; write_deltalake(DIM2,pa.Table.from_pylist(rows),mode='append',storage_options=OPTIONS)
 print(f'[SCD2] changed_or_new={len(changes)}'); show(DIM2)
def failure():
 dt=DeltaTable(EVENTS,storage_options=OPTIONS); v=dt.version(); n=dt.to_pyarrow_table().num_rows
 bad=pa.table({'event_id':['FAIL'],'customer_id':['CFAIL'],'amount':pa.array(['not-int'],type=pa.string()),'event_date':['2026-10-04']})
 try: write_deltalake(EVENTS,bad,mode='append',storage_options=OPTIONS)
 except Exception as e: print(f'[FAILURE] expected rejection {type(e).__name__}: {e}')
 after=DeltaTable(EVENTS,storage_options=OPTIONS); print(f'[FAILURE] version_before={v} version_after={after.version()} rows_before={n} rows_after={after.to_pyarrow_table().num_rows}'); assert v==after.version() and n==after.to_pyarrow_table().num_rows; print('[FAILURE] PROVED no new committed version')
def main():
 p=argparse.ArgumentParser(); p.add_argument('action',choices=['init','reset','compare','write','schema-test','time-travel','merge','scd1','scd2','failure']); a=p.parse_args().action
 if a=='init': ensure_bucket()
 elif a=='reset': reset()
 elif a=='compare': compare()
 elif a=='write': write_demo()
 elif a=='schema-test': schema_test()
 elif a=='time-travel': travel()
 elif a=='merge': merge()
 elif a=='scd1': scd1()
 elif a=='scd2': scd2()
 elif a=='failure': failure()
if __name__=='__main__': main()
