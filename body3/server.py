from multiprocessing import connection
import pymongo
import certifi
from datetime import *

ca =  certifi.where()

connection = pymongo.MongoClient("mongodb+srv://user1:honeycake123@cluster0.zd1jh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    tlsCAFile=ca)

db = connection.database_main
childcol = db["child"]
vaxcol = db["vaccine"]

def upcomingStartingDate(child):
    dob = child["dob"]
    yetVaccines = child["yetVaccines"]
    earliestStartDate = datetime(9999, 12, 31)
    for vid in yetVaccines:
        vaccine = vaxcol.find_one({"vid":vid})
        startDate = dob + timedelta(days=vaccine["date_start"])
        if startDate < earliestStartDate:
            earliestStartDate = startDate
    child["upcomingStartDate"] = earliestStartDate
    childcol.update_one({"cid": child["cid"]}, {"$set": {"upcomingStartDate": earliestStartDate}})
    child = childcol.find_one({"cid":child["cid"]})

def upcomingMidDate(child):
    dob = child["dob"]
    yetVaccines = child["yetVaccines"]
    dueVaccines = child["dueVaccines"]
    earliestMidDate = datetime(9999, 12, 31)
    for vid in dueVaccines:
        vaccine = vaxcol.find_one({"vid":vid})
        timeDifference = timedelta(days=vaccine["date_end"])-timedelta(days=vaccine["date_start"])
        midDate = dob + timedelta(days=vaccine["date_start"]) + timeDifference/2
        if midDate < earliestMidDate:
            earliestMidDate = midDate
    if earliestMidDate > datetime.today():
        child["upcomingMidDate"] = earliestMidDate
        childcol.update_one({"cid": child["cid"]}, {"$set": {"upcomingMidDate": earliestMidDate}})
        return
    earliestMidDate = datetime(9999, 12, 31)
    for vid in yetVaccines:
        vaccine = vaxcol.find_one({"vid":vid})
        timeDifference = timedelta(days=vaccine["date_end"])-timedelta(days=vaccine["date_start"])
        midDate = dob + timedelta(days=vaccine["date_start"]) + timeDifference/2
        if midDate < earliestMidDate:
            earliestMidDate = midDate
    child["upcomingMidDate"] = earliestMidDate
    childcol.update_one({"cid": child["cid"]}, {"$set": {"upcomingMidDate": earliestMidDate}})
    child = childcol.find_one({"cid":child["cid"]})

def upcomingEndDate(child):
    dob = child["dob"]
    dueVaccines = child["dueVaccines"]
    earliestEndDate = datetime(9999, 12, 31)
    for vid in dueVaccines:
        vaccine = vaxcol.find_one({"vid":vid})
        endDate = dob + timedelta(days=vaccine["date_end"])
        if endDate < earliestEndDate:
            earliestEndDate = endDate
    child["upcomingEndDate"] = earliestEndDate
    childcol.update_one({"cid": child["cid"]}, {"$set": {"upcomingEndDate": earliestEndDate}})
    child = childcol.find_one({"cid":child["cid"]})

def startDateScenario(child):
    dob = child["dob"]
    presentDay = datetime.today()
    yetVaccines = child["yetVaccines"]
    dueVaccines = child["dueVaccines"]
    startedList = []
    for vid in yetVaccines:
        vaccine = vaxcol.find_one({"vid":vid})
        if presentDay > dob + timedelta(days=vaccine["date_start"]):
            startedList.append(vid)
    for vid in startedList:
        yetVaccines.remove(vid)
    dueVaccines.extend(startedList)
    childcol.update_one({"cid": child["cid"]}, {"$set": {"dueVaccines": dueVaccines, "yetVaccines": yetVaccines}})
    child = childcol.find_one({"cid":child["cid"]})

def endDateScenario(child):
    dob = child["dob"]
    presentDay = datetime.today()
    dueVaccines = child["dueVaccines"]
    warningList = child["warningList"]
    for vid in dueVaccines:
        vaccine = vaxcol.find_one({"vid":vid})
        if presentDay > dob + timedelta(days=vaccine["date_end"]):
            warningList.append(vid)
    childcol.update_one({"cid": child["cid"]}, {"$set": {"warningList": warningList}})
    child = childcol.find_one({"cid":child["cid"]})

def warningListCheck(child):
    warningList = child["warningList"]
    dueVaccines = child["dueVaccines"]
    delList = []
    for vid in warningList:
        if vid not in dueVaccines:
            delList.append(vid)
    for vid in delList:
        warningList.remove(vid)
    childcol.update_one({"cid": child["cid"]}, {"$set": {"warningList": warningList}})
    child = childcol.find_one({"cid":child["cid"]})

def write_mail(child):
    print("yooo")

def write_warning_mail(child):
    print("hoooo")

def main():
    presentDate = datetime.today()
    isWarningDay = False
    if presentDate.day%6 == 0:
        isWarningDay = True
    for child in childcol.find():
        if presentDate > child["upcomingStartDate"]:
            startDateScenario(child)
            child = childcol.find_one({"cid":child["cid"]})
            upcomingStartingDate(child)
            child = childcol.find_one({"cid":child["cid"]})
            write_mail(child)
        if presentDate > child["upcomingMidDate"]:
            upcomingMidDate(child)
            child = childcol.find_one({"cid":child["cid"]})
            write_mail(child)
        if presentDate > child["upcomingEndDate"]:
            endDateScenario(child)
            child = childcol.find_one({"cid":child["cid"]})
            upcomingEndDate(child)
            child = childcol.find_one({"cid":child["cid"]})
            write_mail(child)
        if isWarningDay:
            warningListCheck(child)
            child = childcol.find_one({"cid":child["cid"]})
            if child["warningList"] != []:
                write_warning_mail(child)

        

main()