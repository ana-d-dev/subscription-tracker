from sqlalchemy import MetaData, create_engine
from config.settings import DB_URL

metadata = MetaData()
engine = create_engine(DB_URL, echo=False)






