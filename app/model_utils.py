#app/model_utils.py
from sqlalchemy import BigInteger
from sqlalchemy.dialects import sqlite

BigIntegerType = BigInteger()
BigIntegerType = BigIntegerType.with_variant(sqlite.INTEGER(), 'sqlite')
