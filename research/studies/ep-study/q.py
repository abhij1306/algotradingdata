import os,sys
os.environ['DB_NAME']='hat_live'; os.environ['PGOPTIONS']='-c default_transaction_read_only=on'
from sqlalchemy import text
from app.database import engine
with engine.connect() as c:
    for r in c.execute(text(sys.argv[1])): print(r)
