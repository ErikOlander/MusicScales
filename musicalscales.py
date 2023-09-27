import json
import re
import math 
import unittest


class MusicalNoteTests(unittest.TestCase):
   def test_octaveNotation2semitonenumber(self):
        assert MusicalNote.octaveNotation2semitonenumber("C#1")==13
        assert MusicalNote.octaveNotation2semitonenumber("D")==2
        
   def test_frequency2note(self):
        assert MusicalNote.frequency2note(16.35)[0] == "C0"
        assert MusicalNote.frequency2note(444)[0] == "A4"
        assert MusicalNote.frequency2note(452.8930)[0] == "A#4"
        assert MusicalNote.frequency2note(7902.13)[0] == "B8"


   

class MusicalScaleTests(unittest.TestCase):
    def test_1(self):
        assert MusicalScale.scaleList2integerList(["A#2","A"])==[0,11]
        assert MusicalScale.scaleString2integerList("A#2  A B ")==[0,11, 1]




class MusicalNote():

    
    @classmethod
    def notes2num(cls,note):

        notes={ "C": 0 , "B#": 0,
                "C#": 1, "Db": 1 , "C#/Db": 1 ,
                "D": 2 ,
                "D#": 3, "Eb" : 3, "D#/Eb" :3,
                "E": 4,
                "F": 5, "E#": 5,
                "F#": 6 , "Gb": 6, "F#/Gb": 6,
                "G": 7,
                "G#": 8 , "Ab": 8, "G#/Ab": 8,
                "A": 9,
                "A#": 10, "Bb": 10, "A#/Bb": 10,
                "B": 11, "Cb": 11 }
        return notes[note]

    @classmethod
    def num2note(cls,num):
        num2note1=[ "C", "C#", "D" , "D#",  "E", "F", "F#",  "G", "G#", "A", "A#", "B" ]
        return num2note1[num]



    @classmethod
    def octaveNotation2semitonenumber(cls,notation):
        notation=notation.replace("♭","b")
        notation=notation.replace("♯","#")
        #  Octave notation to semitone number
        noteoctavere=r"([A-G](?:#|b)?)([0-9]+)?" 
        m=re.match(noteoctavere,notation)
        note=m.group(1)
        if m.group(2)==None:
            octave=0
        else:
            octave=m.group(2)
        return 12*int(octave)+cls.notes2num(note)

    @classmethod
    def frequency2note(cls,frequency):

        C0_Freq=440*2**(-4-9/12) 
        SEMITONES_IN_OCTAVE = 12

        exponent = math.log2(frequency/C0_Freq)
        octave=int(exponent)
        remainder=exponent-int(exponent)
        closestNoteNumber=round(SEMITONES_IN_OCTAVE*remainder)
        octave+= closestNoteNumber//SEMITONES_IN_OCTAVE # Carry 
        closestNoteNumber=closestNoteNumber%SEMITONES_IN_OCTAVE

        if not (0<=octave<=9): 
            raise Exception(f"octave {octave} is outside valid range [0,9]")
        
        closestNote=cls.num2note(closestNoteNumber)
        relativefactor=2**(remainder-closestNoteNumber/SEMITONES_IN_OCTAVE)
        relativePercent=100*(relativefactor-1)

        return f"{closestNote}{octave}" , relativePercent



class MusicalScale(MusicalNote):
    
    @classmethod
    def scaleList2integerList(cls,scale):
    # String list scale to numeric differance scale

        

        return [cls.octaveNotation2semitonenumber(note)%12 for note in scale]
    
    @classmethod
    def numericDiff2integerList(cls,scale):
        out=[]
        s=0
        for note in scale:
            out.append(s)
            s+=note
        return out

    @classmethod
    def scaleString2integerList(cls,scale):
        letterNoteationRe=r"^([A-Z][b,♭,#,♯]?[ ]+)*([A-Z][b,♭,#,♯]?)$"
        m=re.match(letterNoteationRe,scale)
        if m != None:
            scaleList=scale.split(" ")
            scaleList=[ a  for a in scaleList if a != "" ]
            return cls.scaleList2integerList(scaleList)
        
        integerNoteationRe=r"^\{1?[0-9]([ ]*,[ ]*1?[0-9][ ]*)*\}$"
        m=re.match(integerNoteationRe,scale)
        if m != None:
            listofstrs=re.findall(r'(\d+)', scale)
            return  [int(a) for a in listofstrs]

        print("String does not match any support notation")
        return []

    @classmethod
    def compareScalesApproximatly(cls,scale,testscale):
        if len(testscale)<1:
            return []
        listOfMatchIndexLists=[]
        for start in range(len(scale)):
            matchIndexList=[]
            addtestscale=[(scale[start]+a)%12 for a in testscale]
            match=True
            for note in addtestscale:
                if not note in scale:
                    match=False
                    break
                matchIndexList.append(scale.index(note))
            if match:
                #if not matchIndexList in listOfMatchIndexLists: #TODO Why?
                listOfMatchIndexLists.append(matchIndexList)
        return listOfMatchIndexLists

    @classmethod
    def rankApproxComparisons(cls,matchIndexList,intscale):
        scalelenght=len(intscale)
        if len(matchIndexList)<1:
            return 0
        points=0
        if matchIndexList[0]!=0:
            points+=1
        for i in range(len(matchIndexList)-1):
            points+= (matchIndexList[i+1]-matchIndexList[i]-1)%scalelenght  #step of 1 is best; 0 points
        return points

class ScaleMatchObject(MusicalScale):
    def __init__(self,scalename,intscale,offset,result,rank):
        self.name=scalename
        self.intscale=intscale
        self.indexes=result
        self.rank=rank
        self.offset=offset

    def __lt__(self, other):
            return self.rank < other.rank
    def __gt__(self, other):
            return self.rank > other.rank
    def __le__(self, other):
            return self.rank <= other.rank
    def __ge__(self, other):
            return self.rank >= other.rank

    def __str__(self):
            markedscale=""
            for i,note in enumerate(self.intscale):
                if i==self.indexes[0]:
                    markedscale+=f"({note}) "

                elif i in self.indexes:
                    markedscale+=f"[{note}] "
                else:
                    markedscale+=f"{note} "

            markednotes=""
            for i,notenum in enumerate(self.intscale):
                note=self.num2note(notenum)
                if i==self.indexes[0]:
                    markednotes+=f"({note}) "

                elif i in self.indexes:
                    markednotes+=f"[{note}] "
                else:
                    markednotes+=f"{note} "

            key=self.num2note(self.intscale[0])
            return f"{key} {self.name}  \n\t\t {markedscale} \t {markednotes} \t rank: {self.rank}"

class WesternScales(MusicalScale):

    def __init__(self,scalesjson=None):
        if scalesjson==None:
            scalesjson="""
            {
            "Major": ["C", "D", "E", "F", "G", "A", "B"],
            "NaturalMinor": ["C", "D", "Eb", "F", "G", "Ab", "Bb"],
            "HarmonicMinor": ["C", "D", "Eb", "F", "G", "Ab", "B"],
            "MelodicMinorAscending": ["C", "D", "Eb", "F", "G", "A", "B"],
            "MelodicMinorDescending": ["C", "Bb", "Ab", "G", "F", "Eb", "D"],
            "Dorian": ["C", "D", "Eb", "F", "G", "A", "Bb"],
            "Phrygian": ["C", "Db", "Eb", "F", "G", "Ab", "Bb"],
            "Lydian": ["C", "D", "E", "F#", "G", "A", "B"],
            "Mixolydian": ["C", "D", "E", "F", "G", "A", "Bb"],
            "Locrian":   ["C", "Db", "Eb", "F", "Gb", "Ab", "Bb"],
            "Blues": ["C", "Eb", "F", "F#", "G", "Bb"],
            "PentatonicMajor": ["C", "D", "E", "G", "A"],
            "PentatonicMinor": ["C", "Eb", "F", "G", "Bb"]
            }
            """

        scalesStr=json.loads(scalesjson)
        intscales={}
        for scalename in scalesStr:
            intscales[scalename]=MusicalScale.scaleList2integerList(scalesStr[scalename])

        self.intscales=intscales

    def addScaleDiffList(self,name,newscale):
        self.scales[name]=newscale

    def addScaleIntegerNotation(self,name,newscale):
        self.scales[name]=self.integerList2numericDiff(newscale)

    def compareAllScalesApprox(self,testscale):
        if len(testscale)<1:
            return []
        matches=[]
        for scalename in self.intscales:
            intscale=self.intscales[scalename]
            results=self.compareScalesApproximatly(intscale,testscale)
            for result in results:
                rank=self.rankApproxComparisons(result,intscale)
                offset=testscale[0]-intscale[result[0]]
                intscaleoffset=[(a+offset)%12 for a in intscale]

                matches.append(ScaleMatchObject(scalename,intscaleoffset,offset,result,rank))

        return matches


    def cli(self):
        
        while True:
            print("""Type melody in:
    1. Integer notation, example: {3, 5, 7, 8}
    2. Letter notation, example: C D Eb F#
    To exit to write exit """)
            inputString=input()
            if inputString=="exit":
                exit()
            testscale=MusicalScale.scaleString2integerList(inputString)
            result=self.compareAllScalesApprox(testscale)
            threshold=5
            print(f"Matching scales guesses, low rank better:")
            result.sort()
            for a in result:
                if a.rank<=threshold:
                    print(a)



if __name__ == '__main__': 
    
    ws=WesternScales()

    ws.cli()

    #unittest.main()
    

