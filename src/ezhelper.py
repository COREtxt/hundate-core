''' Alapszintű helper függvények:  stingkezelés (pl. text2int, d_annotate, d_lookup), tömbök és szótárak kezelése, fájlrendszer, debug
''' 

from time import process_time,perf_counter
import os
from itertools import groupby
import string
import math
import numpy as np
import re


def stopperstart():
    return process_time()

def stopper(process_time_start):
    '''
    Előtte:  t=stopperstart()       stopper(t)     
    A nettó processzor-időt adja vissza sec-ban (sleep nélkül)
    Másik lehetőség:   perf_counter()   -   a teljes eltelt idő sec-ban (általában lényegesen nagyobb)
    '''
    print('process_time: ' + str(process_time()-process_time_start))


def fn_round(n, decimals=0):
    ''' Ez felel meg a standard kerekítési szabálynak (>=0.5 esetén felfelé egyébként lefelé; negatív esetén az abszolút értékre vonatkozik)
    A python round() függvénye bizonyos pontokon eltér ettől (pl. 2.5 esetén 2-t ad a kerekítés, más esetekben viszont rendben van).
    Ennek az a törekvés a magyarázata, hogy a python a lehető legkisebb eredő kerekeítési hibát próbálja meg elérni.
    '''
    multiplier = 10 ** decimals
    rounded_abs=np.floor(abs(n)*multiplier + 0.5) / multiplier
    return math.copysign(rounded_abs, n)



def kodto(kod,kodlista):
    ''' Szerializált dictionary, nem túl nagy kódlistákra 
    kodlista:  "kod:felirat//..."  
    '''
    if not kod: return ''
    if not kodlista: return ''
    if type(kod)!=str: kod=str(kod) 
    kereső=kod+':'
    nLen=len(kereső)
    aSor=kodlista.split('//')
    for sor in aSor:
        if sor[:nLen]==kereső: return sor[nLen:]
    return ''


def beginwith(strIn,samples,replace=None):   # -> found_sample vagy ''     replace esetén a cserével létrejövő string
    ''' samples:  minták | jeles felsorolása   példa:  'ki|be'
      FIGYELEM:  pont, zárójel és egyéb regex karakterek elé kötelezően '\' kell   (pl. r'\.')
    return:  üres vagy a talált minta
    process_time: mikrosec körül
    '''
    m=re.search(r'\A(' + samples + ')',strIn)
    if m==None: 
        if replace!=None: return strIn
        else: return ''
    else: 
        found=m.group()
        if replace!=None: return replace + strIn[len(found):]
        else: return found 


def endwith(strIn,samples,replace=None):   # -> found_sample vagy ''     replace esetén a cserével létrejövő string
    ''' samples:  minták | jeles felsorolása   példa:  'tól|től'
      FIGYELEM:  pont, zárójel és egyéb regex karakterek elé kötelezően '\' kell   (pl. r'\.')
    return:  üres vagy a talált minta
    process_time: mikrosec körül
    '''
    m=re.search('(' + samples + r')\Z',strIn)
    if m==None: 
        if replace!=None: return strIn
        else: return ''
    else: 
        found=m.group()
        if replace!=None: return strIn[:len(strIn)-len(found)] + replace
        else: return found 


def vanbenne(strIn,samples):
    ''' samples:  minták | jeles felsorolása   példa:  'dika|dike'
    return:  üres string vagy a talált minta  (ha több minta is jó, akkor a strIn-ben előrrébb álló minta)
    process_time: mikrosec körül
    '''
    m=re.search(r'(' + samples + ')',strIn)
    if m==None: return ''
    else: return m.group()

def cutleft(strIn,strCut):
    # Nem ellenőrzi, hogy valóban a strCut-tal kezdődik-e, egyszerűen levágja az elejéről a strCut hosszának megfelelő karaktereket
    return strIn[len(strCut):]

def trim(str):
    ''' strip a széleken + ismétlődő space-k törlése belül 
    Minden whitespace-re kiterjed  (a kimenetben csak space maradhat)
    '''
    return ' '.join(str.split())


def clean(str,accentlevel='soft',bDropSpaces=False):
    ''' lower, hosszú ékezet helyett rövid ékezet (a-á, e-é, o-ö, u-ü nincs összevonva), írásjelek törlése  (betűk és számjegyek maradnak)
    bDropSpaces:   True esetén a whitespace-ek teljes törlése, False esetén csak trim (a belső szóközök megmaradnak, az írásjelek helyett space)
    accentlevel: '': nincs összevonás,  'soft':  a-á, e-é, o-ö, u-ü nincs összevonva,    'hard':  erős összevonás
    '''
    if accentlevel=='hard':
        s1='áéíóöőúüű'
        s2='aeiooouuu'
    elif accentlevel=='soft':
        s1='íóőúű'
        s2='ioöuü'
    else:
        s1=''
        s2=''
    
    if bDropSpaces:
        str=str.translate(str.maketrans(s1,s2,string.punctuation + string.whitespace))
        return str.lower()
    else:
        str=str.translate(str.maketrans(string.punctuation,' '*len(string.punctuation)))   # írásjelek helyett szóközök
        str=str.translate(str.maketrans(s1,s2))
        str=' '.join(str.split())
        return str.lower()

def skipaccents(str,level='soft'):
    ''' Ékezetek elhagyása
    level:
       'soft':  csak a hosszú ékezeteket cseréli rövidre,  a-á, e-á, o-ö, u-ü eltérés megmarad
       'hard':  minden ékezetet elhagy
    '''
    if level=='soft':
        return str.translate(str.maketrans('íóőúűÍÓŐÚŰ','ioöuüioöuü'))
    elif level=='hard':
        return str.translate(str.maketrans('áéíóöőúüűÁÉÍÓÖŐÚÜŰ','aeiooouuuaeiooouuu'))
    else:
        return str


def splitfirst(str,separator=None):
    '''  Hívása:  first,second = splitfirst(str,',') 
    Ha nincs benn határolójel, akkor a második változóba '' értéket ad vissza
    '''
    array=str.split(separator,1)
    if len(array)>1: return array[0],array[1]
    elif len(array)==1: return array[0],''
    else: return '',''

def text2int(text,bSerialOk=True,bCleaned=False,tupleout=False):
    ''' 
    text:  számjegyek, szövegesen kiírt szám vagy sorszám, római szám ('nulla', 'százhuszonöt',  max 999 billió)
       Példa:  "123"  "MCMLII", "háromezertizenkettő", "százhamincadik", "tizenkettes"  
       Általában egyetlen szó, de állhat több szóból is.
       case-insensitive, accent-insensitive, whitespace és írásjel érdektelen, szöveges változatnál szótövesít
       Érdemi elgépelések nem megengedettek (nem fuzzy jellegű)
       Nem lehet benne idegen szó (csak számjegyek, számszavak, római szám karakterek, ragok)
    bSorszamOk:  megengedett-e sorszám is  (az out ebben az esetben is egy szám lesz)
    bCleaned:   előzetes szabványosítás megtörtént-e  (egyetlen szó, lower, ékezet-összevonás).  30-40% gyorsulás érhető el 
    tupleout:  True esetén   (n,type)  a result, ahol type = 'szám', 'rómaiszám', 'sorszám'

    Result:  0-999 billió   -1 ha nem ismerhető fel számként
    process_time: 15 microsec körül   (ebből a fele idő a clean)

    '''


    def sub(nOut,tipus=''):
        if tupleout: return nOut,tipus
        else: return nOut


    if text=='': return sub(-1)

    # a szélekről mindenképpen el kell tüntetni a whitespace-eket és pontokat (pont megengedett a végén)
    text=text.strip('. ')
    if text=='': return sub(-1)

    # ha számjeggyel vagy '-' jellel kezdődik
    c=text[0]
    if c=='-' or c in string.digits:
        try:
            nOut=int(text)
            return sub(nOut,'szám')
        except:
            return sub(-1)


    # Próbálja meg római számként értelmezni (csak nagybetűket fogad el, és pont lehet a végén)
    nOut=romaiszam2int(text)
    if nOut>0: return sub(nOut,'rómaiszám')

    if not bCleaned:
        text=clean(text,'hard',True)        # accent hard, ne maradjon whitespace   (viszonylag időigényes, kb 5 mikrosec)
        if text=='': return sub(-1)

    typeout='szám'
    # Ha sorszám is megengedett
    if bSerialOk and ('dik' in text or 'els' in text or endwith(text,'s|stol|sig|son|sen|sban|sben')):
        # lemmatizálás  (nem minden rag, elsősorban a dátumokban előforduló számokra van kiélezve)
        if 'dik' in text: text=endwith(text,'dika|dike|diki|dikai|dikei|dikan|diken|dikaig|dikeig|dikatol|diketol|dikos|dikes|dikas','dik')
        elif 'els' in text: text=endwith(text,'elsotol|elson|elsoig|elseje|elsejen|elsejei|elsejeig|elsejetol','elso')
        else: text=endwith(text,'stol|sig|son|sen|sban|sben','s')    # huszastól << huszas
        
        d={ 'elso':'egy','egyedik':'egy','egyes':'egy','masodik':'ketto','kettedik':'ketto','kettes':'ketto',
            'harmadik':'harom','harmas':'harom','negyedik':'negy','negyes':'negy',
            'otodik':'ot','otos':'ot','hatodik':'hat','hatos':'hat','hetedik':'het','hetes':'het',
              'nyolcadik':'nyolc','nyolcas':'nyolc','kilencedik':'kilenc','kilences':'kilenc',
            'tizedik':'tiz','tizes':'tiz','huszadik':'husz','huszas':'husz','harmincadik':'harminc','harmincas':'harminc',
              'negvenedik':'negyven','negyvenes':'negyven','otvenedik':'otven','otvenes':'otven',
              'hatvanadik':'hatvan','hatvanas':'hatvan','hetvenedik':'hetven','hetvenes':'hetven',
              'nyolcvanadik':'nyolcvan','nyolcvanas':'nyolcvan','kilencvenedik':'kilencven','kilencvenes':'kilencven',
            'szazadik':'szaz','szazas':'szaz','ezredik':'ezer','ezres':'ezer','milliomodik':'millio','millios':'millio',
              'milliardodik':'milliard','milliardos':'milliard','billiomodik':'billio','billios':'billio'}
        for key,value in d.items():
            if text.endswith(key): 
                text=text[:-len(key)]+value
                typeout='sorszám'
                break


    nOut=0
    if text in ['null','nulla','zero']: return sub(0,'szám')

    numwords=[('billio',1000000000000),('milliard',1000000000),('millio',1000000),('ezer',1000),('szaz',100)]
    for numword,numvalue in numwords:
        nPos=text.find(numword)
        if nPos>-1:
            # előtte 1-999 szám állhat (kivéve a "száz" előtt: 1-9)
            nelottemax=999
            if numvalue==100: nelottemax=9

            elotte=text[:nPos]
            if elotte=='': nelotte=1
            else: nelotte=text2int(elotte)          # rekurzív hívás

            if nelotte<1 or nelotte>nelottemax: return sub(-1)
            nOut+=nelotte*numvalue
            text=text[nPos+len(numword):]       # a felhasznált rész levágása

    if text:
        dTizesek={'tizen':10,'tiz':10,'huszon':20,'husz':20,'harminc':30,'negyven':40,'otven':50,'hatvan':60,'hetven':70,'nyolcvan':80,'kilencven':90}    
        key,out = d_lookup(text,dTizesek,True)
        if out: 
            nOut+=out
            text=text[len(key):]      # a felhasznált rész levágása


    if text:
        dEgyesek={'egy':1,'ketto':2,'ket':2,'harom':3,'negy':4,'ot':5,'hat':6,'het':7,'nyolc':8,'kilenc':9}
        nEgyesek=dEgyesek.get(text)
        if nEgyesek==None: return sub(-1)
        nOut+=nEgyesek

    if nOut==0: return sub(-1)
    
    return sub(nOut,typeout)


def romaiszam2int(text):
    ''' Ha nem római szám, akkor 0
    Csak nagybetűk megengedettek'''

    roman_numerals = {'I':1, 'V':5, 'X':10, 'L':50, 'C':100, 'D':500, 'M':1000}
    result = 0
    try:
        for i,c in enumerate(text):
            if (i+1) == len(text) or roman_numerals[c] >= roman_numerals[text[i+1]]:
                result += roman_numerals[c]
            else:
                result -= roman_numerals[c]
    except:
        result=0

    return result


def fileexists(path):
    return os.path.exists(path)


def unzip(aRecord,nCol=None):
    # Általános függvény
    #   aX,aY=unzip(aXy)
    #   aZ=unzip(aXyz,2)        - a nCol 0-bázisú
    # A visszaadott tömbök valójában tuple-ök. Ha a tömbelemek módosítására van szükség, akkor a list(aX) művelettel át kell térni listára.
    # Inverz művelet:   aRec=list(zip(aX,aY))
    if nCol: return list(zip(*aRecord))[nCol]
    else: return zip(*aRecord)

def sortrecords(aRec,byindex,reverse=False,outindex=None):
    # inplace rendezés a byindex sorszámú oszlop szerint
    # outindex:  visszaadja a rendezett aRec megadott sorszámú oszlopát (list)
    # FIGYELEM:  az np.nan értékekre rosszul rendez (ne legyen nan a rendezési oszlopban)
    #  - stringoszlop esetén az '' rendezési érték a végére kerül (itt nincs gond)
    aRec.sort(key = lambda x: x[byindex],reverse=reverse)
    if outindex!=None: return list(zip(*aRec))[outindex]

def sortarrays(aSorter,aToSort,reverse=False):
    # Az aSorter értékei alapján rendezi mindkét tömböt (inplace jellegű)
    aRec=list(zip(aSorter,aToSort))
    aRec.sort(key = lambda x: x[0],reverse=reverse)
    aSorter2,aToSort2=unzip(aRec)
    for i in range(len(aSorter2)): aSorter[i]=aSorter2[i]
    for i in range(len(aToSort2)): aToSort[i]=aToSort2[i]


def grouprecords(aRec,keylambda):
    # Rekordok csoportosítása egy kulcs szerint
    # - a kulcs általában egy kategória-mező:   keylambda = lambda x:x[0]
    # - a kategóriák képezhetők egy vagy több folytonos értékkészletű mező alapján is
    #   Példa: egy datetime mező kategorizálása aszerint, hogy melyik évbe esik    keylambda = lambda x: x[2].year
    # Előfeltétel:  from itertools import groupby
    
    # aRec:  list of tuple
    # keylambda:  átlalában egy lambda függvény, ami minden rekordhoz hozzárendeli a rendezési kulcsértéket

    # return:  két-elemű iterátor
    #   for key, records in grouprecords(aRec,lambda x:x[0])
    #      print(key)
    #      print(list(records))                     - a records szintén egy iterátor
    #      for rec in records: print(rec)

    aRec.sort(key=keylambda)        
    return groupby(aRec,keylambda)


def ddef(**fields):
    ''' Egy dictionary megadása függvény-arg formátumban
    Előnye a normál szintaxishoz képest:  áttekinthetőbb és nem kell idézőjelezni az adatneveket (csak egy-szavas adatnevekre jó)
    Példa:
        dict1 = { 'suptitle':'Felső sor', 'title':'Alsó sor' }
        dict1 = ddef( suptitle='Felső sor', title='Alsó sor' )
    '''
    return dset({},**fields)

def dget(dict,fields):
    # Többmezős unpacking dictionary-re   (nincs ilyen közvetlen művelet)
    #      Példa:   a,b,c = dget(dict,'a,b,c')
    #  fields:  lista vagy felsorolásos string (vessző határolással)
    #      - ha hiányzik valamelyik mezőnév, akkor None kerül a változóba  (nincs hibaüzenet)
    #      - default érték itt nem kell, a dictionary get függvénye eleve tudja
    if type(fields)==str: fields=fields.split(',')
    if len(fields)==1: return dict.get(fields[0])           # ilyenkor ne tuple-t adjon vissza
    elif len(fields)>0: return tuple(map(dict.get,fields)) 

def dset(dict,**fields):
    '''
    fields:  fieldname1=value1,fieldname2=value2, ....    
      - megadható közvetlenül vagy egy dict objektumként
      - közvetlen megadás esetén a mezőnevekhez nem kell idézőjel   (több szavas mezőnevekre nem működik)
      - ha valamelyik mezőnév hiányzik, akkor automatikus felvétel
      - None értékadás nem törli automatikusan a mezőt (None érték íródik be)
    '''
    aField=list(fields.keys())
    aValue=list(fields.values())
    for i in range(len(aField)): 
        dict[aField[i]]=aValue[i]
    return dict

def dsetsoft(dict,**fields):
    '''
    Soft:
      - csak akkor módosít, ha nincs még ilyen mező a dict-ben vagy None az értéke.
      - None értéket semmiképpen nem ír be
    fields:  fieldname1=value1,fieldname2=value2, ....    
      - megadható közvetlenül vagy egy dict objektumként
      - közvetlen megadás esetén a mezőnevekhez nem kell idézőjel   (több szavas mezőnevekre csak egy módosító dict működik)
      - ha valamelyik mezőnév hiányzik, akkor automatikus felvétel
    '''
    aField=list(fields.keys())
    aValue=list(fields.values())
    for i in range(len(aField)):
        if aValue[i]==None or dget(dict,aField[i])!=None: continue
        dict[aField[i]]=aValue[i]


def d_addhard(dict,key,value):
    ''' Akkor is hozzáadja az értéket a dict-hez, ha van már ilyen key, de ilyenkor sorszámozza a kulcsot.
    return:  a felvett tétel kulcsa  (sorszámozásban térhet el az input key-től)
    Nagy tömegű sorszámozás esetén is viszonylag gyors, mert az eddigi lemgmagasabb szorszámú kulcsot binárisan keresi.
    '''
    
    if key=='': return ''
    # ellenőrzés: van-e már ilyen kulcs
    keyout=key
    if dict.get(keyout):
        i = 2

        # First do an exponential search
        while dict.get(key+str(i)):
            i = i * 2

        # Result lies somewhere in the interval (i/2..i]
        # We call this interval (a..b] and narrow it down until a + 1 = b
        a, b = (i // 2, i)
        while a + 1 < b:
            c = (a + b) // 2 # interval midpoint
            a, b = (c, b) if dict.get(key+str(c)) else (a, c)

        keyout=key+str(b)

    dict[keyout]=value

    return keyout


def d_lookup(strIn,d_samples,tupleout=False,bWholesamples=True):
    ''' Alapesetben beginwith minták, de a d_samples teljes-egyezéses mintákat is tartalmazhat
    Beginwith minták esetén a leghosszabb minta érvényesül (a strIn a talált mintával kezdődik)
    Ha van találat, akkor az adott kulcs-hoz tartozó value-t adja vissza (a tupleout-tal kérhető a kulcs,values pár is return-kétn)
    Ha nincs találat, akkor None
    strIn: általában egyetlen szó   (szavanként, vagy néhány szavas ablakokkal kell hívni a függvényt)
    d_samples:   {[keresőszó]:[value],...}         A keresőszó string, a value lehet szám is vagy akár egy sub dictironary
       - a keresőszavakban csak számok és betűk lehetnek
       - a keresőszavak végén lehet egy pont:  teljes-egyezéses minta   (ha nincs pont, akkor beginwith egyezés is jó)
       
    tupleout: True esetén return (key,value).    A key lehet több szavas  (az esetleges lezáró pont nélkül adja vissza a függvény)
    bWholesamples:  vannak-e teljes-egyezéses minták is a d_samples-ben (pont a keresőszó végén) 
    process_time:   2 microsec     50-es dict, átlagos szó (nem talál)     Feltehetően nagy dict-re is gyors (hash index)
    '''
    
    result=None

    tosearch=strIn

    if bWholesamples:
        tosearch=tosearch.replace(' ','.') + '.'
        
        #result=d_samples.get(tosearch + '.')
        #if result: 
        #    if tupleout: return tosearch,result
        #    else: return result

    # Keresés hosszrövidítésekel (a leghosszabb keresőminta érvényesül)
    while len(tosearch)>1:
        result=d_samples.get(tosearch)
        if result: 
            if tupleout: 
                tosearch=tosearch.replace('.',' ')
                if tosearch[-1]==' ': tosearch=tosearch[:-1]
                return tosearch,result
            else: return result
        tosearch=tosearch[:-1]

    #if result:
    #    if tupleout: return tosearch,result
    #    else: return result
    #else:
    if tupleout: return None,None
    else: return None


       

def d_annotate(strIn,lookup,special='[szám] [tólig]',max_words_in_samples=2,accentlevel='soft'):    # -> pattern,invalues,outvalues
    ''' Annotálás jellegű művelet. A szöveg mintázatát állítja elő.  
    A beazonosítható szövegrészek helyébe szögletes zárójelben az entity-nevét írja, az eredeti és a szabványosított értéket pedig 
        menti az invalues és outvalues tömbbe (a két tömb indexelése a pattern-be kerülő "[...]" helyettesítőjelekhez igazodik) 

    strIn:  általában több szavas kifejezés vagy mondat.    
        Nem kell előzetesen szabványosítani (a jelen függvényben: lower, trim, skipaccents, skippunctuations)
    lookup:   {'[startsamples]':'[entity],[value]', ...}
        - [startsamples]: több keresőminta is megadható | határolással.  Példa:  'múlt|elmúlt|előző|legutóbbi'
                A sorrend érdektelen, mindig a lehetséges leghosszabb találat érvényesül ("tavasszal" akkor is talál, ha a "tavasz" minta előrébb áll)
                A keresőminták több szavasak is lehetnek (trimmelve kell megadni)
                Ha egy keresőminta végén pont van, akkor csak wholeword találat megengedett  (egyébként beginwith találat is jó)
        - [entity]:  entity-név (pl. "évszak"). Kötelezően egyszavas  ('_' lehet benne)  
                Ugyanaz az entitás-név több startsamples-höz is megadható.  Tetszőleges számú entitásnév lehet a lookup-ben.
                "none" entitást kell megadni, ha csak szabványosításról illetve szinonimák összevonásáról van szó
                  Példa:  "korábbi|előző":none,korábbi.     Ebben az esetben csere a szabványosított értékre, az outvalues-be nem kerül bele
                "stopword" entitás-névvel kell felsorolni az elhagyandó szavakat (pl. névelők)
        - [value]:  ez az érték kerül be az outvalues-be (az adott entity névvel). Szabványosított / kivonatolt érték
                Ha nincs megadva, akkor a talált startsample lesz a szabványosított érték
                Lehet szám, dátum, string is.  String esetén több szavas is lehet (trimmelve kell megadni)
    special:  példa: '[szám] [tólig]'   speciális beazonosítási eljárások felsorolása (a határolójel és a sorrend érdektelen)
        [szám]:  a szöveges vagy numerikus szám-szavak annotálása "[szám]" entity-névvel (sorszámok és római számok is)
        [tólig]:  a -tól -től -ig ragok leválasztása külön szóként (egybeírt és kötejeles írásmód esetén is)
    max_words_in_samples:  maximum hány szavas minták vannak a lookup-ben
        - az ennél hosszabb (ennél több szóból álló) minták nem fognak találatot adni 
    accentlevel:     '': nincs összevonás,  'soft':  a-á, e-é, o-ö, u-ü nincs összevonva     'hard':  erős összevonás
      

    return   pattern,invalues,outvalues
                pattern:    példa:  "[entity1] egyébszó [entity2]"
                invalues:   az annotált részek eredeti értéke  (a fenti pattern-példához 2-elemű lista tartozik)
                outvalues:  az annotált részek kimeneti értéke  (a fenti pattern-példához 2-elemű lista tartozik)
    '''

    invalues=[]
    outvalues=[]

    # key-felsorolások kibontása (ha nincs még kibontva;  a lookup egy globális objektum, amit egyszer kell csak kibontani)
    if not lookup.get('d_compiled'):
        dict_compiled={'d_compiled':True}     # a d_compiled adat helyből beállítva
        for key,value in lookup.items():
            subkeys=key.split('|')          # több keresőminta is felsorolható '|' határolással
            for subkey in subkeys: 
                if subkey: 
                    subkey=subkey.lower()
                    subkey=skipaccents(subkey,accentlevel)
                    # írásjelek helyett szóközök (kivéve '.')
                    #strL=strL.translate(str.maketrans(dropchars,' '*len(dropchars)))

                    subkey=subkey.replace(' ','.')       # a több szavas keresőmintákban "." kell a szóközök helyett (technikai oka van)
                    dict_compiled[subkey]=value
        lookup=dict_compiled
    

    strL=strIn

     # ".-"  helyet "-"     Példa:   "5.-én": ne tekintse sorszámnak  (egy helyesírási hiba kijavításáról van szó)
    strL=strL.replace('.-','-')

    # szeparátor írásejelek helyett egységesen "vessző", külön szóban. Nem annotált szóként tagoló szerepe lesz.
    #   vessző, pontosvessző, kettős-perjel, függőleges-tagolóvonal
    strL=strL.replace(',',' vessző ')
    strL=strL.replace(';',' vessző ')
    strL=strL.replace(r'//',' vessző ')
    strL=strL.replace(r'|',' vessző ')

    # írásjelek helyett szóközök (kivéve '.')
    dropchars=string.punctuation.replace('.','')        # a ponton kívüli összes írásjel
    strL=strL.translate(str.maketrans(dropchars,' '*len(dropchars)))
    # pontok helyett pont + space  (külön szavak legyenek, de a szóvégi pontok örződjenek meg. A számok esetén fontos, hogy van-e pont a végén)
    strL=strL.replace('.','. ')
    
#    strL=strL.lower()   
    strL=skipaccents(strL,accentlevel)
    
    if '[tólig]' in special:
        strL=re.sub(r'(-jétöl|-átol|-étöl|-tol|-töl|tol|töl)\b',r' tol',strL)   # szóköz kerül elé, külön szó lesz
        strL=re.sub(r'(-jéig|-áig|-éig|-ig|ig)\b',r' ig',strL)


    # trim
    words=strL.split()

    # magában álló pontok elhagyása (nem volt előtte alfanum, érdektelen)
    wordsout=[]
    for word in words:
        if word=='.': continue
        wordsout.append(word)
    words=wordsout
    
    # Keresés szavanként (vagy pár szavas csúszóablakkal) a mintákat tartalmazó dict-ben  (like: karakter-elhagyások a végéről)
    wordsout=[]
    nLen=len(words)
    i=0
    while i<nLen:
        if '[szám]' in special:
            word=words[i]     # a számoknál csak egyszavas keresés van
            if word!='hét':   # a "hét" szó helyébe ne írjon számot (összetéveszthető a "hét" időhatározóval)
                              # Később még ellenőrzöm, hogy ha [időtartam] a következő szó is, akkor [szám]-ra módosuljon az értelmezése (pl. "hét nap")
                n=text2int(word,True,False)
                if n>-1:
                    # ha számjegyekből áll a szám, és a következő szó egy rag, akkor olvassza be a számba
                    #  ragot
                    if word.isnumeric() and i<nLen-1:
                        wordnext=words[i+1]
                        if wordnext in ['án','én','ján','jén','i','ai','ei','jei','os','as','es','ös',
                                'dikán','dikén','diki','dikei','dikai','dikos','dikas','dikes',
                                't','et','at','dikát','dikét',          # "5-öt" nem kezelhető, mert számmal összetéveszthető 
                                'diká','diké']:     # tól, től ig le lett vágva
                            word=word + wordnext
                            i+=1

                    invalues.append(word)
                    outvalues.append(n)
                    wordsout.append('[szám]')
                    i+=1
                    continue

        # max_words_in_samples szóra kell keresni (ha van még ennyi szó)
        i2 = i + max_words_in_samples
        if i2>nLen: i2=nLen
        tosearch=' '.join(words[i:i2]).lower()
        
        key,foundvalue=d_lookup(tosearch,lookup,True)
        if foundvalue:
            # hány szavas a találat (ennyi szó lesz lecserélve a helyettesítőjellel)
            nFoundWords=len(key.split())
            
            entity,value=splitfirst(foundvalue,',')
            if entity=='stopword': wordout=''
            else:
                if value=='': value=key
                if entity!='none': 
                    # Ha az előző szó is [időtartam] volt "hét" input-értékkel, akkor előző szó legyen számként annotálva (pl. "hét nap" "[szám] [időtartam]"
                    #   Ellenpélda: "utolsó hét az évben"   "az év" külön minta
                    if (entity=='időtartam' and len(wordsout)>0 and wordsout[-1]=='[időtartam]' 
                        and invalues[-1]=='hét' and not words[i] in ['a','az']):
                        wordsout[-1]='[szám]'
                        outvalues[-1]=7
                    if entity=='szám': value=int(value)
                    invalues.append(' '.join(words[i:i+nFoundWords]).lower())
                    outvalues.append(value)
                    wordout='[' + entity + ']'
                # Ha a keresőmintához "none" lett megadva entitásként, akkor nem helyettesítőjellel, hanem a szabványosított értékkel
                #    kell lecserélni a találatot eredményező szövegrészt  (a value több szavas is lehet) 
                else:
                    wordout=value
            i += nFoundWords

        else: 
            # Ha nincs találat, akkor egyetlen szó kerül be a wordsout-ba (változtatás nélkül), majd lépés a következő szóra
            wordout=words[i]
            i+=1



        if wordout!='': wordsout.append(wordout)
    



    #for word in words:
    #    if word=='.': continue   # a . előtt nem volt alfanum (érdektelen)

    #    if bNum:
    #        if word!='hét':   # a "hét" szó helyébe ne írjon számot (összetéveszthető a "hét" időhatározóval)
    #                          # Később még ellenőrzöm, hogy ha [időtartam] a következő szó is, akkor [szám]-ra módosuljon az értelmezése (pl. "hét nap")
    #            n=text2int(word,True,False)
    #            if n>-1:
    #                invalues.append(word)
    #                outvalues.append(n)
    #                wordsout.append('[szám]')
    #                continue

    #    key,foundvalue=d_lookup(word,lookup,True)
    #    if foundvalue:
    #        entity,value=splitfirst(foundvalue,',')
    #        if entity=='stopword': wordout=''
    #        else:
    #            if value=='': value=key
    #            if entity!='none': 
    #                # Ha az előző szó is [időtartam] volt "hét" input-értékkel, akkor előző szó legyen számként annotálva (pl. "hét nap" "[szám] [időtartam]"
    #                if entity=='időtartam' and len(wordsout)>0 and wordsout[-1]=='[időtartam]' and invalues[-1]=='hét':
    #                    wordsout[-1]='[szám]'
    #                    outvalues[-1]=7
    #                if entity=='szám': value=int(value)
    #                invalues.append(word)
    #                outvalues.append(value)
    #                wordout='[' + entity + ']'
    #            else:
    #                wordout=value
    #    else: wordout=word



    #    if wordout!='': wordsout.append(wordout)
    
        
    pattern=' '.join(wordsout)
    return pattern,invalues,outvalues

   
    # B VÁLTOZAT:  mintánként scan a teljes szövegre
    #for regex,data in d_regex:
    #    value0=clean(regex,'',False)
    #    if regex.endswith('*'): regex=regex[:-1]
    #    else: regex=regex + r'\b'
    #    if regex.startswith('*'): regex=regex[1:]
    #    else: regex=r'\b' + regex
    #    regex=regex.replace('*','.*')

    #    entity,value=splitfirst(data,',')
    #    if value=='': value=value0

    #    re.sub(regex,entity,strIn)

    return



def stringadd(str,stradd,sep=','):
    ''' NE HASZNÁLD   Régi vágású stringadd, nem túl sok részstringre;  NINCS INPLACE VÁLTOZAT, lines = stringadd(lines,line,'\n') utasítás kell.
    Korábbi programkódok migrációjához lehet szükséges 
      (a régi módszer bizonyos esetekben kevesebb programsort igényelt, könnyebben át lehetett tekinteni, de kevésbé rugalmas és lassabb volt)
    A Python stringek esetén nem oldható meg az "inplace" (var argumentumos) értékadás   (bytearray objektummal sem) 
    A standard python megoldás összehasonlítása a régi típusú stringadd algoritmussal:
        lines=[]                                lines=''
        for ...:   lines.append(line)           for ...:   stringadd(lines,line,'\n')     // a python-ban csak a lines=stringadd(lines,line,'\n') működik
        '\n'.join(lines)                        lines
    '''
    if str: return str + sep + stradd 
    else: return stradd


def joinlines(lines):
    return '\n'.join(lines)         # régi vágású helper függvény




def FvNumformat(format,var=''):
    # str.format függvény paraméterezése.  
    # var: általában üres;  a diagram-jelölők formázásakor 'x' kell.
    if format[:3]=='{' + var + ':': return format                             # ha teljes formátum van megadva
    elif format==',': return '{' + var + ':,}'                                # ezres tagolás
    elif format[-2:]=='f%': return '{' + var + ':.' + format[:-2] + 'f}%'     # közvetlen százalék (bázis=100)
    else: return '{' + var + ':,.' + format + '}'                             # pl. '2f'  '3g'   '5e',  '0%'


