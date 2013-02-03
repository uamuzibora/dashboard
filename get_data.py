import dbConfig
import pymongo

def get_data(data_requested):
    connection=pymongo.MongoClient()
    db=connection.openmrs_aggregation
    db.authenticate(dbConfig.mongo_username,dbConfig.mongo_password)
    collection=db.aggregate
    data={}
    for entry in collection.find():
        if data_requested=="all":
            data[entry["timestamp"].isoformat()]=entry
        else:
            print entry["timestamp"]
            data[entry["timestamp"].isoformat()]=entry[data_requested]
        del entry["timestamp"]
        del entry["_id"]

            

    return data


if __name__=="__main__":
    print get_data("all")
