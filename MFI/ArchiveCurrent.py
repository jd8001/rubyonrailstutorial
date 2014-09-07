import MFI
import urllib
import MySQLdb
from bs4 import BeautifulSoup
import time
import argparse
import datetime
import sys

#Parsing Args
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start", type=int,
                    help="Starting Percentage of analysis")
parser.add_argument("-e", "--end", type=int,
                    help="Ending Percentage of analysis")
parser.add_argument("-a", "--host",
                    help="Database host address")
parser.add_argument("-u", "--username",
                    help="Database User Name")
parser.add_argument("-p", "--password",
                    help="Database Password")
parser.add_argument("-d", "--database",
                    help="Using Database")
args = parser.parse_args()


#Connect to the database server
db = MySQLdb.connect(args.host, args.username, args.password, args.database)
c=db.cursor()

#Use the insert command
ActionString = "INSERT INTO main (ticker, cap, reteq, earnyield, rank, price) select ticker, cap, reteq, earnyield, rank, price from current;"

c.execute(ActionString)
db.commit()

#update the ADate value
now = datetime.datetime.now()
ActionString = "UPDATE main set ADate='" + now.strftime("%Y-%m-%d %H:%M") + "' WHERE ADate IS NULL;"
c.execute(ActionString)
db.commit()