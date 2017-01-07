
import sys

class Arguments:
    def __init__(self):
        self.argnum=len(sys.argv)
        self.pgranu=4                           # granularity for p, pgranu+1 discrete values from 0
        self.pclas=[[0,0,0,0,0],[0,1,1,1,1],[0,1,1,2,2],[0,1,2,2,3],[0,1,2,3,4]]     #pclas is the matrix for class reasoning. C(%1,%2)p1 and %X(%2,%3)p2 -> %x(%2,%3)pclas, pclas[p2,p1]
        self.relationcode={"W":1,"S":2,"D":3,"C":4,"F":5,"Q":6,"A":7,"I":8,"R":9,"T":10,"P":11,"M":12,"IM":13,"N":14,"V":15,"AND":16,"NOT":17,"OR":18,"XOR":19}

class Logging:
    def __init__(self,fname="logfile.txt"):
        try: self.logf=open(fname,"w")
        except: print("ERROR: Logging: log file could not be opened")
    def add_log(self,what):                                 #what must be iterable
        try:
            for item in what: self.logf.write(str(item))
            self.logf.write("\n")
        except: print("ERROR: Logging: log file not present or called incorrectly",str(what))
        
