from datetime import *
import pymongo
import certifi

ca = certifi.where()

connection = pymongo.MongoClient("mongodb+srv://user1:honeycake123@cluster0.zd1jh.mongodb.net/database_main?retryWrites=true&w=majority", tlsCAFile=ca)
db = connection["database_main"]
vaxcol = db["vaccine"]

class Vaccines:
    vaxlist = []
    def __init__(self, vid, name, date_start, date_end, info):
        dic = {"vid": vid,"name" :name,"date_start" : date_start.days,"date_end" : date_end.days,"info" : info}
        Vaccines.vaxlist.append(dic)
        self.dic = dic
    def __str__(self):
        return self["name"]
    def validVaccines(dob, childVaxList = vaxlist):
        presentDay = datetime.today()
        dueVaccines, overVaccines, yetVaccines = [], [], []
        for vaccine in childVaxList:
            if timedelta(days=vaccine["date_start"]) + dob < presentDay and timedelta(days=vaccine["date_end"]) + dob > presentDay or timedelta(days=vaccine["date_end"]) + dob == presentDay:
                dueVaccines.append(vaccine)
            elif timedelta(days=vaccine["date_start"]) + dob > presentDay:
                overVaccines.append(vaccine)
            else:
                yetVaccines.append(vaccine)
        return dueVaccines, overVaccines, yetVaccines
    def vaccineDbUpdate():
        for vaccine in Vaccines.vaxlist:
            vaxcol.insert_one(vaccine)

opv0 = Vaccines("opv0", "OPV-0", timedelta(days = 0), timedelta(days = 15), None)
opv1 = Vaccines("opv1", "OPV-1", timedelta(weeks = 5), timedelta(weeks = 6), None)
opv2 = Vaccines("opv2", "OPV-2", timedelta(weeks = 9), timedelta(weeks = 10), None)
opv3 = Vaccines("opv3", "OPV-3", timedelta(weeks = 13), timedelta(weeks = 14), None)
ptv1 = Vaccines("ptv1", "Pentavalent-1", timedelta(weeks = 5), timedelta(weeks = 6), None)
ptv2 = Vaccines("ptv2", "Pentavalent-2", timedelta(weeks = 9), timedelta(weeks = 10), None)
ptv3 = Vaccines("ptv3", "Pentavalent-3", timedelta(weeks = 13), timedelta(weeks = 14), None)
rtv1 = Vaccines("rtv1", "Rotavirus-1", timedelta(weeks = 5), timedelta(weeks = 6), None)
rtv2 = Vaccines("rtv2", "Rotavirus-2", timedelta(weeks = 9), timedelta(weeks = 10), None)
rtv3 = Vaccines("rtv3", "Rotavirus-3", timedelta(weeks = 13), timedelta(weeks = 14), None)
ipv1 = Vaccines("ipv1", "IPV-1", timedelta(weeks = 5), timedelta(weeks = 6), None)
ipv2 = Vaccines("ipv2", "IPV-2", timedelta(weeks = 13), timedelta(weeks = 14), None)
mr1 = Vaccines("mr1", "Measles-Rubella-1", timedelta(weeks = 4 * 9), timedelta(weeks = 4 * 12), None)
je1 = Vaccines("je1", "JE-1", timedelta(weeks = 4 * 9), timedelta(weeks = 4 * 12), None)
va1 = Vaccines("va1", "Vitamin A-1", timedelta(weeks = 4 * 9), timedelta(weeks = 4 * 12), None)
dpt1 = Vaccines("dpt1", "DPT booster-1", timedelta(weeks = 4 * 16), timedelta(weeks = 4 * 24), None)
mr2 = Vaccines("mr2", "Measles-Rubella-2", timedelta(weeks = 4 * 16), timedelta(weeks = 4 * 24), None)
opvb = Vaccines("opvb", "OPV Booster", timedelta(weeks = 4 * 16), timedelta(weeks = 4 * 24), None)
je2 = Vaccines("je2", "JE-2", timedelta(weeks = 4 * 16), timedelta(weeks = 4 * 24), None)
va2 = Vaccines("va2", "Vitamin A-2", timedelta(weeks = 4 * 16), timedelta(weeks = 4 * 18), None)
va3 = Vaccines("va3", "Vitamin A-3", timedelta(weeks = 4 * 22), timedelta(weeks = 4 * 24), None)
dptb = Vaccines("dptb", "DPT Booster-2", timedelta(weeks = 52 * 5), timedelta(weeks = 52 * 6), None)
tt = Vaccines("tt", "TT", timedelta(weeks = 52 * 10), timedelta(weeks = 52 * 16), None)

Vaccines.vaccineDbUpdate()