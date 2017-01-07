
import sys, gl

class Concept:
    def __init__(self):
        self.p=0.5                      #p value of concept
        self.relation=2                 #relation code
        self.parent = []                #parents list
        self.child = []                 #children list		
    def add_parents(self,parents):
        for parentitem in parents:self.parent.append(parentitem)

		
class Kbase:
    def __init__(self,instancename):
        self.cp = []                    # CONCEPT LIST CP
        self.name=instancename          # the name of the instance can be used in the log file

    def add_concept(self,new_p,new_rel,new_parents):        #add new concept to WM or KB. parents argument is list
        self.cp.append(Concept())                           #concept added
        self.ci=len(self.cp)-1                              #current index
        self.cp[self.ci].p=new_p                            #set p value
        self.cp[self.ci].relation=new_rel                   # set relation code
        self.cp[self.ci].add_parents(new_parents)           #set parents        
        for par in self.cp[self.ci].parent:                        #register new concept as the child of parents
            self.cp[par].child.append(self.ci)
        gl.log.add_log((self.name," add_concept index=",self.ci," p=",new_p," rel=",new_rel," parents=",new_parents))      #content to be logged is tuple (( ))
        return self.ci

    def match(self,what1,inwhat):                           #two concepts match? handles questions
        yes=1; sparents=[]
        if (what1.relation!=-1 and what1.relation!=inwhat.relation): yes=0   #relation is either same or -1
        else:
            for item in what1.parent: sparents.append(item)
            pindex=0
            for parentitem in sparents:
                if parentitem==-1:                          #-1 indicates question mark, this is considered as matching
                    try:
                        sparents[pindex]=inwhat.parent[pindex]
                    except: yes=yes
                pindex=pindex+1
            if sparents!=inwhat.parent: yes=0
            return yes

    def search_inlist(self,swhat):
        found=[0]
        sindex=0
        for conitem in self.cp:
            if self.match(swhat,conitem)==1:
                found.append(sindex)                #add to found list
                found[0]=found[0]+1                 #increase number of items found
            sindex=sindex+1
        return found

    def read_mentalese(self,mfilename):             #read Mentalese input from a file
        try: 
            mfile = open(mfilename,"r")             #open Mentalese input file
            for mline in mfile:                     #read lines one-by-one and process them
                attr=[mline]
                while len(attr[0])>1:
                    self.read_concept(attr)
        except IOError:
            print("ERROR: Mentalese input file not present or read incorrectly")
        mfile.close()
            
    def read_concept(self,attrList):                #recursive function to read concepts from Mentalese input
        aStr=str(attrList[0]).strip()               #parameter is passed in a wrapping list to be able to use recursion
        actPos=0
        relType=0
        pp=0.5                                      #default p is set to 0.5
        parents=[]
        isWord=1
        while (actPos<len(aStr)):
            c = aStr[actPos]                        #check the characters in the string one-by-one
            if c == '(':                            #if finds a "(", check the relType before "(", and read the embedded concept
                isWord=0
                relType=gl.args.relationcode[aStr[0:actPos]]
                attrList[0]=str(aStr[actPos+1:]).strip()
                parents.append(self.read_concept(attrList))
                aStr=str(attrList[0]).strip()
                actPos=0
                continue
            elif c == ',':                          #if finds a ",", there is two possible way
                if isWord==1:                       #if the concept is a word, register it to WL, add a new concept for it and return back its id
                    ss = aStr[0:actPos]
                    wl_ind = gl.WL.find(ss)
                    attrList[0]=str(aStr[actPos:]).strip()
                    if wl_ind == -1:
                        wl_ind = gl.WL.add_word(ss)
                    return self.add_concept(1,1,[wl_ind])
                else:                               #if the concept is not a single word, register the embedded concept as parent, and read the next parent
                    attrList[0]=str(aStr[actPos+1:]).strip()
                    parents.append(self.read_concept(attrList))
                    aStr=str(attrList[0]).strip()
                    actPos=0
                    continue
            elif c == ')':                          #if finds a ")", there is two possible way
                if isWord==1:                       #if the concept is a word, register it to WL, add a new concept for it and return back its id
                    ss=aStr[0:actPos]
                    wl_ind=gl.WL.find(ss)
                    attrList[0]=str(aStr[actPos:]).strip()
                    if wl_ind == -1:
                        wl_ind = gl.WL.add_word(ss)
                    return self.add_concept(1,1,[wl_ind])
                else:                               #if the concept is not a single word, register the embedded concept as parent, and read the next parent
                    if actPos+2 < len(aStr) and aStr[actPos+1]=='p' and aStr[actPos+2]=='=':
                        n_end=actPos+4
                        while n_end <= len(aStr):
                            try:
                                newp=float(aStr[actPos+3:n_end])
                            except:
                                n_end -= 1
                                break
                            else:
                                n_end += 1
                        newp=float(aStr[actPos+3:n_end])
                        pp=newp
                        actPos=n_end
                    attrList[0]=str(aStr[actPos:]).strip()
                    return self.add_concept(pp,relType,parents)
                
            actPos=actPos+1
        return