import dbConfig
import pymongo
from misc_functions import *

def dashboard(location):
    connection=pymongo.MongoClient()
    db=connection.openmrs_aggregation
    db.authenticate(dbConfig.mongo_username,dbConfig.mongo_password)
    collection=db.aggregate
    data={}
    for entry in collection.find():
        if location=="all":
            data[entry["timestamp"].isoformat()]=entry
        else:
            data[entry["timestamp"].isoformat()]=entry[location]
        del entry["timestamp"]
        del entry["_id"]
    return data

def performance():
    connection=pymongo.MongoClient()
    db=connection.openmrs_aggregation
    db.authenticate(dbConfig.mongo_username,dbConfig.mongo_password)
    collection=db.performance
    data={}
    for entry in collection.find():
        data[entry["timestamp"].isoformat()]=entry
        del entry["timestamp"]
        del entry["_id"]
    return data

def report(start_date,end_date,location):
    connection=pymongo.MongoClient()
    db=connection.openmrs_aggregation
    db.authenticate(dbConfig.mongo_username,dbConfig.mongo_password)
    collection=db.patients
    data={'patient_source':{},'start_art':{},'enrolled':{},'ever_on_art':{},'currently_on_art':{},'eligible_no_art':{},'on_cotrimoxazole':{}}
    # Go through each patient to compute numbers.
    for p in collection.find():
        #print p
        if (p["location"]==location or location=="all") and "date" in p.keys() and p["date"]:
            
            group_number=group(p)
            if p["date"]>start_date and p["date"]<end_date:
                insert(data,'patient_source',None,group_number,text=p['patient_source'])
            if "first_art_start_date" in p.keys():
                if p["first_art_start_date"]>start_date and p["first_art_start_date"]<end_date:
                    insert(data,'start_art',None,group_number,text=p["who_stage_f"])
            if p["date"]<end_date:
                insert(data,'enrolled',None,group_number)
                if "first_art_start_date" in p.keys() and p["first_art_start_date"]<end_date:
                    insert(data,'ever_on_art',None,group_number)
                if p["on_art"] and "current_regimen_start_date" in p.keys() and p["current_regimen_start_date"]<end_date:                
                    #if pregnant
                    if pregnant(p,end_date):
                        insert(data,'currently_on_art',None,group_number,text="Pregnant")
                    else:
                        insert(data,'currently_on_art',None,group_number,text="All Others")
                if p["eligible_for_art"] and not p["on_art"]:
                    insert(data,"eligible_no_art",None,group_number)
                if p["on_cotrimoxazole"]:
                    insert(data,"on_cotrimoxazole",None,group_number)
    return data

def pregnant(p,end_date):
    if p["pregnancy"]==0:
        return False
    else:
        for date in p["pregnancy"]:
            date_diff=end_date-date
            if date_diff.days<9*30: #9 months
                return True
    return False
if __name__=="__main__":
    import datetime

    print report(datetime.datetime.now()-datetime.timedelta(days=365*100),datetime.datetime.now(),"all")

