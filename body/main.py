from temp import *
from datetime import *
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from mongo import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label

children = list(map(lambda item: list(item.values()), childcol.find()))
parentId = "P1"

def children_get():
    global children
    children = list(map(lambda item: list(item.values()), childcol.find()))

def create_popup(title, text):
    popup = Popup(title=title,
        content=Label(text=text),
        size_hint=(0.4, 0.4))
    popup.open()

class ParentScreen(Screen):
    pass

class AddChildScreen(Screen):
    def addChild(self, name, dob, docid):
        dateOfBirth = datetime(int(dob[6:]), int(dob[3:5]), int(dob[:2]))
        childId = "C" + str(len(children) + 1)
        dueVaccines, overVaccines, yetVaccines = Vaccines.validVaccines(dateOfBirth)
        document = {"pid": parentId, "did": docid, "cid": childId,"name": name, "dob": dateOfBirth, "dueVaccines": dueVaccines, "overVaccines": overVaccines, "yetVaccines": yetVaccines}
        childcol.insert_one(document)
        children_get()
        create_popup("Success", "Account created successfully!")




class IllimmunateApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ParentScreen(name = "parent"))
        sm.add_widget(AddChildScreen(name = "addchild"))
        return sm
IllimmunateApp().run()