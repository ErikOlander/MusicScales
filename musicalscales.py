import json
import re
import math 
import argparse





class MusicalNote():

    
    @classmethod
    def notes2num(cls,note: str) -> int:

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
    def num2note(cls,num: int) -> str:
        num2note1=[ "C", "C#", "D" , "D#",  "E", "F", "F#",  "G", "G#", "A", "A#", "B" ]
        return num2note1[num]



    @classmethod
    def octaveNotation2semitonenumber(cls,notation: str)  -> int:
        notation=notation.replace("♭","b")
        notation=notation.replace("♯","#")
        #  Octave notation to semitone number
        noteoctavere=r"([A-G](?:#|b)?)([0-9]+)?" 
        m=re.match(noteoctavere,notation)
        if m==None:
            raise Exception(f"String \"{notation}\" does not match musical letter notation")
        note=m.group(1)
        if m.group(2)==None:
            octave=0
        else:
            octave=m.group(2)
        return 12*int(octave)+cls.notes2num(note)

    @classmethod
    def frequency2note(cls,frequency: float) -> str:

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
    def scaleList2integerList(cls,scale: list) -> list:
    # String list scale to numeric differance scale
        return [cls.octaveNotation2semitonenumber(note)%12 for note in scale]
    
    @classmethod
    def integerList2scaleList(cls,scale: list) -> list:
        return [cls.num2note(note) for note in scale]
    

    @classmethod
    def scaleString2integerList(cls,scale: str) -> list:
        noteRegex=r"([A-Z][b,♭,#,♯]?[0-9]?)"
        listOfNotes=re.findall(noteRegex, scale)
        if listOfNotes!=[]:
            return cls.scaleList2integerList(listOfNotes)
        
        integerNotationRe=r"\{(([0-9]|10|11),)*([0-9]|10|11)\}"
        m=re.match(integerNotationRe,scale.replace(" ",""))
        if m != None:
            listofstrs=re.findall(r'(\d+)', scale)
            return  [int(a) for a in listofstrs]


        raise Exception( "String does not match any notation")

    @classmethod
    def compareScales(cls,scale: list,testscale: list) -> list:
        #Should be acending mod 12

        weights={
                "startNotRoot":3,
                "skipANote":1
                 }
        if len(testscale)<1:
            return []
        listOfMatchIndexLists=[]
        for start in range(len(scale)):
            matchIndexList=[]
            rank=weights["startNotRoot"] if start>0 else 0 
            addtestscale=[(scale[start]-testscale[0]+a)%12 for a in testscale]
            
            match=True
            for note in addtestscale:
                if not note in scale:
                    match=False
                    break
                matchIndexList.append(scale.index(note))

            skippedNotes=len(scale)-len(addtestscale)
            
            rank+=skippedNotes*weights["skipANote"]
            if match:
                listOfMatchIndexLists.append((matchIndexList,rank))

        return listOfMatchIndexLists

    @classmethod
    def melody2Scale(cls,melody):
        #identify root note
        counter=[0]*12
        for note in melody:
            counter[note] +=1

        counter[melody[0]]+=5
        counter[melody[-1]]+=4

        maxindex=counter.index(max(counter))
        root=melody[maxindex]
    
        normalizedScale=[(a-root)%12 for a in melody]

        normalizedScale=list(set(normalizedScale)) #remove duplicates
        normalizedScale.sort()

        scale=[(a+root)%12 for a in normalizedScale]
        return scale



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
            return f"{key} {self.name}  \n\t {markedscale} \t {markednotes} \t rank: {self.rank}"

class WesternScales(MusicalScale):

    def __init__(self,scalesjson: str=""):
        if scalesjson=="":
            scalesjson="""
{
    "Major": {
        "scale": ["C", "D", "E", "F", "G", "A", "B"],
        "rank": 0
    },
    "Natural Minor": {
        "scale": ["C", "D", "Eb", "F", "G", "Ab", "Bb"],
        "rank": 0
    },
    "Harmonic Minor": {
        "scale": ["C", "D", "Eb", "F", "G", "Ab", "B"],
        "rank": 1
    },
    "Dorian": {
        "scale": ["C", "D", "Eb", "F", "G", "A", "Bb"],
        "rank": 1
    },
    "Phrygian": {
        "scale": ["C", "Db", "Eb", "F", "G", "Ab", "Bb"],
        "rank": 2
    },
    "Lydian": {
        "scale": ["C", "D", "E", "F#", "G", "A", "B"],
        "rank": 2
    },
    "Mixolydian": {
        "scale": ["C", "D", "E", "F", "G", "A", "Bb"],
        "rank": 1
    },
    "Locrian": {
        "scale":  ["C", "Db", "Eb", "F", "Gb", "Ab", "Bb"],
        "rank": 3
    },
    "Blues": {
        "scale": ["C", "Eb", "F", "F#", "G", "Bb"],
        "rank": 0
    },
    "Pentatonic Major": {
        "scale": ["C", "D", "E", "G", "A"],
        "rank": 0
    },
    "Pentatonic Minor": {
        "scale": ["C", "Eb", "F", "G", "Bb"],
        "rank": 0
    }
}
            """

        scalesStr=json.loads(scalesjson)
        intscales={}
        ranks={}
        for scalename in scalesStr:
            intscales[scalename]=MusicalScale.scaleList2integerList(scalesStr[scalename]["scale"])
            ranks[scalename]=scalesStr[scalename]["rank"]

        self.intscales=intscales
        self.ranks=ranks

    def setScale(self,name: str,newscale: str, rank: int) -> None:
        self.intscales[name]= self.scaleString2integerList(newscale)
        self.ranks[name]= rank

    def shiftNamedScale(self,name,key):
        scale=self.intscales[name]
        firstnote=scale[0]
        shiftedScale=[ (a+key-firstnote)%12  for a in scale]
        return shiftedScale


    def scaleKey2integerList(self,scale) -> list:
        scaleKeyRegex=r"([A-Z][b,♭,#,♯]?[0-9]?) ([A-Za-z ]+)"
        m=re.search(scaleKeyRegex,scale)
        if m != None:
            name=m.group(2).strip(" ")
            key=self.octaveNotation2semitonenumber( m.group(1))%12
            return self.shiftNamedScale(name,key)


    def compareAllScales(self,testscale: list, maxreturns: int=5) -> list:
        #Should be acending mod 12
        if len(testscale)<1:
            return []
        matches=[]
        for scalename in self.intscales:
            intscale=self.intscales[scalename]
            scalerank=self.ranks[scalename]
            results=self.compareScales(intscale,testscale)
            for result in results:
                indexes=result[0]
                rank=result[1]+scalerank
                offset=testscale[0]-intscale[indexes[0]]
                intscaleoffset=[(a+offset)%12 for a in intscale]
                matches.append(ScaleMatchObject(scalename,intscaleoffset,offset,indexes,rank))

        matches.sort()

        end=min(maxreturns,len(matches))
        return matches[:end]


def main() -> None:
    parser = argparse.ArgumentParser(  
         prog='Mucical Scale Matcher') 
    parser.add_argument('-m', '--maxreturns',default=5)    
    args = parser.parse_args()
    print(""" Supported formats:
1. Integer notation 0-11, example: {3, 5, 7, 8}
2. Letter notation, example: C D Eb F#
3. Key and scale name, example: D Natural Minor
the matching is invariant to order other than root
""")
    ws=WesternScales()

    while True:

        inputScale=input()
        if inputScale=="" or inputScale=="exit":
            print("""Exiting""")
            break

        testscale=None
        try:
            testscale=ws.scaleKey2integerList(inputScale)
            
            #already acending
        except:
            pass
        try:
            testscale=ws.scaleString2integerList(inputScale)
            testscale=ws.melody2Scale(testscale)
        except:
            pass

        if testscale==None:
            print("""Input not recognized as a scale, configured scales:""")
            print ("\n".join([name for name in ws.intscales]))
            continue

        letterTestScale=ws.integerList2scaleList(testscale)
        
        result=ws.compareAllScalesApprox(testscale,args.maxreturns)
        if len(result)<1:
            print(f"No matching scales")
            continue
        print(f"""Matching melody {testscale} {" ".join(letterTestScale)} 
Melody starts on () and continues with [], low rank better
===========================================================
              """)
        for a in result:
            print(a)



if __name__ == '__main__': 
    main()

    

