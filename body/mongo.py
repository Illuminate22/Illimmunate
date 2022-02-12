import pymongo
import certifi

ca = certifi.where()

connection = pymongo.MongoClient("mongodb+srv://user1:honeycake123@cluster0.zd1jh.mongodb.net/database_main?retryWrites=true&w=majority", tlsCAFile=ca)
db = connection["database_main"]
childcol = db["child"]
vaxcol = db["vaccine"]

