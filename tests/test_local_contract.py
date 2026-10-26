import pyarrow as pa
import pytest
from deltalake import DeltaTable,write_deltalake
def test_schema_mismatch_rejected(tmp_path):
 p=str(tmp_path/'table'); write_deltalake(p,pa.table({'id':pa.array([1],type=pa.int64()),'name':['A']})); before=DeltaTable(p).version()
 with pytest.raises(Exception): write_deltalake(p,pa.table({'id':pa.array([2],type=pa.int64()),'name':['B'],'extra':[True]}),mode='append')
 dt=DeltaTable(p); assert dt.version()==before and dt.to_pyarrow_table().num_rows==1
