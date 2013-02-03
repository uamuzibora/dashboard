import pymongo
import numpy
from scipy import stats
from datetime import date
import datetime
import sys
import time,calendar
#importing dbConfig
import db as dbs
from dbConfig import *

def db_connect():
    """
    Retunrs a connection to the database
    """
    
    return dbs.DB(user=login,password=password,database=database,host=host,driver="mysql")


def group(patient):
    group_number=-2

    if patient['age']>age_limit:
        group_number=2
    elif patient['age']<=age_limit:
        group_number=0
    
    if patient['sex']=="F":
        group_number+=1
    elif patient["sex"]=="M":
        pass
    else:
        group_number+=-4
    return group_number


# Define the data we need to get 
# run through all patients and construct master dictionary with all needed data
# Categorize
# Write to mongodb


# Want age and sex for evryone

db=db_connect()
data={} # Master directory with all patient information



# Three kinds of observation datatypes

#  Multiple text 
multiple_text={"who_stage_f":5356,"who_stage_l":5356,"patient_source":6245,"reason_to_follow_up":6281}
which={"who_stage_f":"first","who_stage_l":"last","patient_source":"first","reason_to_follow_up":"last"}
# Multiple numeric
multiple_numeric={"cd4_count":5497}
#Boolean
boolean_sql={"eligible_for_art":"select patient_id from patient where patient_id in (select distinct(person_id) from obs where concept_id=5356 and (value_coded=1206 or value_coded=1207) and voided=0) or patient_id in (select distinct(person_id) from obs where concept_id=5497 and value_numeric<350 and voided=0)","on_art":"select patient_id from (select start_date,patient_id from orders where discontinued=0 and voided=0 group by start_date,patient_id ) as s order by start_date","followed_up":"select patient_id from encounter where form_id=4 and voided=0"}


# Get all patient ids and other needed fields from the patient table
res=db.query_dict('Select patient_id from patient where voided=0 order by patient_id')
for r in res:
    data[r['patient_id']]={}



# Get enrollment date and location for each patient
print "enrollment date"
res=db.query_dict("Select "+'patient_id,date_enrolled,location_id '+" from patient_program where program_id=1 and voided=0")
for r in res:
    if "date_enrolled" in r:
        data[r['patient_id']]['date']=r['date_enrolled'];
    else:
        data[r['patient_id']]['date']=None
    if r["location_id"]:
        location=db.query_dict("Select name from location where location_id=%s",r["location_id"])
        data[r['patient_id']]["location"]=location[0]["name"]
    else:
        data[r['patient_id']]["location"]="Missing"
print "age and sex"
# Get age and sex from person table
res=db.query_dict("Select person_id,gender,birthdate from person where voided=0 order by person_id")
for r in res:
    if r['person_id'] in data.keys():
        data[r['person_id']]["sex"]=r["gender"];
        if r["birthdate"]:
            data[r['person_id']]["age"]=int((datetime.date.today()-r["birthdate"]).days/365)
        else:
            data[r['person_id']]["age"]=None
print "inactive_reason"
# Get Inactive reason
res=db.query_dict("SELECT obs.person_id,obs.value_coded from obs where obs.concept_id = 6153 and obs.voided=0")
temp={}
lookup={}
for r in res:
    concept=r['value_coded']
    if concept in lookup.keys():
        text=lookup[concept]
    else:
        lo=db.query_dict("SELECT name from concept_name where concept_id=%s",concept)
        text=lo[0]['name']
        lookup[concept]=text
    data[r['person_id']]["inactive_reason"]=text
print "status"
# Get Status
res=db.query_dict("SELECT obs.person_id from obs where obs.concept_id = 6153 and voided=0")
patients_with_observation=[]
for r in res:
    patients_with_observation.append(r['person_id'])
for key in data.keys():
    if key in patients_with_observation:
        data[key]["status"]=1
    else:
        data[key]["status"]=0
print "status"
# Get Willing to Return
res=db.query_dict("SELECT obs.person_id from obs where obs.concept_id = 6286 and voided=0")
patients_with_observation=[]
for r in res:
    patients_with_observation.append(r['person_id'])
for key in data.keys():
    if key in patients_with_observation:
        data[key]["willing_to_return"]=1
    else:
        data[key]["willing_to_return"]=0

print "numeric_multiple"
#Get information from obs tables for multiple numeric
for field in multiple_numeric.keys():

    res=db.query_dict("SELECT obs.person_id,obs.value_numeric,enc.encounter_datetime from obs LEFT JOIN encounter as enc on enc.encounter_id=obs.encounter_id where obs.concept_id = %s and obs.voided=0 and enc.voided=0",multiple_numeric[field])

    temp={}
    for r in res:
        if r['person_id'] in temp.keys():
            temp[r['person_id']][r['encounter_datetime']]=r['value_numeric']
        else:
            temp[r['person_id']]={r['encounter_datetime']:r['value_numeric']}
    for key in temp.keys():
        avg=numpy.average(temp[key].values())
        sorted_keys=sorted(temp[key].keys())
        t=[]
        y=[]
        for i in sorted_keys:
            d=i-sorted_keys[0]
            t.append(d.total_seconds()/(2548800)) # Seconds per month
            y.append(temp[key][i])
            slope, intercept, r_value, p_value, std_err = stats.linregress(t,y)
            if slope!=slope:
                slope=None
        data[key][field]={'Mean':avg,'First':temp[key][sorted_keys[0]], 'Last':temp[key][sorted_keys[-1]],'Regression':slope}; 

print "Multiple text"
#Deal with multiple_text 
       
for field in multiple_text.keys():
    res=db.query_dict("SELECT obs.person_id,obs.value_coded,enc.encounter_datetime from obs JOIN encounter as enc on enc.encounter_id=obs.encounter_id where obs.concept_id = %s and obs.voided=0 order by enc.encounter_datetime",multiple_text[field])

    temp={}
    lookup={}
    for r in res:
        if r['person_id'] in temp.keys():
            temp[r['person_id']][r['encounter_datetime']]=r['value_coded']
        else:
            temp[r['person_id']]={r['encounter_datetime']:r['value_coded']}
    for key in temp.keys():
        dates=sorted(temp[key].keys())
        if which[field]=="last":
            date=dates[-1]
        elif which[field]=="first":
            date=dates[0]
        concept=temp[key][date]
        if concept in lookup.keys():
            text=lookup[concept]
        else:
            lo=db.query_dict("SELECT name from concept_name where concept_id=%s",concept)
            text=lo[0]['name']
            lookup[concept]=text
        data[key][field]=text
print "Boolean sql"
#Boolean sql
for field in boolean_sql.keys():
    res=db.query_dict(boolean_sql[field])
    patients_in_query=[]
    for r in res:
        patients_in_query.append(r['patient_id'])
    for p in data.keys():
        if p in patients_in_query:
            data[p][field]=1
        else:
            data[p][field]=0
    

#Clean up 
for d in data:
    for f in multiple_numeric.keys():
        if f not in data[d].keys():
            data[d][f]={'Mean':None,'First':None, 'Last':None,'Regression':None};
    for f in multiple_text.keys()+["location"]:
         if f not in data[d].keys():       
             data[d][f]="Missing"
             

print "Finished getting data. ",len(data.keys())

# Calculate Aggregates:

age_limit=14
aggregate={"enrolled":{},"patient_source":{},"eligible_no_art":{},"willing_to_return":{},"on_art_who":{},"inactive_reason":{},"reason_to_follow_up":{},"followed_up":{},"first_who":{},"first_cd4":{},"timestamp":datetime.datetime.now()}

def insert(aggregate,main_key,location,group_number,text=None):
    if text:
        if text in aggregate[main_key].keys():
            if location in aggregate[main_key][text].keys():
                aggregate[main_key][text][location][group_number]+=1
            else:
                aggregate[main_key][text][location]=[0,0,0,0]
                aggregate[main_key][text][location][group_number]+=1
        else:
            aggregate[main_key][text]={location:[0,0,0,0]}
            aggregate[main_key][text][location][group_number]+=1
    else:
        if location in aggregate[main_key].keys():
            aggregate[main_key][location][group_number]+=1
        else:
            aggregate[main_key][location]=[0,0,0,0]
            aggregate[main_key][location][group_number]+=1
            
        

for patient in data.keys():
    p=data[patient]
    group_number=group(data[patient])
    #print p
    location=p["location"]
    if group_number>=0:
        insert(aggregate,'enrolled',location,group_number)
 
        for field in data[patient].keys():
            # This is where we define what we want
            if field=="patient_source":
                source=data[patient][field]
                insert(aggregate,'patient_source',location,group_number,text=source)
            if field=="eligible_for_art":
                if p[field] and not p["on_art"]:
                    insert(aggregate,"eligible_no_art",location,group_number)
            if field=="followed_up" and p[field]:
                insert(aggregate,"followed_up",location,group_number)
            if field=="willing_to_return" and p[field]:
                insert(aggregate,"willing_to_return",location,group_number)
            if field=="on_art" and p["on_art"]:
                who_stage=p['who_stage_l']
                insert(aggregate,"on_art_who",location,group_number,text=who_stage)
            if field=="who_stage_f":
                who_stage=p['who_stage_f']
                insert(aggregate,"first_who",location,group_number,text=who_stage)
            if field=="cd4_count":
                cd4=p[field]['First']
                c_number="Missing"
                if cd4:
                    if cd4<350:
                        c_number="<350"
                    elif cd4>350:
                        c_number=">350"
                insert(aggregate,"first_cd4",location,group_number,text=c_number)
            if field=="inactive_reason":
                reason=p[field]
                insert(aggregate,"inactive_reason",location,group_number,text=reason)
            if field=="reason_to_follow_up":
                reason=p[field]
                insert(aggregate,"reason_to_follow_up",location,group_number,text=reason)
print "Finished Calculating"

connection=pymongo.MongoClient()
db=connection.openmrs_aggregation
collection=db.aggregate
print aggregate
latest_date=datetime.datetime(1970,12,12)
for entry in collection.find():
    if entry["timestamp"]>latest_date:
        latest_date=entry["timestamp"]

if (aggregate["timestamp"]-latest_date).seconds>12*3600:# Have at least 12 hours between each update
    collection.insert(aggregate)
else:
    print "already have a recent record"





