#!/usr/bin/env python3
import time
from datetime import datetime, timedelta
import threading, pathlib, pickle

DATE_FORMAT = "%d-%m-%Y"
P = pathlib.Path(__file__).with_name(".tdata")

class activity:

    name = ""
    log = {}
    state = False
    thread = None

    def __init__(self,name:str,log={}):
        self.name = name
        self.log = log

    def start(self):
        self.state = True
        key = todays_date()
        if key not in self.log:
           self.log[key] = 0

        while self.state:
            self.log[key] += 1
            time.sleep(1)

    def stop(self):
        self.state = False


class activities(list):
    ACTIVE = None

    def add(self, name:str, log={}):
        if not self.exists(name): self.append(activity(name,log)); return True

    def delete(self, name:str):
        if self.exists(name): self.remove(self.get(name)); return True

    def flush(self):
        for _ in range(len(self)): self.pop(0)

    def clean_log(self,name:str,date=None,today=False):
        act = self.get(name)
        if today and act:
            key = todays_date()
            if key in act.log: del act.log[key]; return True
        elif date and act:
            if date in act.log: del act.log[date]; return True
        elif act:
            act.log = {}; return True

    def clean_all_logs(self):
        for act in self:
            act.log = {}

    def exists(self, name:str):
        for activity in self:
            if name.lower() == activity.name.lower():
                return True
        return False

    def get_all_names(self) -> list:
        names = []
        for act in self:
            names.append(act.name.capitalize())
        return names

    def get(self,name:str):
        for act in self:
            if act.name.lower() == name.lower():
                return act

    def get_log(self,name:str,raw=False):
        if self.exists(name):
            log = self.get(name).log

            if raw:
                return log

            if log == {}: return "Empty"

            string = "\n".join([f"{key}: {timeconv(value)}" for key,value in log.items()])
            return string

    def get_logs(self,raw=False):
        string = ""
        for act in self:
            string += act.name.capitalize() + "\n"
            string += self.get_log(act.name) + "\n\n"
        return string

    def todays_log(self,name:str):
        key = todays_date(); act = self.get(name)
        if act:
            log = str(timedelta(seconds=act.log[key])) if key in act.log else "Empty"
            return log

    def activate(self, name:str):
        if self.exists(name):
            self.ACTIVE = self.get(name)
            self.ACTIVE.thread = threading.Thread(target=self.ACTIVE.start,daemon=True)
            self.ACTIVE.thread.start()

    def deactivate(self):
        if self.ACTIVE:
            self.ACTIVE.stop()

    def is_thread_active(self):
        if self.ACTIVE is None:
            return False
        isactive = self.ACTIVE.thread.is_alive()
        return isactive

    def select(self,name:str):
        if self.exists(name): self.insert(0,self.pop(self.index(self.get(name)))); return True

    def map(self,name,index):
        if index >= len(self): return False
        if self.exists(name):
            self.insert(index,self.pop(self.index(self.get(name))))
            return True

def timeconv(seconds:int):
        seconds = str(timedelta(seconds=seconds))
        return seconds

def todays_date(string=True):
    todayob = datetime.now()
    formatted = todayob.strftime(DATE_FORMAT)
    if string:
        return formatted
    return todayob

def save(activities):
    data = {}
    with P.open("wb") as f:
        for act in activities:
            data[act.name] = act.log

        pickle.dump(data,f)

def load():
    data = activities()
    try:
        with P.open("rb") as f:
            x = pickle.load(f)
    except (FileExistsError, FileNotFoundError, pickle.UnpicklingError): return data

    if x is None or x == {}:
        return data

    for name, log in x.items():
        data.add(name,log)

    return data

if __name__ == "__main__":
    breakpoint()
