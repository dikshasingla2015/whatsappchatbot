from pymongo import MongoClient
import datetime

client=MongoClient("mongodb+srv://diksha:diksha@cluster0-uncer.mongodb.net/test?retryWrites=true&w=majority")
db=client.get_database("userdata")
records=db.get_collection("userdata")

def insertdata(userdata):
    count=records.insert_one(userdata)
    print(count.inserted_id)
    print(records.count_documents({}))

def updatedata():
    count=records.update_one({
        "name":"diksha"
    },{
        "$set":{
            "name":"diksha",
            "address":"haryana"
        }
    })
    print(count.modified_count)

def get_time():
    x = datetime.datetime.now()
    time=x.strftime("%x") +" "+x.strftime("%X")
    return time
