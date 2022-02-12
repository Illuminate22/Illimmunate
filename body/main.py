from datetime import *
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from mongo import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label

children = list(map(lambda item: list(item.values()), childcol.find()))
parentId = "P1"
vaxlist = []

def children_get():
    global children
    children = list(map(lambda item: list(item.values()), childcol.find()))

def vaccines_get():
    global vaxlist
    for vaccine in vaxcol.find():
        vaxlist.append(vaccine)

def create_popup(title, text):
    popup = Popup(title=title,
        content=Label(text=text),
        size_hint=(0.4, 0.4))
    popup.open()

def validVaccines(dob, childVaxList = vaxlist):
        vaccines_get()
        presentDay = datetime.today()
        dueVaccines, overVaccines, yetVaccines = [], [], []
        for vaccine in childVaxList:
            if timedelta(days=vaccine["date_start"]) + dob < presentDay and timedelta(days=vaccine["date_end"]) + dob > presentDay or timedelta(days=vaccine["date_end"]) + dob == presentDay:
                dueVaccines.append(vaccine)
            elif timedelta(days=vaccine["date_start"]) + dob > presentDay:
                yetVaccines.append(vaccine)
            elif timedelta(days=vaccine["date_end"])+dob<presentDay:
                overVaccines.append(vaccine)
        return dueVaccines, overVaccines, yetVaccines


class ParentScreen(Screen):
    pass

class AddChildScreen(Screen):
    def addChild(self, name, dob, docid):
        try:
            dateOfBirth = datetime(int(dob[6:]), int(dob[3:5]), int(dob[:2]))
        except:
            create_popup("Error!", "Enter a valid date!")
            self.ids.dobin.text = ""
            return
        if name == "":
            create_popup("Error!", "Enter a valid date!")
            self.ids.namein.text = ""
            return

        childId = "C" + str(len(children) + 1)
        dueVaccines, overVaccines, yetVaccines = validVaccines(dateOfBirth)
        document = {"pid": parentId, "did": docid, "cid": childId,"name": name, "dob": dateOfBirth, "dueVaccines": dueVaccines, "overVaccines": overVaccines, "yetVaccines": yetVaccines}
        childcol.insert_one(document)
        children_get()
        create_popup("Success", "Account created successfully!")
        self.ids.dobin.text = ""
        self.ids.namein.text = ""
        self.ids.docin.text = ""





class IllimmunateApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ParentScreen(name = "parent"))
        sm.add_widget(AddChildScreen(name = "addchild"))
        return sm
IllimmunateApp().run()