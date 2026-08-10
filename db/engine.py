from sqlalchemy import MetaData, create_engine
from dotenv import load_dotenv
import os


load_dotenv('../.env')
DB_URL = os.getenv('DB_URL')


metadata = MetaData()
engine = create_engine(DB_URL, echo=False)






