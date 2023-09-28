
from musicalscales import MusicalNote,MusicalScale,WesternScales
import unittest
from unittest.mock import patch, Mock

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
        assert MusicalScale.scaleList2integerList(["A#2","A"])==[10,9]

    def test_2(self):
        assert MusicalScale.scaleString2integerList("A#2  A B ")==[10,9, 11]
        assert MusicalScale.scaleString2integerList("A♯5 , A♭, B ")==[10,8, 11]
        assert MusicalScale.scaleString2integerList("A#1 - A - B ")==[10,9, 11]
        assert MusicalScale.scaleString2integerList("{10, 9, 11}")==[10,9, 11]

class WestenScalesTest(unittest.TestCase):
    def test_matchscale(self):
        ws=WesternScales()
        testscale=ws.scaleString2integerList("C D E F G")
        result=ws.compareAllScalesApprox(testscale)
        assert result[0].name=="Major"

    def test_setscale(self):
        ws=WesternScales()
        ws.setScale("Diminished Whole Half","{0, 2, 3, 5, 6, 8, 9,11}",1)
        assert ws.intscales["Diminished Whole Half"]==[0, 2, 3, 5, 6, 8, 9, 11]
        result=ws.compareAllScalesApprox([2, 3, 5, 6, 8, 9,11, 0])
        assert result[0].name=="Diminished Whole Half"



if __name__ == '__main__': 
    unittest.main()
    
