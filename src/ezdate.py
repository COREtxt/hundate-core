''' NLP modul for hungarian date-entity recognition and translation to specific date values
NLP modul, magyar nyelvű dátum-kifejezések felismerése és lefordítása konkrét dátum-értékekre.
A legfontosabb függvény a modulban:  text2date( )    (a többi függvény helper jellegű)
Paraméterezési lehetőség  (mindkettő a modul végén): 
   pattern2method:   mintázatok
   lookup_text2dateG:  annotáláshoz szükséges lookup-szótár
Részletes leírás:  https://github.com/COREtxt/hundate-core
''' 

from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta

try:
    from ezhelper import *
except:
    from .ezhelper import *     # ha csomagban van telepítve (pip install hundate)

# Általános dátumkezelő helper függvények
def fn_today(format='.'):
    # date.today() is jó
    if format=='c10.' or format=='.':
        return datetime.now().strftime('%Y.%m.%d')
    elif format=='c10-' or format=='-':
        return datetime.now().strftime('%Y-%m-%d')
    elif format=='c8':
        return datetime.now().strftime('%Y%m%d')

def fn_dateadd(dt,nToAdd,unit='day'):
    if nToAdd==0: return dt
    if unit=='month':
        return dt + relativedelta(months=nToAdd)
    elif unit=='year':
        return dt.replace(year=dt.year+nToAdd)
    elif unit=='week':
        return dt + timedelta(weeks=nToAdd)
    elif unit=='day':
        return dt + timedelta(days=nToAdd)
    elif unit=='workday':
        # Lépj a megadott sorszámú munkanaphoz (a visszadott nap mindenképpen hétköznap lesz, kivéve a nToAdd=0 esetet, amikor nem történik semmi)
        # Az ünnepnapokat nem figyeli, csak a hétvégi napok kihagyásáról van szó (munkanap helyett "hétköznap" a találóbb kifejezés)
        bVissza=False
        if nToAdd<0:
            bVissza=True
            nToAdd=-nToAdd
        nToAddL= nToAdd//5 * 7
        rest=nToAdd % 5
        weekday=dt.weekday()    # 0 bázisú
        if bVissza:
            # ha dt hétvégére esik, akkor az utána álló első munkanapra kell lépni
            if weekday>4: 
                nToAddL=nToAddL - (7-weekday)
                weekday=0
            restOk=0
            while restOk<rest:
                nToAddL+=1
                weekday-=1
                if weekday<0: weekday=6
                if weekday<5: restOk+=1
            return dt + timedelta(days=-nToAddL)

        else:
            # ha dt hétvégére esik, akkor vissza kell lépni az előtte lévő péntekre
            if weekday>4: 
                nToAddL=nToAddL - (weekday-4)
                weekday=4
            restOk=0
            while restOk<rest:
                nToAddL+=1
                weekday+=1
                if weekday>6: weekday=0
                if weekday<5: restOk+=1
            return dt + timedelta(days=nToAddL)

def fn_daydiff(dt1,dt2):
    return (dt1-dt2) / timedelta(days=1)

def fn_monthlastday(dt):
    # A megadott nap hónapjának utolsó napja
    return fn_dateadd(fn_dateadd(dt,1,'month'),-1)

def fn_monday(dt='today'):
    # A megadott nap hetének hétfői napja
    if dt=='today': dt=date.today()
    return fn_dateadd(dt,-dt.weekday())         # 0 bázisú

def fn_parsedate(strDate,format='.'):
    # Alapformátumok lefordítása datetime-ra
    # format: a strDate input formátuma
    #        '.'  'c10.'  '-' 'c10-'   'c8'  
    # return:  datetime vagy None
    if format=='c10.' or format=='.':
        return datetime.strptime(strDate,'%Y.%m.%d')
    elif format=='c10-' or format=='-':
        return datetime.strptime(strDate,'%Y-%m-%d')
    elif format=='c8':
        return datetime.strptime(strDate,'%Y%m%d')

# Függvény:  tesztek eredményének nyomtatás a konzolra
def fn_printteszt(címsor,tesztesetek,bSzegedAI):
    ''' Tesztek eredményének nyomtatás a konzolra (összehasonlítás is kérhető a hun_date_parser alkalmazással)'''
    print('\n\n' + címsor + '\n')
    for teszt in tesztesetek:
        try:
            hundate_out=text2date(teszt)
        except:
            hundate_out='(exception)'

        if bSzegedAI:
            try:
                hundate_szeged=''
                listL=text2datetime(teszt)
                if len(listL)>0:
                    dictL=listL[0]
                    date1=dictL['start_date']
                    hundate_szeged=date1.strftime('%Y.%m.%d')
                    date2=dictL['end_date']
                    s2=date2.strftime('%Y.%m.%d')
                    if s2>hundate_szeged: hundate_szeged=hundate_szeged + '-' + s2
            except:
                hundate_szeged='(exception)'
            print('"' + teszt + '"\n' +
                  '\t\t\t\t hundate:   ' + hundate_out + '\n' +
                  '\t\t\t\t szegedAI:  ' + hundate_szeged)
    
        else:
            teszt='"' + teszt + '"'
            if len(teszt)<30: teszt = teszt + ' '*(30-len(teszt))
            print(teszt + '\t' +  hundate_out)



# Elsődleges függvény (publikus interfész)
def text2date(text,dt0=None,tense='',outtype='first'):
    ''' Magyar nyelvű időmeghatározások lefordítása egy dátumra vagy dátum tartományra
    text:  általában több szavas
        A mondatban dátum-meghatározástól független szavak is lehetnek
    dt0:  relációs dátummeghatározások esetén a kiinduló dátum.
        Ha nincs megadva, akkor a mai nap.
    tense: 'future' / 'past'.  A nem egyértelmű időmeghatározások esetén jövőbeli vagy múltbeli dátumot preferáljon a függvény
        Ha üres, akkor az aktuális évben/hónapban/héten
    outtype:
      'first':    return =  '',   '2021.10.12',  '2021.12.10-2021.12.20'     Az első előforduló dátum vagy dátumtartomány.
      'first_tuple':  return = (datetime1, datetime2)    Az első dátum None, ha nem talált dátum-kifejezést. A második dátum csak időszak-kifejezése esetén nem None
      'first+':   ugyanaz mint a first, de a string végére beírja a pattern-t is   Példa: '2021.10.12   pattern: [szám] [hónapnév] [szám]
      'all':      '2021.10.12,2021.12.10-2021.12.20'
    '''
    
    def sub_findpattern(pattern,invalues,outvalues,dt0):
        # ciklus az ablakméretre:  összes szó, összes-1 szó, összes-2 szó, ...
        patternwords=pattern.split()
        nWords=len(patternwords)

        # invalues és outvalues összehangolása a patternwords-szel (nem azonos az elemszámuk)
        invalues_sync=[None]*nWords
        outvalues_sync=[None]*nWords
        i_value=0
        for i,patternword in enumerate(patternwords):
            if patternword[0]=='[':
                invalues_sync[i]=invalues[i_value]
                outvalues_sync[i]=outvalues[i_value]
                i_value+=1

        # Ablak-pásztázási ciklus
        nWindowLenMax=8        # ennél több szóból álló minták nem érvényesülnek (lásd pattern2method)
        if nWindowLenMax>nWords: nWindowLenMax=nWords

        for nWindowLen in reversed(range(nWindowLenMax+1)):   
            for nWindowStart in range(nWords-nWindowLen+1):
                # patternL,invaluesL,outvalues beállítása
                patternL=' '.join(patternwords[nWindowStart:nWindowStart+nWindowLen])

                method=pattern2method.get(patternL)
                if method:
                    # Argumentumok előkészítése

                    # today beállítása  (a "jövő" "múlt" "most" mindig erre hivatkozik)
                    if dt0==None: dt0=datetime.now()
                    methods.today=dt0
                    
                    # dt0 beállítása:  today az induló érték, de a beazonosított dátumok dinamikusan módosítják
                    #   A "következő", "előző", "ugyanabban", továbbá a hiányos dátumkifejezések erre hivatkoznak
                    # Ha van már előtte [dátum], akkor az lesz a viszonyítási alap
                    for i in reversed(range(nWindowStart)):
                        if patternwords[i]=='[dátum]':
                            dates=outvalues_sync[i]
                            dt1,dt2=dates
                            if dt1.year>1: dt0=dt1
                            elif dt2.year<9999: dt0=dt2
                            break
                    if dt0==None: dt0=datetime.now()
                    methods.dt0=dt0
                    
                    methods.tense=tense
                    methods.patternword_előtte=''
                    if nWindowStart>0: methods.patternword_előtte=patternwords[nWindowStart-1]
                    methods.patternword_utána=''
                    if nWindowStart+nWindowLen<nWords: methods.patternword_utána=patternwords[nWindowStart+nWindowLen]
                    invaluesL=[]
                    for value in invalues_sync[nWindowStart:nWindowStart+nWindowLen]:
                        if value: invaluesL.append(value)    # a None értékek nem kellenek
                    methods.invalues=invaluesL
                    outvalues=[]
                    for value in outvalues_sync[nWindowStart:nWindowStart+nWindowLen]:
                        if value: outvalues.append(value)   # a None értékek nem kellenek
                    methods.outvalues=outvalues

                    dates=method()

                     # Ha sikeres a beazonosítás
                    if dates and dates[0]:
                        foundpattern=patternL
                        date1,date2 = dates
                        if date2 and date2!=date1: foundpattern=foundpattern + '   ' + date1.strftime('%Y.%m.%d') + '-' + date2.strftime('%Y.%m.%d')
                        else: foundpattern=foundpattern + '   ' + date1.strftime('%Y.%m.%d')
                       

                        pattern=' '.join([*patternwords[:nWindowStart],'[dátum]',*patternwords[nWindowStart+nWindowLen:]])
                        pattern=trim(pattern)

                        # Az invalues-ba ne kerüljön be [dátum] mező, mert túl sok információt takarna el
                        words=patternL.split()
                        for i in range(len(words)):
                           if words[i]=='[dátum]':
                               patternL=patternL.replace('[dátum]',invaluesL[i])
                               break

                        invalues_sync=[*invalues_sync[:nWindowStart],patternL,*invalues_sync[nWindowStart+nWindowLen:]]
                        outvalues_sync=[*outvalues_sync[:nWindowStart],dates,*outvalues_sync[nWindowStart+nWindowLen:]]
                        invalues=[]
                        for value in invalues_sync:
                            if value: invalues.append(value)    # a None értékek nem kellenek
                        outvalues=[]
                        for value in outvalues_sync:
                            if value: outvalues.append(value)   # a None értékek nem kellenek
                        return (pattern,invalues,outvalues,foundpattern)
        return None


    # Annnotálás
    annotated_input,invalues,outvalues = d_annotate(text,lookup_text2dateG,max_words_in_samples=2)
    annotated_input0=annotated_input
    # - a max_words_in_samples a ténylegesen alkalmazott keresőmintákhoz igazítandó (lookup_text2dateG)

    if outtype=='annotate only': return annotated_input         # debug
    
    foundpatterns=[]

    while True:
        # adja hozzá a vizsgálandó inputhoz a következő [múltjövő] szakaszt
        # words=annotated_input.split()
        # for i in range(len(words)):
        #     if word[i]=='[múltjövő]':
        #         section=words[:i]
        #         section_invalues=invalues[:i]
        #         outvalues=outvalues[:i]
        #         annotated_input=annotated_input[i:]


        result=sub_findpattern(annotated_input,invalues,outvalues,dt0)
        

        if result: 
            annotated_input,invalues,outvalues,foundpattern = result
            foundpatterns.append(foundpattern)



        # Ha nincs további beazonosítás, vagy a teljes szöveg be lett azonosítva, akkor vége
        if result==None or annotated_input=='[dátum]':
            # Megnézendő, hogy volt-e sikeres dátumbeazonosítás (az első lesz a return)
            dátumok=[]
            nValueIndex=-1
            patternwords=annotated_input.split()
            for patternword in patternwords:
                if patternword[0]=='[': nValueIndex+=1
                if patternword=='[dátum]':
                    date1,date2 = outvalues[nValueIndex]
                    if outtype=='first_tuple':
                        return (date1,date2)
                    else:
                        if date2 and date2!=date1: result=date1.strftime('%Y.%m.%d') + '-' + date2.strftime('%Y.%m.%d')
                        else: result=date1.strftime('%Y.%m.%d')
                        if outtype=='first+': result=(result + '\n' +
                            '   input:     ' + annotated_input0 + '\n' +
                            '   output:    ' + annotated_input + '\n' +
                            '   outvalues: ' + str(outvalues) + '\n' +
                            '   invalues:  ' + str(invalues) + '\n' +
                            'foundpatterns:\n   ' + '\n   '.join(foundpatterns)
                            )
                        if outtype in ['first','first+']:
                            return result
                    dátumok.append(result)
            if len(dátumok)>0:
                return ','.join(dátumok)

            # sikertelen  (egyetlen dátum sem volt a szövegben)
            if outtype=='first':  result=''
            elif outtype=='first+':  
                result=('sikertelen\n' +
                        '   input:     ' + annotated_input0 + '\n' +
                        '   output:    ' + annotated_input + '\n' +
                        '   outvalues: ' + str(outvalues) + '\n' +
                        '   invalues:  ' + str(invalues) + '\n' +
                        'foundpatterns:\n   ' + '\n   '.join(foundpatterns)
                        )
            elif outtype=='first_tuple': result=(None,None)
            return result

        # Ha részleges beazonosítás volt, akkor a pásztázási ciklus újrakezdése



# Háttér-metódusok a mintázatok interpretálásához
class Ttext2date:

    def __init__(self):
        self.datemin=datetime(1,1,1)
        self.datemax=datetime(9999,12,31)

    @staticmethod
    def sub_is_sorszam(szám_in):
        return  szám_in and endwith(szám_in,r'\.|dik|elsö|első')    

    @staticmethod
    def sub_húsvétvasárnap(év):   # return datetime vagy None
            honapnap=kodto(év,'2000:04.23//2001:04.15//2002:03.31//2003:04.20//2004:04.11//2005:03.27//2006:04.16//2007:04.08//' +
                    '2008:03.23//2009:04.12//2010:04.04//2011:04.24//2012:04.08//2013:03.31//2014:04.20//2015:04.05//2016:03.27//' +
                    '2017:04.16//2018:04.01//2019:04.21//2020:04.12//2021:04.04//2022:04.17//2023:04.09//2024:03.31//2025:04.20//' +
                    '2026:04.05//2027:03.28//2028:04.16//2029:04.01//2030:04.21//2031:04.13//2032:03.28//2033:04.17//2034:04.09//' +
                    '2035:03.25//2036:04.13//2037:04.05//2038:04.25//2039:04.10//2040:04.01//2041:04.21//2042:04.06//2043:03.29//' +
                    '2044:04.17//2045:04.09//2046:03.25//2047:04.14//2048:04.05//2049:04.18//2050:04.10')
            if honapnap: 
                return fn_parsedate(str(év) + '.' + honapnap,'.')




    @staticmethod
    def sub_wholedate(szám,szám2,szám3):
        try: dtout=datetime(szám,szám2,szám3)
        except: return None
        return (dtout,None)

    @staticmethod
    def sub_monthdate(szám,szám2):
        try: dtout=datetime(szám,szám2,1)
        except: return None
        dtout2=fn_monthlastday(dtout)
        return (dtout,dtout2)

    @staticmethod
    def sub_hónapnév(n,dt0,tense):
        dtout=datetime(dt0.year,n,1)         # aktuális évben
        # Ha van kontextus, akkor eltolásra lehet szükség
        if tense=='future' and n<dt0.month: dtout=fn_dateadd(dtout,1,'year')
        elif tense=='past' and n>dt0.month: dtout=fn_dateadd(dtout,-1,'year')
        dtout2=fn_monthlastday(dtout)
        return (dtout,dtout2)

    @staticmethod
    def sub_év_hónap(év,hónap):
        if év<1 or év>2100: return None
        if hónap<1 or hónap>12: return None
        dtout=datetime(év,hónap,1)
        dtout2=fn_monthlastday(dtout)
        return (dtout,dtout2)
    
    @staticmethod
    def sub_évnapja(év,évnapja):   # return (date1,date2)
        
        # "MMdd"
        if len(évnapja)==4 and évnapja.isdigit():
            try: return ( fn_parsedate(str(év) + évnapja,'c8'), None )
            except: pass 
        # "MMdd:MMdd"
        elif len(évnapja)==9 and évnapja[:4].isdigit() and évnapja[5:].isdigit():
            try: return ( fn_parsedate(str(év) + évnapja[:4],'c8'), fn_parsedate(str(év) + évnapja[5:],'c8') )
            except: pass
        # "húsvét%"
        elif beginwith(évnapja,'húsvét'):
            date1=Ttext2date.sub_húsvétvasárnap(év)
            if date1:
                add=cutleft(évnapja,'húsvét')
                if add=='_': return (fn_dateadd(date1,-2), fn_dateadd(date1,1) )    # péntektől hétfőig
                else:
                    try: nAdd=int(add)
                    except: nAdd=0
                    date1=fn_dateadd(date1,nAdd)
                    return ( date1, None )
                     
        # "pünkösd%"
        elif beginwith(évnapja,'pünkösd'):
            date1=Ttext2date.sub_húsvétvasárnap(év)
            if date1:
                date1 = fn_dateadd(date1,49)        # 7 héttel húsvét után
                add=cutleft(évnapja,'pünkösd')
                if add=='_': return (date1, fn_dateadd(date1,1) )    # vasárnaptól hétfőig
                else:
                    try: nAdd=int(add)
                    except: nAdd=0
                    date1=fn_dateadd(date1,nAdd)
                    return ( date1, None )

        
        return (None,None)



    @staticmethod
    def sub_múltjövő_időtartam(időtartam,múltjövő,dt0):
        # csak a viszonyítási alap tér el a "jövő"-"következő" párban, az algoritmus megegyezik
        dtout=None
        dtout2=None
        
        szám=1
        if múltjövő in ['múlt','előző']: szám=-1
        elif múltjövő=='most': szám=0
        
        if időtartam=='nap':
            dtout=fn_dateadd(dt0,szám)
        elif időtartam=='hét':
            dtMonday=fn_monday(dt0)             # az aktuális hét első napja
            dtout=fn_dateadd(dtMonday,7*szám)   # előző, aktuális, következő
            dtout2=fn_dateadd(dtout,6)          
        elif időtartam=='hónap':
            dtMonthfirst=dt0.replace(day=1)
            dtout=fn_dateadd(dtMonthfirst,szám,'month')
            dtout2=fn_monthlastday(dtout)
        elif időtartam=='negyedév':
            dtFirst=dt0.replace(month=(1 + ((dt0.month-1)//3) * 3))
            dtFirst=dtFirst.replace(day=1)
            dtout=fn_dateadd(dtFirst,3*szám,'month')
            dtout2=fn_monthlastday(fn_dateadd(dtout,2,'month'))
        elif időtartam=='félév':
            dtFirst=dt0.replace(month=(1 + ((dt0.month-1)//6) * 6))
            dtFirst=dtFirst.replace(day=1)
            dtout=fn_dateadd(dtFirst,6*szám,'month')
            dtout2=fn_monthlastday(fn_dateadd(dtout,5,'month'))
        elif időtartam=='év':
            dtFirst=datetime(dt0.year,1,1)
            dtout=fn_dateadd(dtFirst,szám,'year')
            dtout2=datetime(dtout.year,12,31)
        elif időtartam=='évtized':
            dtFirst=datetime((dt0.year//10)*10,1,1)
            dtout=fn_dateadd(dtFirst,szám*10,'year')
            dtout2=datetime(dtout.year+9,12,31)
        elif időtartam=='évszázad':
            dtFirst=datetime((dt0.year//100)*100,1,1)
            dtout=fn_dateadd(dtFirst,szám*100,'year')
            dtout2=datetime(dtout.year+99,12,31)
        elif időtartam=='évezred':
            dtFirst=datetime((dt0.year//1000)*1000,1,1)
            dtout=fn_dateadd(dtFirst,szám*1000,'year')
            dtout2=datetime(dtout.year+999,12,31)
        
        return (dtout,dtout2)

    @staticmethod
    def sub_múltjövő_évszak(múltjövő,évszak,dt0):
        year=dt0.year
        month=dt0.month
        # A tél külön kezelendő, mert átfed az évváltással
        if évszak=='12':
            if múltjövő=='következő':
                if month==12: year+=1       # decemberben már a következő évi tél
            elif múltjövő=='előző':
                if month<3: year-=2         # januárfebruárban még az előző tél
                else: year-=1               # egyébként az év eleji tél
            else:
                if múltjövő =='most': year-=1
                elif múltjövő =='múlt': year-=2
                if month>=7: year+=1 # félévtől már a következő évire utal
        
        else:
            if múltjövő =='múlt': year-=1
            elif múltjövő =='jövő': year+=1
            elif múltjövő =='előző': 
                if month<=int(évszak)+2: year-=1
            elif múltjövő =='következő': 
                if month>=int(évszak): year+=1

        dtout=datetime(year,int(évszak),1)
        dtout2=fn_monthlastday(fn_dateadd(dtout,2,'month'))
        return (dtout,dtout2)

    @staticmethod
    def sub_múltjövő_hónapnév(múltjövő,honap,dt0):
        year=dt0.year
        if múltjövő=='múlt': year=year-1
        elif múltjövő=='előző': 
            if dt0.month<=honap: year-=1
        elif múltjövő=='jövő': year=year+1
        elif múltjövő=='következő': 
            if dt0.month>=honap: year+=1

        dtout=datetime(year,honap,1)
        dtout2=fn_monthlastday(dtout)
        return (dtout,dtout2)

    @staticmethod
    def sub_múltjövő_hónapnév_szám(múltjövő,honap,szám,szám_in,dt0):
        if endwith(szám_in,'dik|elsö'): return None
        if type(honap)==str: honap=int(honap)

        year=dt0.year
        if múltjövő=='múlt': year=year-1
        elif múltjövő=='előző': 
            if dt0.month<honap or (dt0.month==honap and dt0.day<=szám): year-=1
        elif múltjövő=='jövő': year=year+1
        elif múltjövő=='következő': 
            if dt0.month>honap or (dt0.month==honap and dt0.day>=szám): year+=1

        try: dtout=datetime(year,honap,szám)
        except: return None
        return (dtout,None)

    @staticmethod
    def sub_múltjövő_hétnapja(múltjövő,hétnapja,dt0):
        # a "következő", "előző" csak a "következő hét" kontextusban kerül ide, amikor nics érdemi különbség
        #   "jövő" és "következő" között
        dtMonday=fn_monday(dt0)
        if múltjövő in ['múlt','előző']: dtMonday=fn_dateadd(dtMonday,-7) 
        elif múltjövő in ['jövő','következő']: dtMonday=fn_dateadd(dtMonday,7) 

        if hétnapja=='hétvége': 
            dtout=fn_dateadd(dtMonday,5)    # szombat
            dtout2=fn_dateadd(dtout,1)
        elif hétnapja=='hétköznap': 
            dtout=dtMonday
            dtout2=fn_dateadd(dtout,4)
        else: 
            dtout=fn_dateadd(dtMonday,int(hétnapja)-1)
            dtout2=None
        return (dtout,dtout2)

    @staticmethod
    def sub_múltjövő_forduló(forduló,múltjövő,dt0):
        if beginwith(forduló,'század'): years=100
        elif beginwith(forduló,'ezred'): years=1000
       
        dtout=datetime((dt0.year//years) * years,1,1)

        if forduló in ['századvég','ezredvég']: dtout=fn_dateadd(dtout,-1)
            
        if múltjövő!='most':
            if múltjövő in ['múlt','előző']: dtout=fn_dateadd(dtout,-years,'year')
            elif múltjövő in ['jövő','következő']: dtout=fn_dateadd(dtout,years,'year')

        return (dtout,None)

    @staticmethod
    def sub_sorszám_hétnapja(dt1,dt2,sorszám,hétnapja):
        # adott időszakon belüli [sorszám] hétnapja ("hétvége" és "hétköznap" is)
        dtout=None
        dtout2=None
        if dt1!=None and dt2!=None and dt2>dt1:       # időszak szerepel a dátumban
            # "[sorszám] hétköznap"
            if hétnapja=='hétköznap':
                if sorszám=='utolsó':
                    if dt2.weekday()<5: dtout=dt2
                    else: dtout=fn_dateadd(dt2,-1,'workday')
                elif sorszám=='utolsóelőtti':
                    if dt2.weekday()<5: dtout=fn_dateadd(dt2,-1,'workday')
                    else: dtout=fn_dateadd(dt2,-2,'workday')
                else:
                    if sorszám==None:   # sorszám nélküli változat (pl. "március második hetében hétköznap")
                        # az időszakba eső első hétköznapi naptól az adott hét pénteki napjáig
                        if dt1.weekday()<5: dtout=dt1
                        else: 
                            dtout=fn_dateadd(dt1,1,'workday')
                            if dtout>dt2: return (None,None)
                        dtout2=fn_dateadd(dt1,4-dt1.weekday())   # legközelebbi péntek (megegyezhet a dt1-gyel)
                        return (dtout,dtout2)
                    else:
                        if dt1.weekday()<5: sorszám-=1
                        dtout=fn_dateadd(dt1,sorszám,'workday')
                dtout2=dtout
            else:
                if sorszám==None: sorszám=1
                length=1
                if hétnapja=='hétvége':
                    length=2
                    hétnapja='6'
                # Az első megfelelő nap az időszakban
                dtFirst = fn_dateadd(dt1, (7 + int(hétnapja) - (dt1.weekday()+1)) % 7)
                if sorszám=='utolsó': sorszám=fn_daydiff(dt2,dtFirst)//7 + 1
                elif sorszám=='utolsóelőtti': sorszám=fn_daydiff(dt2,dtFirst)//7

                dtout = fn_dateadd(dtFirst,(sorszám-1)*7)
                dtout2=fn_dateadd(dtout,length-1)

                if dtout!=None:
                    if dtout>dt2: dtout=None     # a kezdődátum nem lehet későbbi az időszaknál
                    else: 
                        if dtout<dt1: dtout=dt1
                        if dtout2>dt2: dtout2=dt2
                        if dtout2<dtout: dtout=None
        return (dtout,dtout2)

    @staticmethod
    def sub_utánielőtti_időszak(dátum,utánielőtti,szám,szám_in,időtartam):
        # utánielőtti:  "utáni" "előtti", "után", "előtt", "tól", "ig"
        # szám:  "utolsó", "utolsóelőtti" is lehet
        
        dtout=None
        dtout2=None

        dt1,dt2 = dátum
        if dt2==None: dt2=dt1

        if utánielőtti in ['utáni','után']:
            előjel=1
            dt0=dt2   # időszak esetén a zárónap után
        elif utánielőtti=='tól':
            előjel=1
            dt0=dt1   # időszak esetén a kezdőnaptól
        elif utánielőtti in ['előtti','előtt']:
            előjel=-1
            dt0=dt1   # időszak esetén a kezdőnap előtt
        elif utánielőtti=='ig':
            előjel=-1
            dt0=dt2   # időszak esetén a zárónapig

        bTólig=utánielőtti in ['tól','ig']

        if type(szám)==str:          # "utolsó"  "utolsóelőtti"   (csak "ig", "előtt", "előtti" esetén)
            if utánielőtti in ['utáni','után','tól']: return (None,None)
            if szám=='utolsó': szám=1
            elif szám=='utolsóelőtti': szám=2
            else: return (None,None)

        szám=int(szám)
        # sorszám vagy normál szám?
        if Ttext2date.sub_is_sorszam(szám_in):   # szombat utáni első nap,   tavasz előtti utolsó hét  (naptári hét, naptári hónap, ...)
            # sorszámozott (naptári) hét, hónap, év, ...
            if időtartam=='nap': dtout=fn_dateadd(dt0,szám*előjel)
            elif időtartam=='hét':
                dtMonday=fn_monday(dt0)             # az aktuális hét első napja
                dtout=fn_dateadd(dtMonday,7*szám*előjel)   # előző, aktuális, következő
                dtout2=fn_dateadd(dtout,6)          
            elif időtartam=='hónap':
                dtMonthfirst=dt0.replace(day=1)
                dtout=fn_dateadd(dtMonthfirst,szám*előjel,'month')
                dtout2=fn_monthlastday(dtout)
            elif időtartam=='negyedév':
                dtFirst=dt0.replace(month=(1 + ((dt0.month-1)//3) * 3))
                dtFirst=dt0.replace(day=1)
                dtout=fn_dateadd(dtFirst,3*szám*előjel,'month')
                dtout2=fn_monthlastday(fn_dateadd(dtout,2,'month'))
            elif időtartam=='félév':
                dtFirst=dt0.replace(month=(1 + ((dt0.month-1)//6) * 6))
                dtFirst=dt0.replace(day=1)
                dtout=fn_dateadd(dtFirst,6*szám*előjel,'month')
                dtout2=fn_monthlastday(fn_dateadd(dtout,5,'month'))
            elif időtartam=='év':
                dtFirst=datetime(dt0.year,1,1)
                dtout=fn_dateadd(dtFirst,szám*előjel,'year')
                dtout2=datetime(dtout.year,12,31)
            elif időtartam=='évtized':
                dtFirst=datetime((dt0.year//10)*10,1,1)
                dtout=fn_dateadd(dtFirst,szám*10*előjel,'year')
                dtout2=datetime(dtout.year+9,12,31)
            elif időtartam=='évszázad':
                dtFirst=datetime((dt0.year//100)*100,1,1)
                dtout=fn_dateadd(dtFirst,szám*100*előjel,'year')
                dtout2=datetime(dtout.year+99,12,31)
            elif időtartam=='évezred':
                dtFirst=datetime((dt0.year//1000)*1000,1,1)
                dtout=fn_dateadd(dtFirst,szám*1000*előjel,'year')
                dtout2=datetime(dtout.year+999,12,31)
            
            # if utánielőtti=='tól':          # dátumtól a második hétig   (naptári hét)
            #     dtout=dt1       # kiinduló időszak kezdődátuma (inkluzív)
               

          
        else:   # szombat utáni 2 nap      január 3 előtti 3 hét
            if időtartam=='nap': dt1=fn_dateadd(dt0,szám*előjel)
            elif időtartam=='hét': dt1=fn_dateadd(dt0,7*szám*előjel)   
            elif időtartam=='hónap': dt1=fn_dateadd(dt0,szám*előjel,'month')
            elif időtartam=='negyedév':  dt1=fn_dateadd(dt0,3*szám*előjel,'month')
            elif időtartam=='félév': dt1=fn_dateadd(dt0,6*szám*előjel,'month')
            elif időtartam=='év': dt1=fn_dateadd(dt0,szám*előjel,'year')
            elif időtartam=='évtized':  dt1=fn_dateadd(dt0,szám*10*előjel,'year')
            elif időtartam=='évszázad':  dt1=fn_dateadd(dt0,szám*100*előjel,'year')
            elif időtartam=='évezred':  dt1=fn_dateadd(dt0,szám*1000*előjel,'year')

            if utánielőtti in ['után','előtt']:     # péntek után két nappal  (egyetlen nap)
                dtout=dt1
                dtout2=None
            else:
                # A kiinduló dátum előtt
                if dt1<dt0:
                    if bTólig:    # ig
                        dtout=fn_dateadd(dt1,1)
                        dtout2=dt0
                    else:     # előtt
                        dtout=dt1
                        dtout2=fn_dateadd(dt0,-1)
                # A kiinduló dátum után
                else:
                    if bTólig:   # tól
                        dtout=dt0
                        dtout2=fn_dateadd(dt1,-1)
                    else:
                        dtout=fn_dateadd(dt0,1)
                        dtout2=dt1

        return (dtout,dtout2)

    @staticmethod
    def sub_szám_időtartam_múlvaezelőtt(szám,időtartam,múlvaezelőtt,dt0):
        dtout=None
        if múlvaezelőtt=='ezelőtt': szám=-szám
            
        if időtartam=='nap':
            dtout=fn_dateadd(dt0,szám)
        elif időtartam=='hét':
            dtout=fn_dateadd(dt0,7*szám)
        elif időtartam=='hónap':
            dtout=fn_dateadd(dt0,szám,'month')
        elif időtartam=='év':
            dtout=fn_dateadd(dt0,szám,'year')
        else: return None
        return (dtout,None)
    
    @staticmethod
    def sub_hónapszám_múlvaezelőtt_napon(szám,nap,dt0):
        dt=fn_dateadd(dt0,szám,'month')
        if nap<=1 or nap>31: return None       # and (endwith(szám_in,'\.') or vanbenne(szám_in,'dika|dike|diká|diké|elsej')):
        try: dtout=datetime(dt.year,dt.month,nap)
        except: return None
        return (dtout,None)        

    @staticmethod
    def sub_hétszám_múlvaezelőtt_hétnapján(szám,hétnapja,dt0):
        dtout=None
        dtout2=None
        dt=fn_dateadd(dt0,7*szám)
        dtMonday=fn_monday(dt)
        if hétnapja=='hétvége': 
            dtout=fn_dateadd(dtMonday,5)    # szombat
            dtout2=fn_dateadd(dtout,1)
        elif hétnapja=='hétköznap': 
            dtout=dtMonday
            dtout2=fn_dateadd(dtout,4)
        else:
            dtout=fn_dateadd(dtMonday,int(hétnapja)-1)
        if dtout==None: return None
        return (dtout,dtout2)



    @staticmethod
    def sub_dátum_utánelőtti_sorszám_hétnapja(dátum,utánielőtti,szám,hétnapja):
        dt1,dt2 = dátum
        if dt2==None: dt2=dt1

        if type(szám)==str:
            if utánielőtti in ['utáni']: return None
            if szám=='utolsó': szám=1
            elif szám=='utolsóelőtti': szám=2
            else: return None
        else:
            szám=int(szám)

        dtout=None
        dtout2=None
        if hétnapja=='hétköznap':
            if utánielőtti=='utáni': dtout=fn_dateadd(dt2,szám,'workday')
            elif utánielőtti=='előtti': dtout=fn_dateadd(dt1,-szám,'workday')
            dtout2=dtout
        else:                
            length=1
            if hétnapja=='hétvége':
                length=2
                hétnapja='6'
            if utánielőtti=='utáni':
                dt0=fn_dateadd(dt2,1)
                # Az első megfelelő nap az időszakban
                dtMonday=fn_monday(dt0)
                dtFirst=fn_dateadd(dtMonday,int(hétnapja)-1)
                if dtFirst<dt0: dtFirst=fn_dateadd(dtFirst,7)
                dtout = fn_dateadd(dtFirst,(szám-1)*7)
                if length==2: dtout2=fn_dateadd(dtout,1)
            elif utánielőtti=='előtti':
                dt0=fn_dateadd(dt1,-1)
                # Az első megfelelő nap az időszakban
                dtMonday=fn_monday(dt0)
                dtFirst=fn_dateadd(dtMonday,int(hétnapja)-1)
                if dtFirst>dt0: dtFirst=fn_dateadd(dtFirst,-7)
                dtout=fn_dateadd(dtFirst,-(szám-1)*7)
                if length==2: dtout2=fn_dateadd(dtout,1)
        return (dtout,dtout2)

    @staticmethod
    def sub_dátum_sorszám_időtartam(dátum,szám,időtartam):
        dtout=None
        dtout2=None
        dt1,dt2=dátum
        if időtartam=='évtized' and (dt1.year % 10)==0 and dt1.month==1 and dt1.day==1:            
            if szám=='utolsó': szám=(dt2.year-dt1.year)//10 + 1
            elif szám=='utolsóelőtti': szám=(dt2.year-dt1.year)//10
            dtout=datetime(dt1.year + 10*(szám-1),1,1)
            dtout2=datetime(dt1.year + 10*(szám-1) + 9,12,31)
        elif időtartam=='év' and dt1.month==1 and dt1.day==1:            
            if szám=='utolsó': szám=(dt2.year-dt1.year)+1
            elif szám=='utolsóelőtti': szám=(dt2.year-dt1.year)
            dtout=datetime(dt1.year + (szám-1),1,1)
            dtout2=datetime(dt1.year + (szám-1),12,31)
        elif időtartam=='félév' and dt1.month==1 and dt1.day==1:            
            if szám=='utolsó': dtout=datetime(dt2.year,((dt2.month-1)//2)*2 + 1,1)
            elif szám=='utolsóelőtti': dtout=fn_dateadd(datetime(dt2.year,((dt2.month-1)//2)*2 + 1,1),-6,'month')
            else: dtout=datetime(dt1.year,1+(szám-1)*6,1)
            dtout2=fn_monthlastday(fn_dateadd(dtout,5,'month'))
        elif időtartam=='negyedév' and dt1.month==1 and dt1.day==1:         
            if szám=='utolsó': dtout=datetime(dt2.year,((dt2.month-1)//3)*3 + 1,1)
            elif szám=='utolsóelőtti': dtout=fn_dateadd(datetime(dt2.year,((dt2.month-1)//3)*3 + 1,1),-3,'month')
            else: dtout=datetime(dt1.year,1+(szám-1)*3,1)
            dtout2=fn_monthlastday(fn_dateadd(dtout,2,'month'))
        elif időtartam=='hónap' and dt1.day==1:            
            if szám=='utolsó': dtout=datetime(dt2.year,dt2.month,1)
            elif szám=='utolsóelőtti': dtout=fn_dateadd(datetime(dt2.year,dt2.month,1),-1,'month')
            else: dtout=datetime(dt1.year,dt1.month + (szám-1),1)
            dtout2=fn_monthlastday(dtout)
        elif időtartam=='hét':              
            dtMonday=fn_monday(dt1)   # az időszak első hetének hétfői napja (általában korábra esik az időszak első napjánál)
            if szám=='utolsó': szám=fn_daydiff(dt2,dtMonday)//7 + 1
            elif szám=='utolsóelőtti': szám=fn_daydiff(dt2,dtMonday)//7
            dtout=fn_dateadd(dtMonday,(szám-1)*7,'day')
            dtout2=fn_dateadd(dtout,6,'day')
        elif időtartam=='nap':              
            if szám=='utolsó': szám=fn_daydiff(dt2,dt1) + 1
            elif szám=='utolsóelőtti': szám=fn_daydiff(dt2,dt1)
            dtout=fn_dateadd(dt1,szám-1,'day')
            dtout2=dtout

        if dtout==None or dtout>dt2: return None     # a kezdődátum nem lehet későbbi az időszaknál

        if dtout<dt1: dtout=dt1
        if dtout2>dt2: dtout2=dt2
        if dtout2<dtout: return None
        return (dtout,dtout2)

    @staticmethod
    def sub_dátum_sorszám_törtrész(dátum,szám,törtrész):
        dt1,dt2 = dátum
        if dt2==None or dt2<=dt1: return None         # időszak szerepel a dátumban
        oszto=int(törtrész)
        if szám=='utolsó': szám=oszto
        elif szám=='utolsóelőtti': szám=oszto-1
        if szám<1 or szám>oszto: return None
        unit=fn_daydiff(dt2,dt1)/oszto
        if szám==oszto:
            dtout=fn_dateadd(dt2,-fn_round(unit),'day')
            dtout2=dt2
        else:
            dtout=fn_dateadd(dt1,fn_round(unit*(szám-1)),'day')
            dtout2=fn_dateadd(dtout,fn_round(unit),'day')
        return (dtout,dtout2)

    @staticmethod
    def sub_dátum_elejevége_elejevége(dátum,elejevége,elejevége2):
        szám1=int(elejevége)
        szám2=int(elejevége2)
        if szám2<=szám1: return None
        dt1,dt2 = dátum
        if dt2==None or dt2<=dt1: return None       # időszak szerepel a dátumban

        dtout=None
        dtout2=None
        # A "közepe" itt nem a középső harmadra, hanem a középső napra utal
        dtkozep=fn_dateadd(dt1,fn_daydiff(dt2,dt1)//2)
        if szám1==1: dtout=dt1
        elif szám1==2: dtout=dtkozep
        if szám2==2: dtout2=dtkozep
        elif szám2==3: dtout2=dt2
        return (dtout,dtout2)

    @staticmethod
    def sub_dátumtól_sorszám_időtartam_végéig(dátum,tólig,szám,szám_in,időtartam,elejevége):
        dtout,dt_=dátum

        dt1,dt2 = Ttext2date.sub_utánielőtti_időszak(dátum,tólig,szám,szám_in,időtartam)

        if elejevége=='1': dtout2=fn_dateadd(dt1,-1)     # a kezdőnap előtti nap
        elif elejevége=='2': dtout2=fn_dateadd(dt1,fn_daydiff(dt2,dt1)//2)    # a középső nap
        elif elejevége=='3': dtout2=dt2
        else: return None

        if dtout2<dtout: return None
        return (dtout,dtout2)


    @staticmethod
    def sub_dátum_dátum(dátumA,mintaA,dátumB,mintaB):
        dtAStart,dtAEnd = dátumA
        if dtAEnd==None: dtAEnd=dtAStart

        dtBStart,dtBEnd = dátumB
        if dtBEnd==None: dtBEnd=dtBStart

        # Speciális esetek
        # "2020 februártól augusztusig",  "2020 február-augusztus"
        if beginwith(mintaB,'\[hónapnév\]|\[múltjövő\] \[hónapnév\]'):
            dtBStart=dtBStart.replace(year=dtAStart.year)
            dtBEnd=dtBEnd.replace(year=dtAStart.year)
        # "2020 tavasztól őszig"
        elif beginwith(mintaB,'\[évszak\]'):
            dtBStart=dtBStart.replace(year=dtAStart.year)
            dtBEnd=dtBEnd.replace(year=dtAStart.year)
            if dtBEnd<dtAStart: fn_dateadd(dtBEnd,1,'year')
        # "2020 második negyedévtől a harmadik negyedévig" (elavult, külön mintázata van)
        # if beginwith(mintaB,'\[szám\] \[időtartam\]'):
        #     dtBStart=dtBStart.replace(year=dtAStart.year)
        #     dtBEnd=dtBEnd.replace(year=dtAStart.year)

        dtout=None
        dtout2=None
        # Befoglalás esetén a befoglalt időszak  (pl. "jövő évben decemberben")
        if dtBStart>=dtAStart and dtBEnd<=dtAEnd and dtAEnd.year<9999 and dtAStart.year>1: 
            dtout=dtBStart
            dtout2=dtBEnd
        # egyébként tól-ig értelmezés    (ha vessző van közöttük, akkor ez problémás lehet)
        elif dtAEnd<dtBStart or dtAEnd.year==9999 or dtBStart==1:
            dtout=dtAStart
            dtout2=dtBEnd
        if dtout==None or dtout>dtout2: return None
        return (dtout,dtout2)

    @staticmethod
    def sub_dátum_sorszám_időtartamtól_sorszám_időtartamig(dátum,szám,időtartam,szám2,időtartam2):
        dátum1 = Ttext2date.sub_dátum_sorszám_időtartam(dátum,szám,időtartam)
        if not dátum1: return None
        dátum2 = Ttext2date.sub_dátum_sorszám_időtartam(dátum,szám2,időtartam2)
        if not dátum2: return None
        dtout=dátum1[0]
        dtout2=dátum2[1]
        if dtout2<dtout: return None
        return (dtout,dtout2)

    @staticmethod
    def sub_múltjövő_dt0(self,múltjövő):
        # "-től a következő" ne legyen feldolgozva
        if múltjövő=='következő' and self.patternword_előtte in ['[tólig]','[utánelőtt]','[utánielőtti]']: return None
        dt0=self.today
        if múltjövő in ['következő','előző']: dt0=self.dt0
        return dt0
       







    def szám_szám_szám(self):
        n1,n2,n3=self.outvalues
        if (n1<1000 or n1>2100): return None 
        return self.sub_wholedate(n1,n2,n3)

    def szám_szám_időtartam_szám(self):
        n1,n2,időtartam,n3=self.outvalues
        if időtartam!='hónap': return None
        if (n1<1000 or n2>2100): return None
        return self.sub_wholedate(n1,n2,n3)

    def szám_hónapnév_szám(self):
        n1,honap,n2=self.outvalues
        # "első", "második", ... nem megengedett  (pl. "2022 március első péntek")
        szám_in=self.invalues[2]
        if endwith(szám_in,'dik|elsö'): return None
        return self.sub_wholedate(n1,int(honap),n2)

    def szám_hónapnév(self):
        n1,honap=self.outvalues
        n2=int(honap)
        if not ((n1>=1000 and n1<=2100) and (n2>=1 and n2<=12)): return None 
        return self.sub_monthdate(n1,n2)

    def hónapnév_szám(self):
        honap,n2=self.outvalues
        szám_in = self.invalues[1]
        # nem itt kell kezelni, ha a [sorszám] [időtartam] mintázat is jó lehet  (pl. "november 2. fele", "november 2. hétfője")
        if Ttext2date.sub_is_sorszam(szám_in) and self.patternword_utána in ['[időtartam]','[hétnapja]','[törtrész]']: return None
        #if not (endwith(szám_in,'dik') or szám_in=='elsö'):     # "január első fele" ne "január 1." legyen
        return self.sub_wholedate(self.dt0.year,int(honap),n2)

    def szám_szám(self):
        dtout=None
        dtout2=None
        n1,n2=self.outvalues
        # "2022 01"   
        if (n1>=1000 and n1<=2100) and (n2>=1 and n2<=12): 
            szám_in = self.invalues[1]
            if len(szám_in)==2 and szám_in.isdigit():    # fontos, hogy a "2021 2. ne kerüljön ide (pl. nem működne a "2021. második fele" beazonosítása)
                dtout=datetime(n1,n2,1)
                dtout2=fn_monthlastday(dtout)
        # "01 12"    hónap nap
        elif (n1>=1 and n1<=12) and (n2>=1 and n2<=31) and self.patternword_előtte not in ['[időtartam]','[hónapnév]']:
            try: dtout=datetime(self.dt0.year,n1,n2)
            except: dtout=None
        # "2012-2014"
        elif (n1>=1000 and n1<=2100) and (n2>=1000 and n2<=2100) and (n2>n1):
            dtout=datetime(n1,1,1)
            dtout2=datetime(n2,12,31)
        return (dtout,dtout2)


    def szám_évszak(self):  # "2015 tavasz"   
        dtout=None
        dtout2=None
        n,évszak=self.outvalues         # évszak: 3,6,9,12
        if n>=1 and n<=2100:
            if évszak=='12': n-=1    # a tél átnyúlik az évhatáron, a kezdődátuma előző évi
            dtout=datetime(n,int(évszak),1)    
            dtout2=fn_monthlastday(fn_dateadd(dtout,2,'month'))
        return (dtout,dtout2)

    def szám(self):
        dtout=None
        dtout2=None
        n,=self.outvalues
        szám_in,=self.invalues
        # évszám
        if n>=1000 and n<=2100:
            dtout=datetime(n,1,1)
            dtout2=datetime(n,12,31)
        # másodikán, másodikától, ...  (de "első" "második" ne kerüljön ide)
        #  todo: 2-án, 2-ától, ... is kellene
        elif n>=1 and n<=31 and vanbenne(szám_in,'dika|dike|diká|diké|elsej'):
            try: dtout=datetime(self.dt0.year,self.dt0.month,n)
            except: dtout=None
        # '20220102'  '19551211'
        elif len(szám_in)==8:
            if beginwith(szám_in,'19|20'): 
                try: dtout=datetime(int(szám_in[:4]),int(szám_in[4:6]),int(szám_in[6:]))
                except: dtout=None
        # '0203'  '1201'
        elif len(szám_in)==4:
            if beginwith(szám_in,'0|1'): 
                try: dtout=datetime(self.dt0.year,int(szám_in[:2]),int(szám_in[2:]))
                except: dtout=None
        return (dtout,dtout2)



    def maholnap(self):
        n,=self.outvalues
        return (fn_dateadd(self.dt0,int(n)),None)       



    def maholnap_időtartam(self):
        maholnap,időtartam=self.outvalues
        n=int(maholnap)
        if időtartam!='nap': return None
        return (fn_dateadd(self.dt0,n),None)      


    def maholnap_utánelőtt(self):
        dtout=None
        maholnap,utánelőtt=self.outvalues
        n=int(maholnap)
        if n==1 and utánelőtt=='után': dtout=fn_dateadd(self.dt0,2)       
        elif n==-1 and utánelőtt=='előtt': dtout=fn_dateadd(self.dt0,-2)       
        return (dtout,None)

    def hónapnév(self):
        hónapnév,=self.outvalues
        return Ttext2date.sub_hónapnév(int(hónapnév),self.dt0,self.tense)

    def hónapnév_időtartam(self):           # február hónap
        hónapnév,időtartam = self.outvalues
        if időtartam!='hónap': return None
        return Ttext2date.sub_hónapnév(int(hónapnév),self.dt0,self.tense)

    def hétnapja(self):
        hétnapja,=self.outvalues        # '1', ..., '7', 'hétvége'
        
        dtout=None
        dtout2=None
        dtMonday=fn_monday(self.dt0)
        # Az aktuális héten
        if hétnapja=='hétvége': 
            dtout=fn_dateadd(dtMonday,5)    # szombat
            if self.tense=='past' and dtout>self.dt0: dtout=fn_dateadd(dtout,-7)
            dtout2=fn_dateadd(dtout,1)
        elif hétnapja=='hétköznap': 
            dtout=dtMonday
            if self.tense=='past' and dtout>self.dt0: dtout=fn_dateadd(dtout,-7)
            dtout2=fn_dateadd(dtout,4)
        else:
            dtout=fn_dateadd(dtMonday,int(hétnapja)-1)
            # Ha van kontextus, akkor eltolásra lehet szükség
            if self.tense=='future' and dtout<self.dt0: dtout=fn_dateadd(dtout,7)
            elif self.tense=='past' and dtout>self.dt0: dtout=fn_dateadd(dtout,-7)
        return (dtout,dtout2)



    def szám_hétnapja(self):           # "második hétfő" (idén)  "120. munkanap" (idén) 
        szám,hétnapja=self.outvalues       
        # sorszám
        if not Ttext2date.sub_is_sorszam(self.invalues[0]): return None
        # ne legyen előtte dátumként vagy relációként értelmezhető egyszavas kifejezés  (pl. "2020 második hétfő") 
        if self.patternword_előtte in ['[szám]','[hónapnév]','[időtartam]','[utánielőtti]','[tólig]']: return None

        return Ttext2date.sub_sorszám_hétnapja(datetime(self.dt0.year,1,1),datetime(self.dt0.year,12,31),szám,hétnapja)


    def utolsó_hétnapja(self):          # "utolsó hétfő" (aktuális nap előtti utolsó)
        szám,hétnapja=self.outvalues       
        # ne legyen előtte dátumként vagy relációként értelmezhető egyszavas kifejezés  (pl. "2020 második hétfő") 
        if self.patternword_előtte in ['[szám]','[hónapnév]','[időtartam]','[utánielőtti]','[tólig]']: return None
        return Ttext2date.sub_sorszám_hétnapja(self.datemin,fn_dateadd(self.dt0,-1),szám,hétnapja)
        return Ttext2date.sub_sorszám_hétnapja(datetime(self.dt0.year,1,1),datetime(self.dt0.year,12,31),szám,hétnapja)


    def évszak(self):
        value,=self.outvalues
        
        year=self.dt0.year
        if value=='12' and self.dt0.month<6: year-=1    # a tél átnyúlik az évhatáron, ezért nem teljesen egyértelmű az "ezen a télen" ... jelentése

        dtout=datetime(year,int(value),1)    # kezdődátum
        dtout2=fn_monthlastday(fn_dateadd(dtout,2,'month'))

        # Ha van kontextus, akkor eltolásra lehet szükség
        if self.tense=='future' and self.dt0>dtout2:   # "télen hideg lesz",  az aktuális tél után vagyunk
            dtout=fn_dateadd(dtout,1,'year')
            dtout2=fn_monthlastday(fn_dateadd(dtout,2,'month'))
        elif self.tense=='past' and self.dt0<dtout:   # "télen hideg volt",  az aktuális tél előtt vagyunk
            dtout=fn_dateadd(dtout,-1,'year')
            dtout2=fn_monthlastday(fn_dateadd(dtout,2,'month'))
        
        return (dtout,dtout2)


    def évnapja(self):              # karácsony, újév
        évnapja, = self.outvalues
        year=self.dt0.year
        return Ttext2date.sub_évnapja(year,évnapja)


    def szám_évnapja(self):         # 2020 karácsony
        szám,évnapja = self.outvalues
        year=szám
        return Ttext2date.sub_évnapja(year,évnapja)


    def dátum_évnapja(self):        # tavaly karácsony
        dátum,évnapja = self.outvalues
        dt1,dt2 = dátum
        if dt1.month!=1 or dt1.day!=1: return None    # csak teljes év jó
        year=dt1.year
        return Ttext2date.sub_évnapja(year,évnapja)


    def múltjövő_évnapja(self):     # következő karácsony
        múltjövő,évnapja = self.outvalues
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None

        dtout,dtout2=Ttext2date.sub_évnapja(dt0.year,évnapja)


        yeardiff=0
        if múltjövő=='múlt': yeardiff=-1
        elif múltjövő=='előző': 
            if dt0<=dtout2: yeardiff=-1
        elif múltjövő=='jövő': yeardiff=1
        elif múltjövő=='következő': 
            if dt0>=dtout: yeardiff=1
        
        if yeardiff!=0:
            dtout=fn_dateadd(dtout,yeardiff,'year')
            dtout2=fn_dateadd(dtout2,yeardiff,'year')

        return (dtout,dtout2)

    def múltjövő(self):                 # 'most'
        múltjövő, = self.outvalues
        if múltjövő=='most' and beginwith(self.invalues[0],'most'): return (self.today,None)
        else: return None


    def forduló(self):                  # "az ezredfordulón"   "az előző századvégen"
        forduló, = self.outvalues
        múltjövő = 'most'
        return Ttext2date.sub_múltjövő_forduló(forduló,múltjövő,self.today)


    def múltjövő_forduló(self):
        múltjövő,forduló = self.outvalues
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None
        return Ttext2date.sub_múltjövő_forduló(forduló,múltjövő,dt0)

    def egyedi(self):   # "rendszerváltás"    év,nap,időszak is lehet (korlátozottan használható mert a mintában pl nem lehet szám szó) 
        egyedi,=self.outvalues
        return text2date(egyedi,self.dt0,outtype='first_tuple')


    def szám_időtartam_múlvaezelőtt(self):      # 2 nap múlva, 3 év múlva,  négy hét múlva,  egy évvel ezelőtt
        szám,időtartam,múlvaezelőtt=self.outvalues
        return Ttext2date.sub_szám_időtartam_múlvaezelőtt(szám,időtartam,múlvaezelőtt,self.dt0)        

    def szám_időtartam(self):                   # "2022 év", "90-es években", "két hete", "12 éve", "20 napja"
        szám,időtartam = self.outvalues
        
        dtout=None
        dtout2=None
        szám_in = self.invalues[0]
        időtartam_in=self.invalues[1]
        #  "két hete",  "három hónapja",  "12 éve"   "20 napja"  (kétértelmű, de időpontot is jelenthet, "... ezelőtt" jelentéssel) 
        if időtartam_in in ['éve','honapja','hete','napja']: 
            # ha szám sorszám, és előtte valamilyen időtartam-szó áll, akkor nem itt kell értelmezni (pl. "2020 3. hete")
            if Ttext2date.sub_is_sorszam(szám_in) and self.patternword_előtte in ['[időtartam]','[szám]','[évszak]','[hónapnév]','[évnapja]','[hétnapja]']: return None
            
            szám=-szám
            if időtartam=='nap':
                dtout=fn_dateadd(self.dt0,szám)
            elif időtartam=='hét':
                dtout=fn_dateadd(self.dt0,7*szám)
            elif időtartam=='hónap':
                dtout=fn_dateadd(self.dt0,szám,'month')
            elif időtartam=='év':
                dtout=fn_dateadd(self.dt0,szám,'year')

        # "'90-es évek", "1870-es évek", "1200-as évek",
        elif beginwith(időtartam_in,'évek|évei') and (szám % 10)==0:
            if (szám % 100) ==0:
                dtout=datetime(szám,1,1)
                dtout2=datetime(szám+99,12,31)
            elif szám<100:      # jelen vagy múltbelinek tekintem ('30-as évek: 1930-as évek)
                évszázad0 = self.dt0.year//100
                évtized0 = (self.dt0.year - évszázad0*100)//10
                évtized = szám//10
                if évtized>évtized0: évszázad0-=1
                dtout=datetime(évszázad0*100 + szám,1,1)
                dtout2=datetime(évszázad0*100 + szám + 9,12,31)
            else:
                dtout=datetime(szám,1,1)
                dtout2=datetime(szám + 9,12,31)
            
        elif időtartam=='év' and szám>1900 and szám<=2100:      # ha nincs utána pont, akkor is tekintse konkrét évszámnak
            dtout=datetime(szám,1,1)
            dtout2=datetime(szám,12,31)

        elif időtartam=='évszázad':          # időszámítás kezdete óta
            if szám>=1 or szám<=30:
                dtout=datetime((szám-1)*100,1,1)
                dtout2=datetime((szám-1)*100 + 99,12,31)

        # [sorszám] [időtartam]
        #   Csak akkor jöjjön ide, ha előtte nem egyszavas dátumkifejezés áll
        #     (ebben az esetben először az egyszavas dátum lefordítása kell, majd utána a "[dátum] [szám] [időtartam]" mintázat
        elif Ttext2date.sub_is_sorszam(szám_in) and not self.patternword_előtte in ['[szám]','[évszak]','[időtartam]',
                                                '[évnapja]','[hónapnév]','[utánelőtt]','[utánielőtti]','[tólig]']:
            if időtartam=='évtized':       # aktuális évszázadban
                if szám>=1 or szám<=10:
                    year=(self.dt0.year//100) * 100
                    dtout=datetime(year + (szám-1)*10,1,1)
                    dtout2=datetime(year + (szám-1)*10 + 9,12,31)
            elif időtartam=='év':            # időszámítás kezdete óta
                if szám>=1 or szám<=2100:
                    dtout=datetime(szám,1,1)
                    dtout2=datetime(szám,12,31)
            elif időtartam=='félév':            # aktuális évben
                if szám==1 or szám==2:
                    dtout=datetime(self.dt0.year,1+(szám-1)*6,1)
                    dtout2=fn_monthlastday(fn_dateadd(dtout,5,'month'))
            elif időtartam=='negyedév':         # aktuális évben
                if szám>=1 and szám<=4:
                    dtout=datetime(self.dt0.year,1+(szám-1)*3,1)
                    dtout2=fn_monthlastday(fn_dateadd(dtout,2,'month'))
            elif időtartam=='hónap':            # aktuális évben
                if szám>=1 and szám<=12:
                    dtout=datetime(self.dt0.year,szám,1)
                    dtout2=fn_monthlastday(dtout)
            elif időtartam=='hét':              # aktuális évben
                if szám>=1 and szám<=53:
                    dtMonday=fn_monday(datetime(self.dt0.year,1,1))   # az év első hetének hétfői napja (általában az előző év végére esik)
                    dtout=fn_dateadd(dtMonday,(szám-1)*7,'day')
                    dtout2=fn_dateadd(dtout,6,'day')
                    if dtout.year<self.dt0.year: dtout=datetime(self.dt0.year,1,1)
                    if dtout2.year>self.dt0.year: dtout2=datetime(self.dt0.year,12,31)
                    if dtout>dtout2: dtout=None         # szám=53 esetén fordulhat elő
            elif időtartam=='nap':              # aktuális évben
                if szám>=1 and szám<=366:
                    dtout=fn_dateadd(datetime(self.dt0.year,1,1),szám-1,'day')
                    if dtout.year>self.dt0.year: dtout=None
        if dtout==None: return None
        return (dtout,dtout2)

    def szám_időtartam_múlvaezelőtt_hónapnév(self):     # 3 évvel ezelőtt decemberben, két év múlva októberben
        szám,időtartam,múlvaezelőtt,hónap=self.outvalues
        if időtartam!='év': return None
        if múlvaezelőtt=='ezelőtt': szám=-szám
        return Ttext2date.sub_év_hónap(self.dt0.year+szám,int(hónap))

    def szám_időtartam_hónapnév(self):              # 3 éve decemberben, két éve októberben
        szám,időtartam,hónap=self.outvalues
        időtartam_in=self.invalues[1]
        if időtartam_in!='éve': return None
        szám=-szám
        return Ttext2date.sub_év_hónap(self.dt0.year+szám,int(hónap))


    def szám_időtartam_múlvaezelőtt_szám(self):     # 2 hónappal ezelőtt 5-én, három hónap múlva hatodikán
        szám,időtartam,múlvaezelőtt,napon=self.outvalues
        if időtartam!='hónap': return None
        if múlvaezelőtt=='ezelőtt': szám=-szám
        return Ttext2date.sub_hónapszám_múlvaezelőtt_napon(szám,napon,self.dt0)        

    def szám_időtartam_szám(self):              # három hónapja negyedikén
        szám,időtartam,napon=self.outvalues
        időtartam_in=self.invalues[1]
        if időtartam_in!='honapja': return None
        szám=-szám
        return Ttext2date.sub_hónapszám_múlvaezelőtt_napon(szám,napon,self.date0)        


    def szám_időtartam_múlvaezelőtt_hétnapja(self):             # 4 héttel korábban pénteken, két hét múlva hétvégén
        szám,időtartam,múlvaezelőtt,hétnapja=self.outvalues
        if időtartam!='hét': return None
        if múlvaezelőtt=='ezelőtt': szám=-szám
        return Ttext2date.sub_hétszám_múlvaezelőtt_hétnapján(szám,hétnapja,self.dt0)        

    def szám_időtartam_hétnapja(self):                      # két hete szombaton
        szám,időtartam,hétnapja=self.outvalues
        if időtartam!='hét': return None
        szám=-szám
        if self.invalues[1]!='hete': return None
        return Ttext2date.sub_hétszám_múlvaezelőtt_hétnapján(szám,hétnapja,self.dt0)        

    def időtartam(self):                # "a héten" "a hónap", "az év", "a félév", "az évszázad"
        időtartam,=self.outvalues
        időtartam_in,=self.invalues
        if not beginwith(időtartam_in,'a |az '): return None     # a keresőmintákban benne van a névelős változat is (pl. "a hét")
        return Ttext2date.sub_múltjövő_időtartam(időtartam,'most',self.today)


    def múltjövő_időtartam(self):       # múlt héten, előző évben, következő hónapban, jövő félévben, következő héten
        múltjövő,időtartam=self.outvalues

        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None

        return Ttext2date.sub_múltjövő_időtartam(időtartam,múltjövő,dt0)

    def múltjövő_szám_időtartam(self):  # a következő két hónapban
        múltjövő,szám,időtartam = self.outvalues
        if not múltjövő in ['következő','előző']: return None     # "jövő" "múlt" itt nem értelmezhető
        szám_in=self.invalues[1]
        if Ttext2date.sub_is_sorszam(szám_in): return None   # nem lehet sorszám
        utánielőtti=kodto(múltjövő,'előző:előtti//következő:utáni')
        return Ttext2date.sub_utánielőtti_időszak((self.dt0,None),utánielőtti,szám,szám_in,időtartam)


    def múltjövő_évszak(self):          # múlt nyáron, ezen a télen, jövő tavasszal
        múltjövő,évszak = self.outvalues        # évszak: '3','6','9','12'
        
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None

        return Ttext2date.sub_múltjövő_évszak(múltjövő,évszak,dt0)


    def múltjövő_időtartam_évszak(self):    # múlt év nyarán, jövő év tavasszal
        múltjövő,időtartam,évszak = self.outvalues
        if időtartam!='év': return None
        
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None
        
        return Ttext2date.sub_múltjövő_évszak(múltjövő,évszak,dt0)

    def múltjövő_hónapnév(self):    # jövő májusban, múlt szeptemberben  (nem "következő"/"előző" a jelentése, hanem "jövőre","tavaly")
        múltjövő,honap=self.outvalues      
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None
        return Ttext2date.sub_múltjövő_hónapnév(múltjövő,int(honap),dt0)

    def múltjövő_időtartam_hónapnév(self):  # jövő év február
        múltjövő,időtartam,honap = self.outvalues
        if időtartam!='év': return None
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None
        if múltjövő=='következő': múltjövő='jövő'   # "jövő év" jelentés
        elif múltjövő=='előző': múltjövő='múlt'
        return Ttext2date.sub_múltjövő_hónapnév(múltjövő,int(honap),dt0)

    def múltjövő_időtartam_hónapnév_szám(self):  # jövő év február 4-én
        múltjövő,időtartam,honap,szám = self.outvalues
        if időtartam!='év': return None
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None
        szám_in=self.invalues[3]
        return Ttext2date.sub_múltjövő_hónapnév_szám(múltjövő,honap,szám,szám_in,dt0)


    def múltjövő_hónapnév_szám(self):  # jővő május 3-án, előző február 4-én  (nem "következő"/"előző" a jelentése, hanem "jövőre","tavaly")
        múltjövő,honap,szám=self.outvalues
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None

        szám_in=self.invalues[2]
        return Ttext2date.sub_múltjövő_hónapnév_szám(múltjövő,honap,szám,szám_in,dt0)




    def múltjövő_időtartam_szám(self):  # jövő hónap harmadikán
        múltjövő,időtartam,szám=self.outvalues
        if időtartam!= 'hónap':  return None
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None

        honap=self.dt0.month
        year=self.dt0.year

        szám_in=self.invalues[2]
        if endwith(szám_in,'dik|elsö'): return None
        try: dtout=datetime(year,int(honap),szám)
        except: return None
        if múltjövő in ['múlt','előző']: dtout=fn_dateadd(dtout,-1,'month')
        elif múltjövő in ['jövő','következő']: dtout=fn_dateadd(dtout,1,'month')
        return (dtout,None)


    def múltjövő_hétnapja(self):        # "jövő szombaton"
        múltjövő,hétnapja = self.outvalues
        
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None
      
        # Más a jelentése a "jövő péntek" és a "következő péntek" kifejezésnek (a "jövő" a "jövő hét péntek"-re utal )
        if múltjövő=='következő':
            dátum=(dt0,None)
            return Ttext2date.sub_dátum_utánelőtti_sorszám_hétnapja(dátum,'utáni',1,hétnapja)
        elif múltjövő=='előző':
            dátum=(dt0,None)
            return Ttext2date.sub_dátum_utánelőtti_sorszám_hétnapja(dátum,'előtti',1,hétnapja)
        else:       
            return Ttext2date.sub_múltjövő_hétnapja(múltjövő,hétnapja,dt0)
        
    def múltjövő_időtartam_hétnapja(self):  # "múlt hét pénteken"
        múltjövő,időtartam,hétnapja = self.outvalues
        if időtartam!='hét': return None
        dt0=Ttext2date.sub_múltjövő_dt0(self,múltjövő)
        if not dt0: return None
        return Ttext2date.sub_múltjövő_hétnapja(múltjövő,hétnapja,dt0)


    def dátum_tólig(self):
        dátum,tólig = self.outvalues
        dt1,dt2 = dátum
        if dt2==None: dt2=dt1

        if tólig=='tól':
            dtout=dt1
            dtout2=self.datemax
        elif tólig=='ig':
            # ha va előtte "tól" is, akkor ne módosítson semmit
            if vanbenne(self.invalues[0],'tólig'): return None
            dtout=self.datemin
            dtout2=dt2
        else: return None
        return (dtout,dtout2)


    def dátum_utánelőtt(self):
        dátum,utánelőtt = self.outvalues
        dt1,dt2 = dátum
        if dt2==None: dt2=dt1

        if utánelőtt=='előtt':
            dtout=self.datemin
            if dt1==self.datemin: dtout2=dt2   # ? nem biztos hogy kell
            else: dtout2=fn_dateadd(dt1,-1)
        elif utánelőtt=='után':
            if dt2==self.datemax: dtout=dt1    # példa: "március 1-től az utána következő péntekig"
            else: dtout=fn_dateadd(dt2,1)
            dtout2=self.datemax
        else: return None
        return (dtout,dtout2)



    def dátum_tólig_szám_időtartam(self):       # "hétfőtől 5 nap", "december 1-ig két hét"
        dátum,tólig,szám,időtartam = self.outvalues
        szám_in=self.invalues[2]
        # if Ttext2date.sub_is_sorszam(szám_in): return None        # a sorszámozott naptári időszakok itt nem értelmezhetők
        # ellenpélda: "hétfőtől számítva a második héten"  helyesen: "hétfő utáni második héten", "hétfő után a második héten"
        # - ha a sorszámos változatot is átengedi a függvény, akkor a "2020 második negyedévtől a harmadik negyedévig" teljesen fals eredményt ad
        return Ttext2date.sub_utánielőtti_időszak(dátum,tólig,szám,szám_in,időtartam)


    def dátum_tólig_szám_időtartam_tólig(self): # "hétfőtől 5 napig", "december 1-től két hétig
        dátum,tólig,szám,időtartam,tólig2 = self.outvalues
        if tólig!='tól' or tólig2!='ig': return None
        szám_in=self.invalues[2]
        if Ttext2date.sub_is_sorszam(szám_in): return None        # a sorszámozott naptári időszakok itt nem értelmezhetők
        # - ha a sorszámos változatot is átengedi a függvény, akkor a "2020 második negyedévtől a harmadik negyedévig" teljesen fals eredményt ad
        return Ttext2date.sub_utánielőtti_időszak(dátum,tólig,szám,szám_in,időtartam)


    def szám_időtartam_dátum_tólig(self):       # "5 nap hétfőtől",  két hét december 1-ig
        szám,időtartam,dátum,tólig = self.outvalues
        szám_in=self.invalues[0]
        if Ttext2date.sub_is_sorszam(szám_in): return None        # a sorszámozott naptári időszakok itt nem értelmezhetők
        return Ttext2date.sub_utánielőtti_időszak(dátum,tólig,szám,szám_in,időtartam)

    def dátum_tólig_szám_időtartam_elejevége_tólig(self):       # "március első hétfőjétől a második hét végéig"
        dátum,tólig,szám,időtartam,elejevége,tólig2 = self.outvalues
        szám_in=self.invalues[2]
        if tólig!='tól' or tólig2!='ig': return None
        return Ttext2date.sub_dátumtól_sorszám_időtartam_végéig(dátum,tólig,szám,szám_in,időtartam,elejevége)


    def dátum_tólig_múltjövő_időtartam_elejevége_tólig(self):   # "március első hétfőjétől a következő hónap közepéig"
        dátum,tólig,múltjövő,időtartam,elejevége,tólig2 = self.outvalues
        múltjövő_in=self.invalues[2]
        if not beginwith(múltjövő_in,'követ'): return None          # csak a "következő" jó
        szám=1          # "második"-nak felel meg
        szám_in='elsö'
        if tólig!='tól' or tólig2!='ig': return None
        return Ttext2date.sub_dátumtól_sorszám_időtartam_végéig(dátum,tólig,szám,szám_in,időtartam,elejevége)


    def dátum_tólig_időtartam_elejevége_tólig(self):            # "március első hétfőjétől a hónap végéig"
        dátum,tólig,időtartam,elejevége,tólig2 = self.outvalues
        szám=0
        szám_in='nulladik'
        if tólig!='tól' or tólig2!='ig': return None
        return Ttext2date.sub_dátumtól_sorszám_időtartam_végéig(dátum,tólig,szám,szám_in,időtartam,elejevége)


    def dátum_tólig_szám_hétnapja_tólig(self):          # "december 5-től a második keddig", "hétfőtől az első hétvégéig"
        dátum,tólig,szám,hétnapja,tólig2 = self.outvalues
        szám_in=self.invalues[2]
        if not Ttext2date.sub_is_sorszam(szám_in): return None
        if tólig!='tól' or tólig2!='ig': return None
        dt1,dt2=dátum
        # záródátum:
        dt1L,dt2L = Ttext2date.sub_sorszám_hétnapja(dt1,self.datemax,szám,hétnapja)
        if dt2L==None: return None
        return (dt1,dt2L)

    def dátum_tólig_hétnapja_tólig(self):               # március második hetében keddtől csütörtökig
        dátum,tólig,hétnapja,tólig2 = self.outvalues
        if tólig!='tól' or tólig2!='ig': return None
        dt1,dt2=dátum
        if dt2==None: dt2=dt1
        # záródátum:
        dt1L,dt2L = Ttext2date.sub_sorszám_hétnapja(fn_dateadd(dt2,1),self.datemax,1,hétnapja)
        if dt2L==None: return None
        return (dt1,dt2L)


    def dátum_utánelőtt_szám_időtartam(self):       # szombat után két nappal    január 10 előtt 2 héttel  péntek előtt a második héten
        dátum,utánelőtt,szám,időtartam = self.outvalues
        szám_in=self.invalues[2]
        return Ttext2date.sub_utánielőtti_időszak(dátum,utánelőtt,szám,szám_in,időtartam)

    def szám_időtartam_dátum_utánelőtt(self):       # két nappal március után
        szám,időtartam,dátum,utánelőtt = self.outvalues
        szám_in=self.self.invalues[0]
        return Ttext2date.sub_utánielőtti_időszak(dátum,utánelőtt,szám,szám_in,időtartam)


    def dátum_utánielőtti_szám_időtartam(self):         # "szombat utáni első hét"  "január 10 előtti 2 nap"
        dátum,utánielőtti,szám,időtartam = self.outvalues       
        szám_in = self.invalues[2]
        return Ttext2date.sub_utánielőtti_időszak(dátum,utánielőtti,szám,szám_in,időtartam)

    def dátum_utánielőtti_utolsó_időtartam(self):       # "szombat előtti utolsó munkanap"
        dátum,utánielőtti,szám,időtartam = self.outvalues       # szám: "utolsó", "utolsóelőtti"
        szám_in = Ttext2date.invalues[2]
        return Ttext2date.sub_utánielőtti_időszak(dátum,utánielőtti,szám,szám_in,időtartam)

    def dátum_utánielőtti_időtartam(self):              # "jövő hét utáni hét"
        dátum,utánielőtti,időtartam = self.outvalues
        szám = 1
        szám_in=''
        return Ttext2date.sub_utánielőtti_időszak(dátum,utánielőtti,szám,szám_in,időtartam)


    def dátum_utánielőtti_szám_hétnapja(self):          # "december 1 utáni második hétvége"
        dátum,utánielőtti,szám,hétnapja = self.outvalues        

        szám_in = self.invalues[2]
        if not Ttext2date.sub_is_sorszam(szám_in): return None   

        return Ttext2date.sub_dátum_utánelőtti_sorszám_hétnapja(dátum,utánielőtti,szám,hétnapja)



    def dátum_utánielőtti_utolsó_hétnapja(self):            
        dátum,utánielőtti,szám,hétnapja = self.outvalues        

        return Ttext2date.sub_dátum_utánelőtti_sorszám_hétnapja(dátum,utánielőtti,szám,hétnapja)


    def dátum_utánielőtti_hétnapja(self):               # "karácsony előtti péntek"
        dátum,utánielőtti,hétnapja = self.outvalues
        return Ttext2date.sub_dátum_utánelőtti_sorszám_hétnapja(dátum,utánielőtti,1,hétnapja)


    def dátum_elejevége_elejevége(self):                            #  "január közepe-vége", "január közepe és vége között
        dátum,elejevége,elejevége2 = self.outvalues
        return Ttext2date.sub_dátum_elejevége_elejevége(dátum,elejevége,elejevége2)

    def dátum_elejevége_tólig_elejevége(self):                      #  "január közepétől a végéig
        dátum,elejevége,tólig,elejevége2 = self.outvalues
        if tólig!='tól':  return None
        return Ttext2date.sub_dátum_elejevége_elejevége(dátum,elejevége,elejevége2)

    def időtartam_elejevége_elejevége(self):                       #  "a hét közepe és vége között"
        időtartam,elejevége,elejevége2 = self.outvalues
       
        if self.patternword_előtte=='[szám]': return None   # nem állhat előtte szám, pl. "XIX. század közepétől a végéig"
        dátum=Ttext2date.sub_múltjövő_időtartam(időtartam,'most',self.today)
        return Ttext2date.sub_dátum_elejevége_elejevége(dátum,elejevége,elejevége2)


    def időtartam_elejevége_tólig_elejevége(self):                 #  "a hét elejétől a végéig"
        időtartam,elejevége,tólig,elejevége2 = self.outvalues
        if tólig!='tól':  return None
        if self.patternword_előtte=='[szám]': return None   # nem állhat előtte szám, pl. "XIX. század közepétől a végéig"

        dátum=Ttext2date.sub_múltjövő_időtartam(időtartam,'most',self.today)
        return Ttext2date.sub_dátum_elejevége_elejevége(dátum,elejevége,elejevége2)


    def dátum_szám_törtrész(self):                                 # "2022. első felében", "XIX. század második felében", "január harmadik hamadában",  "múlt hét első felében"
        dátum,szám,törtrész = self.outvalues
        szám_in = self.invalues[1]
        if not Ttext2date.sub_is_sorszam(szám_in): return None

        return Ttext2date.sub_dátum_sorszám_törtrész(dátum,szám,törtrész)

    def dátum_utolsó_törtrész(self):
        dátum,szám,törtrész = self.outvalues
        return Ttext2date.sub_dátum_sorszám_törtrész(dátum,szám,törtrész)

    def dátum_elejevége(self):                                     # "2022. elején","február közepén","XIX. század végén", "jövő hét elején"
        dátum,elejevége = self.outvalues
        # Ha a [dátum] végén is elejevége volt, akkor egyedi kezelés (pl. "január közepétől a végéig")
        dátum_minta=self.invalues[0]
        if endwith(dátum_minta,'\[elejevége\]'): return None
        törtrész=3
        szám=int(elejevége)         # Hányadik harmad:   eleje:1  közepe: 2  vége:3
        return Ttext2date.sub_dátum_sorszám_törtrész(dátum,szám,törtrész)


    def időtartam_szám_törtrész(self):              # "az év első felében",   "a hét második felében"
        időtartam,szám,törtrész = self.outvalues
        szám_in = self.invalues[1]
        if not Ttext2date.sub_is_sorszam(szám_in): return None
        if self.patternword_előtte in ['[szám]','[múltjövő]']: return None   # nem állhat előtte szám, pl. "XIX. század első felében" példamondat "század első felében"-ként értelmeződne
        dátum=Ttext2date.sub_múltjövő_időtartam(időtartam,'most',self.today)
        return Ttext2date.sub_dátum_sorszám_törtrész(dátum,szám,törtrész)

    def időtartam_elejevége(self):                  # "hét közepén", "a hónap elejétől", "év végén"
        időtartam,elejevége = self.outvalues
        if self.patternword_előtte in ['[szám]','[múltjövő]']: return None   # nem állhat előtte szám, pl. "XIX. század első felében" példamondat "század első felében"-ként értelmeződne
        dátum=Ttext2date.sub_múltjövő_időtartam(időtartam,'most',self.today)
        törtrész=3
        szám=int(elejevége)         # Hányadik harmad:   eleje:1  közepe: 2  vége:3
        return Ttext2date.sub_dátum_sorszám_törtrész(dátum,szám,törtrész)


    def dátum_szám_időtartam(self):                 # "jövő év második félévében", "XIX. század harmadik évtizedében", "február első hetében"
        dátum,szám,időtartam = self.outvalues

        # A dátum végén nem lehet [tólig]
        if endwith(self.invalues[0],r'\[tólig\]'): return None

        # A dátumnak időszakot kell tartalmaznia
        dt1,dt2 = dátum
        if dt1==None or dt2==None or dt2<=dt1: return None

        if Ttext2date.sub_is_sorszam(self.invalues[1]):
            return Ttext2date.sub_dátum_sorszám_időtartam(dátum,szám,időtartam)

        # "XIX. század 20-as éveiben"
        elif beginwith(self.invalues[2],'évei|évek'):       
            if dt1.year%100==0 and dt1.month==1 and dt1.day==1 and szám%10==0:
                dtout=datetime(dt1.year + szám,1,1)
                dtout2=datetime(dt1.year + szám + 9,12,31)

    def dátum_szám_időtartam_tólig_szám_időtartam_tólig(self):  # a hét első napjától a harmadik napjáig
        dátum,szám,időtartam,tólig,szám2,időtartam2,tólig2 = self.outvalues
        if tólig!='tól' or tólig2!='ig': return None
        if not Ttext2date.sub_is_sorszam(self.invalues[1]): return None
        if not Ttext2date.sub_is_sorszam(self.invalues[4]): return None
        return Ttext2date.sub_dátum_sorszám_időtartamtól_sorszám_időtartamig(dátum,szám,időtartam,szám2,időtartam2)

    def dátum_szám_időtartam_tólig_szám_tólig(self):   # a hét első napjától a harmadikig
        dátum,szám,időtartam,tólig,szám2,tólig2 = self.outvalues
        if tólig!='tól' or tólig2!='ig': return None
        if not Ttext2date.sub_is_sorszam(self.invalues[1]): return None
        if not Ttext2date.sub_is_sorszam(self.invalues[4]): return None
        return Ttext2date.sub_dátum_sorszám_időtartamtól_sorszám_időtartamig(dátum,szám,időtartam,szám2,időtartam)

    def dátum_szám_szám_időtartam(self):   # a hét első és ötödik napja között
        dátum,szám,szám2,időtartam = self.outvalues
        if not Ttext2date.sub_is_sorszam(self.invalues[1]): return None
        if not Ttext2date.sub_is_sorszam(self.invalues[2]): return None
        return Ttext2date.sub_dátum_sorszám_időtartamtól_sorszám_időtartamig(dátum,szám,időtartam,szám2,időtartam)



    def dátum_utolsó_időtartam(self):               # "jövő év utolsó napján", "XIX. század utolsó évtizedében", "február első hetében"
        dátum,szám,időtartam = self.outvalues

        # A dátum végén nem lehet [tólig]
        if endwith(self.invalues[0],r'\[tólig\]'): return None

        # A dátumnak időszakot kell tartalmaznia
        dt1,dt2 = dátum
        if dt1==None or dt2==None or dt2<=dt1: return None

        return Ttext2date.sub_dátum_sorszám_időtartam(dátum,szám,időtartam)



    def dátum_szám_hétnapja(self):                  # jövő hónap első hétfőjén"
        dátum,szám,hétnapja = self.outvalues
        if not Ttext2date.sub_is_sorszam(self.invalues[1]): return None
        dt1,dt2 = dátum
        return Ttext2date.sub_sorszám_hétnapja(dt1,dt2,szám,hétnapja)


    def dátum_hétnapja(self):                       # jövő hónap második hetében kedden"
        dátum,hétnapja = self.outvalues
        szám=None           # alapesetben "első hétfő" ... lesz a jelentése, kivéve "hétköznap" ahol nem nap hanem egy tartomány a kimenet 
        dt1,dt2 = dátum
        # csak akkor fogadja el, ha a dátum egy naptári hetet jelöl (pl. "március második hete")
        if dt1.weekday()!=0 or dt2==None or dt2!=fn_dateadd(dt1,6): return None
        return Ttext2date.sub_sorszám_hétnapja(dt1,dt2,szám,hétnapja)


    def dátum_utolsó_hétnapja(self):                # "február utolsó hétvégéjén"
        dátum,szám,hétnapja = self.outvalues
        dt1,dt2 = dátum
        return Ttext2date.sub_sorszám_hétnapja(dt1,dt2,szám,hétnapja)


    def dátum_szám(self):                           # "2023 február 5-től 10-ig",  "2023.02.05-10"
        dátum,szám = self.outvalues
                
        dtout=None
        dtout2=None
        dt1,dt2 = dátum
        if dt2==None or dt2==dt1:           # egyetlen nap
            dátum_minta = self.invalues[0]
            if endwith(dátum_minta,r'\[szám\]') and szám>=1 and szám<=31:
                try: dtout2=datetime(dt1.year,dt1.month,szám)
                except: dtout2=None
                if dtout2!=None: dtout=dt1
        return (dtout,dtout2)


    def dátum_dátum(self):                          # "2023 évben május végén",  "2023.02.01 - 2025.03.31",  "2023.február és 2025.január között"
        dátumA,dátumB = self.outvalues
        mintaA,mintaB = self.invalues
        return Ttext2date.sub_dátum_dátum(dátumA,mintaA,dátumB,mintaB)

    def dátum_dátum_tólig(self):
        dátumA,dátumB,tóligB = self.outvalues
        if tóligB!='ig': return None
        mintaA,mintaB,minta__ = self.invalues
        return Ttext2date.sub_dátum_dátum(dátumA,mintaA,dátumB,mintaB)

    def dátum_tólig_dátum_tólig(self):              # "2023 februártól májusig",  "téltől tavaszig"
        dátumA,tóligA,dátumB,tóligB = self.outvalues
        if tóligA!='tól' or tóligB!='ig': return None
        mintaA,minta_,mintaB,minta__ = self.invalues
        return Ttext2date.sub_dátum_dátum(dátumA,mintaA,dátumB,mintaB)

    def dátum_tólig_múltjövő_dátum_tólig(self):              # "2023 februártól májusig",  "téltől tavaszig"
        dátumA,tóligA,múltjövő,dátumB,tóligB = self.outvalues
        if tóligA!='tól' or tóligB!='ig': return None
        if múltjövő!='következő': return None

        mintaA,minta_,mintaB,minta__ = self.invalues
        return Ttext2date.sub_dátum_dátum(dátumA,mintaA,dátumB,mintaB)


methods=Ttext2date()        # egyetlen példány


# MINTÁZATOK
pattern2method={
    '[szám] [szám] [szám]': methods.szám_szám_szám,             # "2022 01 01",  "2022.01.01"  "2022-01-01", "2020 I. elseje"
    '[szám] [szám] [időtartam] [szám]': methods.szám_szám_időtartam_szám,   # "2022. II.hó 4."
    '[szám] [hónapnév] [szám]': methods.szám_hónapnév_szám,     #  "2020 január 1."
    '[szám] [hónapnév]': methods.szám_hónapnév,                 #  "2020 január"
    '[hónapnév] [szám]': methods.hónapnév_szám,                 #  "január 1."
    '[szám] [szám]': methods.szám_szám,                         # "2022 01", "01 12", "2012-2014"
    '[szám] [évszak]': methods.szám_évszak,                     # "2015 tavasz"
    '[szám]': methods.szám,                                     # "másodikán", "másodikától", "20220102", "0102"
    '[maholnap]': methods.maholnap,                             # "ma", "holnap", "tegnap"
    '[maholnap] [időtartam]': methods.maholnap_időtartam,       # "mai napon"
    '[maholnap] [utánelőtt]': methods.maholnap_utánelőtt,       # "holnap után"  (különírva)
    '[hónapnév]': methods.hónapnév,                             # "január"
    '[hónapnév] [időtartam]': methods.hónapnév_időtartam,       # "január hónap"
    '[hétnapja]': methods.hétnapja,                             # "hétfő", "hétvége", "hétköznap"
    '[szám] [hétnapja]': methods.szám_hétnapja,                 # "második hétfő" (idén)  "120. munkanap" (idén)
    '[utolsó] [hétnapja]': methods.utolsó_hétnapja,             # "utolsó hétfő" (idén)
    '[évszak]': methods.évszak,                                 # "tavasz" (idén)
    '[évnapja]': methods.évnapja,                               # "karácsony", "újév", ...
    '[szám] [évnapja]': methods.szám_évnapja,                   # "2023 karácsony"
    '[dátum] [évnapja]': methods.dátum_évnapja,                 # "tavaly karácsony"   (dátum csak teljes év lehet)
    '[forduló]': methods.forduló,                               # "az ezredfordulón"   
    '[egyedi]': methods.egyedi,                                 # "rendszerváltáskor"
    '[szám] [időtartam] [múlvaezelőtt]': methods.szám_időtartam_múlvaezelőtt,   # 2 nap múlva, 3 év múlva,  négy hét múlva,  egy évvel ezelőtt
    '[szám] [időtartam]': methods.szám_időtartam,               # "2022 év", "90-es években", "két hete", "12 éve", "20 napja", XIX. században, második félévben, utolsó negyedévben, 12. héten, 120. napon
    '[szám] [időtartam] [múlvaezelőtt] [hónapnév]': methods.szám_időtartam_múlvaezelőtt_hónapnév,   # 3 évvel ezelőtt decemberben, két év múlva októberben
    '[szám] [időtartam] [hónapnév]': methods.szám_időtartam_hónapnév,                               # 3 éve decemberben, két éve októberben
    '[szám] [időtartam] [múlvaezelőtt] [szám]': methods.szám_időtartam_múlvaezelőtt_szám,           # 2 hónappal ezelőtt 5-én, három hónap múlva hatodikán
    '[szám] [időtartam] [szám]': methods.szám_időtartam_szám,                                       # három hónapja negyedikén
    '[szám] [időtartam] [múlvaezelőtt] [hétnapja]': methods.szám_időtartam_múlvaezelőtt_hétnapja,   # 4 héttel korábban pénteken, két hét múlva hétvégén
    '[szám] [időtartam] [hétnapja]': methods.szám_időtartam_hétnapja,                               # két hete szombaton
    '[időtartam]': methods.időtartam,                                           # "a héten" "a hónap", "az év", "a félév", "az évszázad"
    '[múltjövő]': methods.múltjövő,                             # "most"
    '[múltjövő] [évnapja]': methods.múltjövő_évnapja,           # "jövő karácsony", "előző húsvét"
    '[múltjövő] [forduló]': methods.múltjövő_forduló,           # "az előző századvégen"
    '[múltjövő] [időtartam]': methods.múltjövő_időtartam,                       # múlt héten, előző évben, következő hónapban, jövő félévben, következő héten
    '[múltjövő] [szám] [időtartam]': methods.múltjövő_szám_időtartam,           # a következő két hónapban, az előző 3 héten
    '[múltjövő] [évszak]': methods.múltjövő_évszak,                             # múlt nyáron, ezen a télen, következő tavasszal
    '[múltjövő] [időtartam] [évszak]': methods.múltjövő_időtartam_évszak,       # múlt év nyarán, jövő év tavasszal
    '[múltjövő] [hónapnév]': methods.múltjövő_hónapnév,                         # jövő májusban, múlt szeptemberben  (nem "következő"/"előző" a jelentése, hanem "jövőre","tavaly")
    '[múltjövő] [időtartam] [hónapnév]': methods.múltjövő_időtartam_hónapnév,   # jövő év február
    '[múltjövő] [időtartam] [hónapnév] [szám]': methods.múltjövő_időtartam_hónapnév_szám,   # jövő év február 4-én
    '[múltjövő] [hónapnév] [szám]': methods.múltjövő_hónapnév_szám,             # jővő május 3-án, előző február 4-én  (nem "következő"/"előző" a jelentése, hanem "jövőre","tavaly")
    '[múltjövő] [időtartam] [szám]': methods.múltjövő_időtartam_szám,           # jövő hónap harmadikán
    '[múltjövő] [hétnapja]': methods.múltjövő_hétnapja,                         # jövő szombaton
    '[múltjövő] [időtartam] [hétnapja]': methods.múltjövő_időtartam_hétnapja,   # "múlt hét pénteken"
    '[dátum] [tólig]': methods.dátum_tólig,                                     # 2020 novembertől,  jövő év tavaszig
    '[dátum] [dátum] [tólig]': methods.dátum_dátum_tólig,                   # "
    '[dátum] [tólig] [dátum] [tólig]': methods.dátum_tólig_dátum_tólig,     # "2023 februártól májusig",  "téltől tavaszig"
    '[dátum] [tólig] [múltjövő] [dátum] [tólig]': methods.dátum_tólig_múltjövő_dátum_tólig,      # "2023 februártól a következő májusig"
    '[dátum] [tólig] [szám] [időtartam]': methods.dátum_tólig_szám_időtartam,                   # "hétfőtől 5 nap", "december 1-ig két hét"
    '[dátum] [tólig] [szám] [időtartam] [tólig]': methods.dátum_tólig_szám_időtartam_tólig,     # "hétfőtől 5 napig", "december 1-től két hétig
    '[szám] [időtartam] [dátum] [tólig]': methods.szám_időtartam_dátum_tólig,                   # "5 nap hétfőtől",  két hét december 1-ig
    '[dátum] [tólig] [szám] [időtartam] [elejevége] [tólig]': methods.dátum_tólig_szám_időtartam_elejevége_tólig,   # "március első hétfőjétől a második hét végéig"
    '[dátum] [tólig] [múltjövő] [időtartam] [elejevége] [tólig]': methods.dátum_tólig_múltjövő_időtartam_elejevége_tólig, # "március első hétfőjétől a következő hónap közepéig"
    '[dátum] [tólig] [időtartam] [elejevége] [tólig]': methods.dátum_tólig_időtartam_elejevége_tólig,   # "március első hétfőjétől a hónap végéig"
    '[dátum] [tólig] [szám] [hétnapja] [tólig]': methods.dátum_tólig_szám_hétnapja_tólig,       # "december 5-től a második keddig", "hétfőtől az első hétvégéig"
    '[dátum] [tólig] [hétnapja] [tólig]': methods.dátum_tólig_hétnapja_tólig,                   # március második hetében keddtől csütörtökig
    '[dátum] [utánelőtt]': methods.dátum_utánelőtt,                             # 2020 után, jövő év tavasz előtt
    '[dátum] [utánelőtt] [szám] [időtartam]': methods.dátum_utánelőtt_szám_időtartam,           # szombat után két nappal    január 10 előtt 2 héttel  péntek előtt a második héten
    '[szám] [időtartam] [dátum] [utánelőtt]': methods.szám_időtartam_dátum_utánelőtt,           # két nappal március után
    '[dátum] [utánielőtti] [szám] [időtartam]': methods.dátum_utánielőtti_szám_időtartam,       # "szombat utáni első hét"  "január 10 előtti 2 nap"
    '[dátum] [utánielőtti] [utolsó] [időtartam]': methods.dátum_utánielőtti_utolsó_időtartam,   # "szombat előtti utolsó munkanap"
    '[dátum] [utánielőtti] [időtartam]': methods.dátum_utánielőtti_időtartam,                   # "jövő hét utáni hét"
    '[dátum] [utánielőtti] [szám] [hétnapja]': methods.dátum_utánielőtti_szám_hétnapja,         # "december 1 utáni második hétvége"
    '[dátum] [utánielőtti] [utolsó] [hétnapja]': methods.dátum_utánielőtti_utolsó_hétnapja,     # "december 1 előtti utolsó hétvége"
    '[dátum] [utánielőtti] [hétnapja]': methods.dátum_utánielőtti_hétnapja,                     # "karácsony előtti péntek"
    '[dátum] [elejevége] [elejevége]': methods.dátum_elejevége_elejevége,                       #  "január közepe-vége", "január közepe és vége között
    '[dátum] [elejevége] [tólig] [elejevége]': methods.dátum_elejevége_tólig_elejevége,         #  "január közepétől a végéig
    '[időtartam] [elejevége] [elejevége]': methods.időtartam_elejevége_elejevége,               #  "a hét közepe és vége között
    '[időtartam] [elejevége] [tólig] [elejevége]': methods.időtartam_elejevége_tólig_elejevége, #  "a hét elejétől a végéig"
    '[dátum] [szám] [törtrész]': methods.dátum_szám_törtrész,               # "2022. első felében", "XIX. század második felében", "január harmadik hamadában",  "múlt hét első felében"
    '[dátum] [utolsó] [törtrész]': methods.dátum_utolsó_törtrész,           # "2022 utolsó harmadában"
    '[dátum] [elejevége]': methods.dátum_elejevége,                         # "2022. elején","február közepén","XIX. század végén", "jövő hét elején"
    '[időtartam] [szám] [törtrész]': methods.időtartam_szám_törtrész,       # "az év első felében",   "a hét második felében"
    '[időtartam] [elejevége]': methods.időtartam_elejevége,                 # "hét közepén", "a hónap elejétől", "év végén"
    '[dátum] [szám] [időtartam]': methods.dátum_szám_időtartam,             # "jövő év második félévében", "XIX. század harmadik évtizedében", "február első hetében"
    '[dátum] [szám] [időtartam] [tólig] [szám] [időtartam] [tólig]': methods.dátum_szám_időtartam_tólig_szám_időtartam_tólig,      # "a hét második napjától a negyedik napjáig"
    '[dátum] [szám] [időtartam] [tólig] [szám] [tólig]': methods.dátum_szám_időtartam_tólig_szám_tólig,      # "a hét második napjától a negyedikig"
    '[dátum] [szám] [szám] [időtartam]': methods.dátum_szám_szám_időtartam,      # "a hét második és negyedik napja között"
    '[dátum] [utolsó] [időtartam]': methods.dátum_utolsó_időtartam,         # "jövő év utolsó napján", "XIX. század utolsó évtizedében", "február első hetében"
    '[dátum] [szám] [hétnapja]': methods.dátum_szám_hétnapja,               # jövő hónap első hétfőjén"
    '[dátum] [hétnapja]': methods.dátum_hétnapja,                           # jövő hónap második hetében kedden"
    '[dátum] [utolsó] [hétnapja]': methods.dátum_utolsó_hétnapja,           # "február utolsó hétvégéjén"
    '[dátum] [szám]': methods.dátum_szám,                                   # "2023 februártól 5-től 10-ig",  "2023.02.05-10"
    '[dátum] [dátum]': methods.dátum_dátum,                                 # "2023 évben május végén",  "2023.02.01 - 2025.03.31",  "2023.február és 2025.január között"
    }

def fn_teszt(pattern):
    method=pattern2method.get(pattern)
    if method:
        methods.szám=2000

        return method(pattern,'','','','','')
    else:
        return 'sikertelen'


# KERESŐMINTÁK (lookup)
# Formátum soronként:   keresőminták:entityname,outvalue
#      - keresőminták:  több minta is megadható '|' határolással
#         - "." a keresőminta végén, ha teljes szavas találat az elvárás (egyébként beginwith)
#         - egy-egy keresőminta több szavas is lehet (pl. "mindenszentek nap"). Többszavas minta esetén számít a szavak sorrendje. 
#         - a szavakon belül csak betűk és számjegyek lehetnek (de a "hét" szón kívül nem lehet benne szám-szó, mert a számokat külön kezeli az algoritmus) 
#         - kisbetű-nagybetű és hosszú ékezet eltérés érdektelen (a-á, e-é, o-ö, u-ü eltérés viszont számít)
#      - entityname:  szögletes zárójeles helyettesítőjelként kerül be a mintázatba  (kötelezően egyszavas)
#         - az entityname lehet "none": ebben az esetben nem a helyettesítőjel íródik be a mintázatba, hanem az outvalue 
#           (szabványosítás, szinonimák összevonása)
#         - új entity-név bevezetése esetén a pattern2method szótárba fel kell venni az entity-névre támaszkodó
#           mintázatokat, és a hozzájuk tartozó interpretáló algoritmust
#      - outvalue:   a szabványosított / kivonatolt érték   (a mintázatot értelmező algoritmus támaszkodik rá)
#         - "évnapja" esetén speciális kódolás:  
#             "MMdd",  "MMdd:MMdd",  "húsvét-1", "húsvét-2:húsvét+1  (a húsvét helyébe húsvét vasárnap dátuma íródik)

# Speciális entity:  "stopword"    Kimarad a mintázatból és az outvalues-ből is.

lookup_text2dateG={
    'hétfő|h.':'hétnapja,1',
    'kedd|k.':'hétnapja,2',
    'szerd|sze.|szer.':'hétnapja,3',
    'csüt|cs.':'hétnapja,4',
    'pént|p.':'hétnapja,5',
    'szomb|szo.':'hétnapja,6',
    'vasár|vas.|v.':'hétnapja,7',
    'hétvég':'hétnapja,hétvége',
    'hétköznap|hétközben|munkanap':'hétnapja,hétköznap',

    'január|jan.':'hónapnév,1',
    'február|febr.':'hónapnév,2',
    'március|márc.':'hónapnév,3',
    'április|ápr.':'hónapnév,4',
    'május|máj.':'hónapnév,5',
    'június|jún.|júni.':'hónapnév,6',
    'július|júl.|júli.':'hónapnév,7',
    'augusztus|aug.':'hónapnév,8',
    'szeptember|szept.':'hónapnév,9',
    'október|okt.':'hónapnév,10',
    'november|nov.':'hónapnév,11',
    'december|dec.':'hónapnév,12',

    'ma.|mai.|má':'maholnap,0',
    'holnap':'maholnap,1',
    'holnapután':'maholnap,2',
    'tegnap':'maholnap,-1',
    'tegnapelőtt':'maholnap,-2',

    'századvég|a századvég':'forduló,századvég',
    'századelő|a századelő|századforduló|a századforduló|évszázad forduló|az évszázad forduló':'forduló,századelő',
    'ezredvég|az ezredvég':'forduló,ezredvég',
    'ezredelő|az ezredelő|ezredforduló|az ezredforduló|évezred forduló|az évezred forduló':'forduló,ezredelő',

    'idén':'szám,' + str(datetime.now().year),
    'jövőre':'szám,' + str(datetime.now().year+1),
    'tavaly':'szám,' + str(datetime.now().year-1),
    'tavalyelőtt':'szám,' + str(datetime.now().year-2),

    'évszázad|század|szd.|a század|az évszázad':'időtartam,évszázad',
    'évtized|az évtized':'időtartam,évtized',
    'év.|éve.|évek|évei|évtől|évig|évben|évvel|évé|évre|az év':'időtartam,év',
    'félév|a félév':'időtartam,félév',
    'negyedév|a negyedév':'időtartam,negyedév',
    'hónap|hó.|a hónap':'időtartam,hónap',
    'hét|hete.|heté|a hét':'időtartam,hét',
    'nap':'időtartam,nap',

    'tavasz|tavasszal|a tavasz':'évszak,3',
    'nyár|nyarán|a nyár':'évszak,6',
    'ősz|ősszel|az ősz':'évszak,9',
    'tél|telén|a tél':'évszak,12',

    'múlt|elmúlt':'múltjövő,múlt',
    'előző|megelőző|legutóbbi':'múltjövő,előző',    # más a viszonyítási alapja, mint a "múlt"-nak (dinamikus, szemben a "múlt" fix origójával)
    'jövő':'múltjövő,jövő',
    'következő|utána jövő|rá következő|legközelebbi':'múltjövő,következő',
    'most|jelen|ezen|idei|aktuális|e.|ebben|ettől|eddig':'múltjövő,most',


    'múlva|ezután|azután|később|rá.|követően':'múlvaezelőtt,múlva',
    'ezelőtt|azelőtt|korábban|megelőzően':'múlvaezelőtt,ezelőtt',

    'után':'utánelőtt,után',
    'előtt':'utánelőtt,előtt',

    'tól.|től.|kezdődő.|induló.|':'tólig,tól',          # előtte kell egy előfeldolgozás: kötőjeles vagy egybeírt rag leválasztása külön szóként (lásd d_annotate)
    'ig.|záruló.|záródó.|lezáruló.|befejeződő.|végződő.': 'tólig,ig',

    'utáni|követő|kezdve|után indul|után kezdőd|után következ|után jövő':'utánielőtti,utáni',
    'előtti|megelőző|előtt zár|előtt befejez':'utánielőtti,előtti',

    'utolsó': 'utolsó,utolsó',
    'utolsó előtti|utolsóelőtti':'utolsó,utolsóelőtti',

    'fele.|felében|felétől|feléig':'törtrész,2',
    'harmada|harmadá':'törtrész,3',
    'negyede|negyedé':'törtrész,4',

    'elej|kezdőnap|kezdet':'elejevége,1',
    'közepe.|közepé':'elejevége,2',
    'vége.|végé|zárónap|zárás':'elejevége,3',

    'karácsony':'évnapja,1225:1226',
    'szenteste|karácsony este':'évnapja,1224',
    'szilveszter|évvég':'évnapja,1231',
    'újév|évkezdet':'évnapja,0101',
    'mikulás|télapó':'évnapja,1206',
    'húsvét':'évnapja,húsvét_',
    'húsvétpéntek|húsvét péntek':'évnapja,húsvét-2',
    'húsvétszombat|húsvét szombat':'évnapja,húsvét-1',
    'húsvétvasárnap|húsvét vasárnap':'évnapja,húsvét',
    'húsvéthétfő|húsvét hétfő':'évnapja,húsvét+1',
    'pünkösd':'évnapja,pünkösd_',
    'pünkösdvasárnap|pünkösd vasárnap':'évnapja,pünkösd',
    'pünkösdhétfő|pünkösd hétfő':'évnapja,pünkösd+1',
    'halottak nap':'évnapja,1102',
    'mindenszentek|mindenszentek nap':'évnapja,1101',
    'államalapítás nap|államalapítás ünnep|alkotmány nap': 'évnapja,0820',
    'március idus':'évnapja,0315',

    'rendszerváltás':'egyedi,1990',         # írásjelek és szám-szavak nem szerepelhetnek a mintákban (korlázott az egyedi mintázatok felvételi lehetősége)



    'a.|az.|és.|ezt.|azt.|i.|ai.|ei.|án.|én.|jén.|jei.|ji.|as.|es.|számít|számol|tartó|terjedő':'stopword'    
                # számít: "péntektől számítva két nap",  tartó: "decemberig tartó 3 hónap"
    }


