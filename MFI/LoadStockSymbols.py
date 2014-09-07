import MFI

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
parser.add_argument("-f", "--file",
                    help="CSV input file")
parser.add_argument("-t", "--table",
                    help="Table to load stock symbols into")

args = parser.parse_args()

#Connect to the database server
db = MySQLdb.connect(args.host, args.username, args.password, args.database)

MFI.Populate_Stock_Symbols(db, args.table, args.file)

