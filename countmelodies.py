from musicalscales import MusicalNote,MusicalScale,WesternScales
import itertools


ws=WesternScales()

validScales=[]
total=0
for i in range(12):
    for scale in itertools.combinations(range(12), i):
        total+=1
        result=ws.compareAllScales(scale,1)
        if len(result)>0:
            validScales.append(scale)


print(total)
print(len(validScales))