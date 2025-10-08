# MySQL connection config
import os
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "mysql+pymysql://root:password123@db/classdj")
SQLALCHEMY_TRACK_MODIFICATIONS = False


