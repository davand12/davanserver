'''
@author: davandev
'''
import hashlib

class Alarm():
    def __init__(self, alarm_id, severence, title):
        self.id = hashlib.md5(alarm_id.encode()).hexdigest()
        self.severence = severence
        self.title = title
        
    def toString(self):
        return self.id + " " + self.title + " " + self.severence
