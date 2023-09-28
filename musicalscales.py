import json
import re
import math 
import argparse





class MusicalNote():

    
    @classmethod
    def notes2num(cls,note: str):

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
    def num2note(cls,num: int):
        num2note1=[ "C", "C#", "D" , "D#",  "E", "F", "F#",  "G", "G#", "A", "A#", "B" ]
        return num2note1[num]



    @classmethod
    def octaveNotation2semitonenumber(cls,notation: str):
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
    def frequency2note(cls,frequency: float):

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
    def scaleList2integerList(cls,scale: list):
    # String list scale to numeric differance scale
        return [cls.octaveNotation2semitonenumber(note)%12 for note in scale]
    
    @classmethod
    def integerList2scaleList(cls,scale: list):
        return [cls.num2note(note) for note in scale]
    
    @classmethod
    def scaleString2integerList(cls,scale):
        letterNotationRe=r"([A-G](?:#|b)?)([0-9]+)?" 
        matches=re.findall(letterNotationRe, scale)
        if len(matches)>0:
            listOfNotes=re.findall(r'([A-Z][b,♭,#,♯]?)', scale)
            return cls.scaleList2integerList(listOfNotes)
        
        integerNoteationRe=r"\{1?[0-9]([ ]*,[ ]*1?[0-9][ ]*)*\}"
        m=re.match(integerNoteationRe,scale)
        if m != None:
            listofstrs=re.findall(r'(\d+)', scale)
            return  [int(a) for a in listofstrs]

        raise Exception( "String does not match any notation")

    @classmethod
    def compareScalesApproximatly(cls,scale: list,testscale: list):
        weights={
                "startNotRoot":1,
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
            index=start
            for note in addtestscale:
                if note==scale[index]: 
                    # try next note in scale
                    matchIndexList.append(index)
                    index=(index+1)%len(scale)

                elif note in scale:
                    # try skipping forward in scale
                    newindex=scale.index(note)
                    rank+=weights["skipANote"]*((newindex-index)%len(scale))
                    index=newindex
                    matchIndexList.append(index)
                    index=(index+1)%len(scale)

                else:
                    match=False
                    break
            if match:
                listOfMatchIndexLists.append((matchIndexList,rank))

        return listOfMatchIndexLists


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

    def __init__(self,scalesjson: str=None):
        if scalesjson==None:
            scalesjson="""
            {
            "Major": ["C", "D", "E", "F", "G", "A", "B"],
            "Natural Minor": ["C", "D", "Eb", "F", "G", "Ab", "Bb"],
            "Harmonic Minor": ["C", "D", "Eb", "F", "G", "Ab", "B"],
            "Melodic Minor Ascending": ["C", "D", "Eb", "F", "G", "A", "B"],
            "Melodic Minor Descending": ["C", "Bb", "Ab", "G", "F", "Eb", "D"],
            "Dorian": ["C", "D", "Eb", "F", "G", "A", "Bb"],
            "Phrygian": ["C", "Db", "Eb", "F", "G", "Ab", "Bb"],
            "Lydian": ["C", "D", "E", "F#", "G", "A", "B"],
            "Mixolydian": ["C", "D", "E", "F", "G", "A", "Bb"],
            "Locrian":   ["C", "Db", "Eb", "F", "Gb", "Ab", "Bb"],
            "Blues": ["C", "Eb", "F", "F#", "G", "Bb"],
            "Pentatonic Major": ["C", "D", "E", "G", "A"],
            "Pentatonic Minor": ["C", "Eb", "F", "G", "Bb"]
            }
            """

        scalesStr=json.loads(scalesjson)
        intscales={}
        for scalename in scalesStr:
            intscales[scalename]=MusicalScale.scaleList2integerList(scalesStr[scalename])

        self.intscales=intscales

    def setScale(self,name: str,newscale: str):
        self.intscales[name]= self.scaleString2integerList(newscale)

    def compareAllScalesApprox(self,testscale: list,threshold: int=3, maxreturns: int=5):
        if len(testscale)<1:
            return []
        matches=[]
        for scalename in self.intscales:
            intscale=self.intscales[scalename]
            results=self.compareScalesApproximatly(intscale,testscale)
            for result in results:
                indexes=result[0]
                rank=result[1]
                offset=testscale[0]-intscale[indexes[0]]
                intscaleoffset=[(a+offset)%12 for a in intscale]
                if rank>threshold:
                    continue
                matches.append(ScaleMatchObject(scalename,intscaleoffset,offset,indexes,rank))

        matches.sort()

        end=min(maxreturns,len(matches))
        return matches[:end]


def main():
    parser = argparse.ArgumentParser(  
         prog='Mucical Scale Matcher')
    parser.add_argument('-t', '--threshold',default=3)  
    parser.add_argument('-m', '--maxreturns',default=5)    
    args = parser.parse_args()
    print(""" Supported formats:
1. Integer notation, example: {3, 5, 7, 8}
2. Letter notation, example: C D Eb F#
""")
    while True:
        ws=WesternScales()
        inputScale=input()
        try:
            testscale=ws.scaleString2integerList(inputScale)
        except:
            print("""Input not recognized as a scale, exiting ...""")
            break
        letterTestScale=ws.integerList2scaleList(testscale)
        
        result=ws.compareAllScalesApprox(testscale,args.threshold,args.maxreturns)
        if len(result)<1:
            print(f"No matching scales below threshold {args.threshold}")
            continue
        print(f"""Matching melody {testscale} {" ".join(letterTestScale)} 
Melody starts on () and continues with [], low rank better
===========================================================
              """)
        for a in result:
            print(a)



if __name__ == '__main__': 
    main()

    

