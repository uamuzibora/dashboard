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
from misc_functions import *
def db_connect():
    """
    Retunrs a connection to the database
    """
    
    return dbs.DB(user=login,password=password,database=mch_database,host=host,driver="mysql")




# Define the data we need to get 
# run through all patients and construct master dictionary with all needed data
# Categorize
# Write to mongodb


# Want age and sex for evryone

db=db_connect()
data={} # Master directory with all patient information



# Three kinds of observation datatypes

#  Multiple text 
#multiple_text={"who_stage_f":5356,"who_stage_l":5356,"patient_source":6245,"reason_to_follow_up":6281}
#which={"who_stage_f":"first","who_stage_l":"last","patient_source":"first","reason_to_follow_up":"last"}
# Multiple numeric
#multiple_numeric={"cd4_count":5497}
#Boolean
#boolean_sql={"eligible_for_art":"select patient_id from patient where patient_id in (select distinct(person_id) from obs where concept_id=5356 and (value_coded=1206 or value_coded=1207) and voided=0) or patient_id in (select distinct(person_id) from obs where concept_id=5497 and value_numeric<350 and voided=0)","hiv_positive_date":"select distinct(person_id) as patient_id from obs where obs.concept_id=6259","art_eligible_date":"select distinct(person_id) as patient_id from obs where obs.concept_id=6260","on_art":"select patient_id from (select start_date,patient_id from orders where discontinued=0 and voided=0 group by start_date,patient_id ) as s order by start_date","followed_up":"select patient_id from encounter where form_id=4 and voided=0","on_cotrimoxazole":"select distinct(person_id) as patient_id from obs where concept_id=6113"}


# Get all patient ids and other needed fields from the patient table
res=db.query_dict('Select patient_id from patient where voided=0 order by patient_id')
for r in res:
    data[r['patient_id']]={}
# Get enrollment date and location for each patient
print "enrollment date"
res=db.query_dict("Select "+'patient_id,date_enrolled,location_id '+" from patient_program where program_id in (4,5) and voided=0")

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

#By age +-18
#Women Enrolled(%completed 4 return vists)
#Deliveries registered
#Children enrolled(% of children registerd to registerd, delivery vist)
#Percentage of hiv-positive on treetment hiv:1040->703, 6356
#IPT1-3 malaria, all in maternal profile 6331,6332,6333

#ITN (bednet 6336)
#missing data: missing hiv screenen if 1040=1118
#             : missing tb screen 5965=6103
#             : missing malaria screening 32=1118
#             : missing fam history of hypertenion 6388 not answered

#Malaria positive 32=703
#TB positive 5965=6102
#VDRL positive 299 = 1228

#mother vita 6396
#reciving haart at 6539 in postnatal vist %
#children immunisation 5585
#6352 children art % of hiv positive women



boolean_concepts={"IPT1":6331,"IPT2":6332,"IPT3":6333,"hypertension":6388,"mother_vit_a":6396,"haart_postnatal":6539,"mother_art":6356,"child_immunisation":5585,"child_art":6352}
coded={"hiv":1040,"tb":5965,"malaria":32,"vdrl":229}

#Number of return visits:
res=db.query_dict("SELECT patient_id,count(encounter_id) as count from encounter where form_id=6 group by patient_id")
for r in res:
    data[r["patient_id"]]["number_of_visits"]=r["count"]
#delivery:
res=db.query_dict("SELECT patient_id,count(encounter_id) as count from encounter where form_id=8 group by patient_id")
for r in res:
    data[r["patient_id"]]["delivery_visit"]=1

for key in boolean_concepts.keys():
    res=db.query_dict("SELECT person_id,value_numeric from obs where concept_id=%s and voided=0",boolean_concepts[key])
    for r in res:
        data[r['person_id']][key]=r['value_numeric']

for field in coded.keys():
    res=db.query_dict("SELECT obs.person_id,obs.value_coded from obs where obs.concept_id = %s and obs.voided=0", coded[field])
    temp={}
    lookup={}
    for r in res:
        data[r['person_id']][field]=r['value_coded']

#Clean up 
for d in data.keys():
    for f in boolean_concepts.keys():
        if f not in data[d].keys():
            data[d][f]="Missing"
    for f in coded.keys()+["location"]:
         if f not in data[d].keys():       
             data[d][f]="Missing"
    if "number_of_visits" not in data[d].keys():
        data[d]["number_of_visits"]=0
    if "delivery_visit" not in data[d].keys():
        data[d]["delivery_visit"]=0

print "Finished getting data. ",len(data.keys())
print data
# Calculate Aggregates:
t=datetime.datetime.now()
aggregate={"mothers":{},"children":{},"four_visits":0,"deliveries":0,"hiv_positive":[0,0],"on_hiv_treatment":0,"IPT1-3":[0,0],"ITN":[0,0],"missing_hiv":0,"missing_tb":0,"missing_malaria":0,"missing_hypertension":0,"malaria_positive":0,"tb_positive":0,"vdrl_positive":0,"mother_vit_a":0,"receiving_haart_postnatal":0,"child_immunisation":0,"child_art":0, "timestamp": t}
age_limit=18

for patient in data.keys():
    p=data[patient]
    if p["age"]>18:
        group_number=1
    else:
        group_number=0
    if p["age"]<5:
        child=True
    else:
        child=False
    #print p
    location=p["location"]

    if child:
        if location in aggregate["children"].keys():
            aggregate["children"][location]+=1
        else:
            aggregate["children"][location]=1
    else:#mother
        if location in aggregate["mothers"].keys():
            aggregate["mothers"][location][group_number]+=1
        else:
            aggregate["mothers"][location]=[0,0]
            aggregate["mothers"][location][group_number]+=1

        if p["number_of_visits"]>=4:
            aggregate["four_visits"]+=1
        if p["delivery_visit"]:
            aggregate["deliveries"]+=1
        if p["hiv"]==703:
            aggregate["hiv_positive"][group_number]+=1
        if p["mother_art"]==1:
            aggregate["on_hiv_treatment"]+=1
        if p["IPT1"]==1 and p["IPT2"]==1 and p["IPT3"]==1:
            aggregate["IPT1-3"][group_number]+=1
        if p["hiv"]==1118 or p["hiv"]=="Missing":
            aggregate["missing_hiv"]+=1
        if p["tb"]==6103 or p["hiv"]=="Missing":
            aggregate["missing_tb"]+=1
        if p["malaria"]==1118 or p["hiv"]=="Missing":
            aggregate["missing_malaria"]+=1
        if p["hypertension"]=="Missing":
            aggregate["missing_hypertension"]+=1
        if p["malaria"]==703:
            aggregate["malaria_positive"]+=1
        if p["vdrl"]==1228:
            aggregate["vdrl_positive"]+=1
        if p["mother_vit_a"]==1:
            aggregate["mother_vit_a"]+=1
        if p["haart_postnatal"]==1:
            aggregate["receiving_haart_postnatal"]+=1
        if p["child_immunisation"]==1:
            aggregate["child_immunisation"]+=1
        if p["child_art"]==1:
            aggregate["child_art"]+=1
print "Finished Calculating"

connection=pymongo.MongoClient()
db_mongo=connection.mch_aggregation
db_mongo.authenticate(mongo_username,mongo_password)
collection=db_mongo.patients
collection.remove()
for pid in data.keys():
    collection.insert(data[pid])
 
collection=db_mongo.aggregate
print aggregate
latest_date=datetime.datetime(1970,12,12)
for entry in collection.find():
    if entry["timestamp"]>latest_date:
        latest_date=entry["timestamp"]

if (aggregate["timestamp"]-latest_date).seconds>5*3600:# Have at least 12 hours between each update
    collection.insert(aggregate)
else:
    print "already have a recent record"

# Performance review

aggregate={"timestamp": t}

form_names={5:"Maternal Profile",6:"Maternal Clinic Visit",8:"Maternal Delivery Visit",9:"Maternal Postnatal Visit",10:"Child Immunisations",11:"Child Profile",12:"Child Clinic Visit"}
for form_id in form_names.keys():
    res=db.query_dict("select username,count(encounter_id) as number from encounter inner join users on encounter.creator=user_id where form_id=%s and encounter_datetime>date_sub(curdate(),interval 7 day) group by encounter.creator",form_id)
    form={}
    for r in res:
        name=" ".join(r['username'].split('.'))
        form[name]=r['number']
    aggregate[form_names[form_id]]=form



collection=db_mongo.performance 
print aggregate
latest_date=datetime.datetime(1970,12,12)
for entry in collection.find():
    if entry["timestamp"]>latest_date:
        latest_date=entry["timestamp"]
if (aggregate["timestamp"]-latest_date).seconds>5*3600:# Have at least 12 hours between each update
    collection.insert(aggregate)
else:
    print "already have a recent record"

