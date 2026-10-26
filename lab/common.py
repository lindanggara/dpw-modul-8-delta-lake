import os
import boto3
import pyarrow as pa
from deltalake import DeltaTable, write_deltalake
ENDPOINT=os.getenv('MINIO_ENDPOINT','http://127.0.0.1:9000')
ACCESS=os.getenv('MINIO_ACCESS_KEY','dpw8admin')
SECRET=os.getenv('MINIO_SECRET_KEY','dpw8secret123')
BUCKET=os.getenv('MINIO_BUCKET','dpw8-lakehouse')
REGION='us-east-1'
EVENTS=f's3://{BUCKET}/events'; DIM1=f's3://{BUCKET}/customer_dim_type1'; DIM2=f's3://{BUCKET}/customer_dim_type2'
OPTIONS={'AWS_ACCESS_KEY_ID':ACCESS,'AWS_SECRET_ACCESS_KEY':SECRET,'AWS_ENDPOINT_URL':ENDPOINT,'AWS_REGION':REGION,'AWS_ALLOW_HTTP':'true','allow_http':'true','virtual_hosted_style_request':'false'}
def ensure_bucket():
 c=boto3.client('s3',endpoint_url=ENDPOINT,aws_access_key_id=ACCESS,aws_secret_access_key=SECRET,region_name=REGION)
 if BUCKET not in [b['Name'] for b in c.list_buckets().get('Buckets',[])]: c.create_bucket(Bucket=BUCKET)
 print(f'[MINIO] endpoint={ENDPOINT} bucket={BUCKET} ready')
def events():
 return pa.table({'event_id':pa.array(['E001','E002','E003'],type=pa.string()),'customer_id':pa.array(['C001','C002','C001'],type=pa.string()),'amount':pa.array([12000,18000,9000],type=pa.int64()),'event_date':pa.array(['2026-10-01','2026-10-01','2026-10-02'],type=pa.string())})
def exists(uri):
 try: DeltaTable(uri,storage_options=OPTIONS); return True
 except Exception: return False
def show(uri,version=None):
 dt=DeltaTable(uri,storage_options=OPTIONS) if version is None else DeltaTable(uri,version=version,storage_options=OPTIONS)
 print(f'[DELTA] uri={uri} version={dt.version()} rows={dt.to_pyarrow_table().num_rows}')
 print(dt.to_pyarrow_table().to_pydict()); return dt
def reset():
 ensure_bucket(); write_deltalake(EVENTS,events(),mode='overwrite',storage_options=OPTIONS)
 d1=pa.table({'customer_id':['C001','C002'],'name':['Ayu','Bima'],'city':['Surabaya','Malang']})
 d2=pa.table({'customer_id':['C001','C002'],'name':['Ayu','Bima'],'city':['Surabaya','Malang'],'valid_from':['2026-01-01','2026-01-01'],'valid_to':['9999-12-31','9999-12-31'],'is_current':[True,True]})
 write_deltalake(DIM1,d1,mode='overwrite',storage_options=OPTIONS); write_deltalake(DIM2,d2,mode='overwrite',storage_options=OPTIONS)
 print('[RESET] event and SCD tables restored')
