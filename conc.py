import sys, gl


def match(what1, inwhat):  # two concepts match? handles questions
    # TODO should we use booleans instead numbers?
    # e.g. result = True
    yes = 1;
    sparents = []
    if what1.relation != -1 and what1.relation != inwhat.relation:
        yes = 0  # relation is either same or -1
    else:                               # relation matches
        for item in what1.parent: sparents.append(item)
        pindex = 0
        for parentitem in sparents:     # handle -1 parents
            if parentitem == -1:        # -1 indicates question mark, this is considered as matching
                try:
                    sparents[pindex] = inwhat.parent[pindex]
                except:
                    yes = yes
            pindex = pindex + 1
        for pix in range(len(sparents)):                # compare for match
            if (gl.WM.cp[sparents[pix]].relation!=1):   # not word
                try:
                    if (sparents[pix]!=inwhat.parent[pix]):yes=0    # pARENTS MUST MATCH
                except: yes=0                           # list length mismatch
            else:                                       # parent is word
                try:
                    if (gl.WM.cp[sparents[pix]].kblink != gl.WM.cp[inwhat.parent[pix]].kblink):
                        yes=0                           # kblink indicates word meaning, it should match
                except: yes=0                           # list length mismatch
    return yes


class Concept:
    def __init__(self,rel=0):
        self.p = 0.5        # p value of concept
        self.relation = rel # relation code
        self.parent = []    # parents list
        self.child = []     # children list
        self.wordlink = []  # link to WL, if this is a word
        self.kblink = []    # link to KB, if this is in WM
        self.mentstr = ""   # string format of mentalese

    def add_parents(self, parents):
        for parentitem in parents: self.parent.append(parentitem)


class Kbase:
    def __init__(self, instancename):
        self.cp = []                    # CONCEPT LIST CP
        self.ci = -1
        self.name = instancename          # the name of the instance can be used in the log file

    def add_concept(self, new_p, new_rel, new_parents,kbl=[]):        #add new concept to WM or KB. parents argument is list
        self.cp.append(Concept(new_rel))                        #concept added
        self.ci = len(self.cp) - 1                              #current index
        self.cp[self.ci].p = new_p                              #set p value
        self.cp[self.ci].add_parents(new_parents)               #set parents
        self.cp[self.ci].kblink[:]=kbl[:]                       # set link to KB
        if (new_rel != gl.args.rcode["W"]):                     # if this is not a word
            for par in self.cp[self.ci].parent:                 #register new concept as the child of parents
                self.cp[par].child.append(self.ci)

            self.cp[self.ci].mentstr = gl.args.rcodeBack[new_rel] + "("     # set mentstr
            for cind in self.cp[self.ci].parent:
                self.cp[self.ci].mentstr = self.cp[self.ci].mentstr + self.cp[cind].mentstr + ","
            self.cp[self.ci].mentstr = self.cp[self.ci].mentstr[:-1] + ")"
            
        else:                                                   #this is a word
            if (len(kbl)>0):                                    #set word link if we have KB link
                self.cp[self.ci].wordlink.append(gl.KB.cp[kbl[0]].wordlink[0])      # we have a single word link
                self.cp[self.ci].mentstr = gl.KB.cp[kbl[0]].mentstr[:]
        gl.log.add_log((self.name," add_concept index=",self.ci," p=",new_p," rel=",new_rel," parents=",new_parents," wordlink=",self.cp[self.ci].wordlink," mentstr=",self.cp[self.ci].mentstr))      #content to be logged is tuple (( ))
        return self.ci

    def remove_concept(self):
        gl.log.add_log((self.name," remove concept index=",self.ci))
        if (self.ci>-1):
            self.cp.pop()
            self.ci=self.ci-1   
        return self.ci

    def rec_match(self, what1, inwhat):  # two concepts match? handles questions
        # TODO should we use booleans instead numbers?
        # e.g. result = True

        if what1.relation != -1 and inwhat.relation != -1 and what1.relation != inwhat.relation:
            return 0     # relation is neither same nor -1 -> not match

        if what1.relation == 1:     # comparing two word concepts
            if what1.kblink == inwhat.kblink :
                return 1
            else: 
                return 0
        
        if len(what1.parent) != len(inwhat.parent):
            return 0     # if number of parents are not equal -> not match
            
        for pindex in range(0, len(what1.parent)):
            if what1.parent[pindex] == -1 or inwhat.parent[pindex] == -1 :     # handle -1 parents
                continue    # -1 indicates question mark, this is considered as matching

            if self.rec_match(self.cp[what1.parent[pindex]], self.cp[inwhat.parent[pindex]]) == 0:      # compare parent concepts for match
                return 0    # if parent concept does not match -> no match
            
        return 1

    def get_child(self,rel,parents=[]):                      # search concept as child of parent
        found=-1
        for child in self.cp[parents[0]].child:         # in children of the first parent
            if (self.cp[child].relation==rel):          # relation must match
                if (self.cp[child].parent==parents):    # parents must match
                    found=child
        return found

    def walk_db(self,curri,lasti=-2):                   # recursive walk over WM or KB from curri towards all parents. Call without lasti.
        while (len(self.cp[curri].parent)>0 and lasti!=self.cp[curri].parent[-1]):
            try: nextp=self.cp[curri].parent.index(lasti)+1
            except:
                lasti=-2        # enter lower level
                nextp=0
            lasti=self.walk_db(self.cp[curri].parent[nextp],lasti)
        print ("walk",self.name,"current concept",curri,"parents",self.cp[curri].parent,"mentalese",self.cp[curri].mentstr)
        return curri

    def copyto_kb(self,curri,lasti=-2):         # copy concept in WM on curri to KB with all parents
        while (len(self.cp[curri].parent)>0 and lasti!=self.cp[curri].parent[-1]):
            try: nextp=self.cp[curri].parent.index(lasti)+1
            except:
                lasti=-2        # enter lower level
                nextp=0
            lasti=self.copyto_kb(self.cp[curri].parent[nextp],lasti)
        # COPY ACTION to follow:
        if self.name=="WM":                         # copy from WM only
            if len(self.cp[curri].kblink)==0:       # not yet in KB
                plist=[]                            # holds parent indices valiod in KB
                for pari in self.cp[curri].parent:  # parents valid in WM
                    plist.append(self.cp[pari].kblink[0])   # append parent index valid in KB
                kbl=gl.KB.get_child(self.cp[curri].relation,plist)   # search concept in KB as child of parent
                if kbl==-1:                         # not found in KB
                    kbl=gl.KB.add_concept(self.cp[curri].p,self.cp[curri].relation,plist)      # copy to KB
                self.cp[curri].kblink.append(kbl)   # set KB link in WM
                # print ("KB copy curri",curri,"KB index",kbl,"ment:",gl.KB.cp[kbl].mentstr)
        return curri
            
    def move_rule(self,tf,ri,starti):           # if this is a rule then move it to KB
        if ("%1" in tf.mentalese[ri]):          # if this is a rule
            gl.WM.copyto_kb(gl.WM.ci)           # copy last concept in WM, which should be the rule, to KLB
            for i in range(gl.WM.ci-starti): gl.WM.remove_concept()     # remove rule from WM
        

    def search_inlist(self, swhat):
        found = []
        sindex = 0
        for conitem in self.cp:
            if self.rec_match(swhat, conitem) == 1:
                found.append(sindex)  # add to found list
            sindex = sindex + 1
        return found

    def answer_question(self,starti,endi):           # answer a question that is is WM
        answerlist=[]
        pix=0
        for pit in gl.WM.cp[endi].parent:
            for wi in gl.WM.cp[pit].wordlink:
                if (gl.WL.wcp[wi].word=="?"):           # replace ? word with parent=-1
                    gl.WM.cp[endi].parent[pix]=-1
            pix=pix+1
        answers=gl.WM.search_inlist(gl.WM.cp[endi])     # search in WM
        for aw in answers:
            if (aw<endi):                               # answer must be before question
                answerlist.append(aw)
        if len(answerlist)==0:                          # no answer
            if -1 not in gl.WM.cp[endi].parent:         # question not for parent but for p Z(a,b)?
                starti=endi                              # we keep the question as answer
                answerlist.append(endi)
                gl.WM.cp[endi].p=gl.args.pdef_unknown   # p is set to unknown value, 0.5
        for i in range(endi-starti): gl.WM.remove_concept()     # remove question from WM
        return answerlist
    
    def read_mentalese(self,mfilename,mlist=[]):    #read Mentalese from a file or get in a list
        if (len(mlist)==0):                         #no input in mlist
            try: 
                mfile = open(mfilename,"r")             #open Mentalese input file
                for mline in mfile:                     #read lines one-by-one and process them
                    attr=[mline]
                    while len(attr[0])>1:
                        self.read_concept(attr)
            except IOError:
                print("ERROR: Mentalese input file not present or read incorrectly")
            mfile.close()
        else:
            while len(mlist[0])>1:
                self.read_concept(mlist)
            
    def read_concept(self,attrList):                #recursive function to read concepts from Mentalese input
        aStr=str(attrList[0]).strip()               #parameter is passed in a wrapping list to be able to use recursion
        actPos=0
        relType=0
        pp=gl.args.pdefault                         #default p is set to 0.5
        parents=[]
        isWord=1
        while (actPos<len(aStr)):
            c = aStr[actPos]                        #check the characters in the string one-by-one
            if c == '(':                            #if finds a "(", check the relType before "(", and read the embedded concept
                isWord=0
                relType=gl.args.rcode[aStr[0:actPos]]
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
                    return self.add_concept(1,1,[],[wl_ind])  #parent is empty, KB link is wl_ind
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
                    return self.add_concept(1,1,[],[wl_ind])
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
                    else:
                        actPos += 1
                    attrList[0]=str(aStr[actPos:]).strip()
                    return self.add_concept(pp,relType,parents)
                
            actPos=actPos+1
        return


if __name__ == "__main__":
    print("This is a module file, run natlan.py instead")
