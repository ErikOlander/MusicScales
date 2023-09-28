
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
        assert MusicalScale.scaleString2integerList("A♯2 , A♭, B ")==[10,8, 11]
        assert MusicalScale.scaleString2integerList("A#2 - A - B ")==[10,9, 11]

class WestenScalesTest(unittest.TestCase):
    def test_setscale(self):
        ws=WesternScales()
        ws.setScale("DiminishedSeventh","{0, 3, 6, 9}")
        assert ws.intscales["DiminishedSeventh"]==[0, 3, 6, 9]

    def test_matchscale(self):
        ws=WesternScales()
        testscale=ws.scaleString2integerList("C D E F G")
        result=ws.compareAllScalesApprox(testscale)
        assert result[0].name=="Major"


if __name__ == '__main__': 
    unittest.main()
    
