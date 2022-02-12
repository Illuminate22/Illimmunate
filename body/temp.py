from datetime import *

class Vaccines:
    vaxlist = []
    def __init__(self, name, date_start, date_end, info):
        dic = {"name" :name,"date_start" : date_start,"date_end" : date_end,"info" : info}
        Vaccines.vaxlist.append(dic)
        self.dic = dic
    def __str__(self):
        return self["name"]
    def validVaccines(dob, childVaxList = vaxlist):
        presentDay = datetime.today()
        dueVaccines, overVaccines, yetVaccines = [], [], []
        for vaccine in childVaxList:
            if vaccine["date_start"] + dob < presentDay and vaccine["date_end"] + dob > presentDay or vaccine["date_end"] + dob == presentDay:
                dueVaccines.append(vaccine)
            if vaccine["date_start"] + dob > presentDay:
                overVaccines.append(vaccine)
            else:
                yetVaccines.append(vaccine)
        return dueVaccines, overVaccines, yetVaccines

opv0 = Vaccines("OPV-0", timedelta(days = 0), timedelta(days = 15), None)
opv1 = Vaccines("OPV-1", timedelta(weeks = 5), timedelta(weeks = 6), None)
opv2 = Vaccines("OPV-2", timedelta(weeks = 9), timedelta(weeks = 10), None)
opv3 = Vaccines("OPV-3", timedelta(weeks = 13), timedelta(weeks = 14), None)
ptv1 = Vaccines("Pentavalent-1", timedelta(weeks = 5), timedelta(weeks = 6), None)
ptv2 = Vaccines("Pentavalent-2", timedelta(weeks = 9), timedelta(weeks = 10), None)
ptv3 = Vaccines("Pentavalent-3", timedelta(weeks = 13), timedelta(weeks = 14), None)
rtv1 = Vaccines("Rotavirus-1", timedelta(weeks = 5), timedelta(weeks = 6), None)
rtv2 = Vaccines("Rotavirus-2", timedelta(weeks = 9), timedelta(weeks = 10), None)
rtv3 = Vaccines("Rotavirus-3", timedelta(weeks = 13), timedelta(weeks = 14), None)
ipv1 = Vaccines("IPV-1", timedelta(weeks = 5), timedelta(weeks = 6), None)
ipv2 = Vaccines("IPV-2", timedelta(weeks = 13), timedelta(weeks = 14), None)
mr1 = Vaccines("Measles-Rubella-1", timedelta(weeks = 4 * 9), timedelta(weeks = 4 * 12), None)
je1 = Vaccines("JE-1", timedelta(weeks = 4 * 9), timedelta(weeks = 4 * 12), None)
va1 = Vaccines("Vitamin A-1", timedelta(weeks = 4 * 9), timedelta(weeks = 4 * 12), None)
dpt1 = Vaccines("DPT booster-1", timedelta(weeks = 4 * 16), timedelta(weeks = 4 * 24), None)
mr2 = Vaccines("Measles-Rubella-2", timedelta(weeks = 4 * 16), timedelta(weeks = 4 * 24), None)
opvb = Vaccines("OPV Booster", timedelta(weeks = 4 * 16), timedelta(weeks = 4 * 24), None)
je2 = Vaccines("JE-2", timedelta(weeks = 4 * 16), timedelta(weeks = 4 * 24), None)
va2 = Vaccines("Vitamin A-2", timedelta(weeks = 4 * 16), timedelta(weeks = 4 * 18), None)
va3 = Vaccines("Vitamin A-3", timedelta(weeks = 4 * 22), timedelta(weeks = 4 * 24), None)
dptb = Vaccines("DPT Booster-2", timedelta(weeks = 52 * 5), timedelta(weeks = 52 * 6), None)
tt = Vaccines("TT", timedelta(weeks = 52 * 10), timedelta(weeks = 52 * 16), None)

