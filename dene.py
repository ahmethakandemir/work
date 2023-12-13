import json


mydict = {
    'a' : {},
    'b' : {},
    'c' : {},
    'd' : {},
    'e' : {},
    'f' : {},
    'g' : {},
    'h' : {},
    'i' : {}
}
aileler = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
ailelerkullanilacak = ['a', 'b', 'c', 'd', 'e1', 'e', 'f', 'g', 'h', 'h1', 'i']
ailelerayni = ['e1', 'h1']
aileasil = ['e', 'h']

for aile in ailelerkullanilacak:
    if aile in ailelerayni:
        seri = aile
        indexi = ailelerayni.index(aile)
        aile = aileasil[indexi]
        
    else:
        seri = aile
        
    mydict[aile][seri] = {
            'seriadi' : aile,
        }    

dict = json.dumps(mydict, indent=4)
print(dict)
