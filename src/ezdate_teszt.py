import sys
from datetime import datetime,date,timedelta

# Előfeltétel:  "pip install ezdate"
from ezdate import text2date
import ezdate as d

# Összehasonlítási lehetőség a https://github.com/szegedai/hun-date-parser oldalról letölthető szoftverrel
# - előfeltétel:   "pip install hun_date_parser"
# - ha nincs telepítve, akkor csak a tesztelés csak az ezdate kimeneti értékeit mutatja a felsorolt példákra 
bSzegedAI=True     
try:
    from hun_date_parser import text2datetime
except:
    bSzegedAI=False

bSzegedAI=False



#teszteset='rendszerváltás évében'
#print(teszteset + '\n' +
#      text2date(teszteset,outtype='first+'))


def fn_print(címsor,tesztesetek,bSzegedAI):
    print('\n\n' + címsor + '\n')
    for teszt in tesztesetek:
        try:
            coredate=text2date(teszt)
        except:
            coredate='(exception)'

        if bSzegedAI:
            try:
                hundate=''
                listL=text2datetime(teszt)
                if len(listL)>0:
                    dictL=listL[0]
                    date1=dictL['start_date']
                    hundate=date1.strftime('%Y.%m.%d')
                    date2=dictL['end_date']
                    s2=date2.strftime('%Y.%m.%d')
                    if s2>hundate: hundate=hundate + '-' + s2
            except:
                hundate='(exception)'
            print('"' + teszt + '"\n' +
                  '\t\t\t\t core:      ' + coredate + '\n' +
                  '\t\t\t\t szeged:    ' + hundate)
    
        else:
            teszt='"' + teszt + '"'
            if len(teszt)<30: teszt = teszt + ' '*(30-len(teszt))
            print(teszt + '\t' +  coredate)



fn_print('ELEMI DÁTUMKIFEJEZÉSEK',[
          'most',
          'mai napon',                 # ragozott alakok is jók  (pl. "mai napra", "mai napig", ...)
          'tegnap',
          'tegnapelőtt',
          'tegnap előtt',              # külön írt változat is jó
          'Tegnapelött',               # a kisbetű-nagybetű és a rövid-hosszú ékezet vagy a szóközök és irásejelek eltérése nem jelent problémát
          'tegnapellőtt',              # az elgépeléseket jelenleg nem kezeli (nem fuzzy jellegű a keresés; a mintát az elírás miatt "tegnap..."-nak értelmezi) 
          'holnap',
          'holnapután',
          'holnap után',
          '2022.01.02',
          '2022-01-03',
          '20220104','2022 01 02','0105','02 03','2022. január 10','2022. II.hó 3.',
          'MMXXI. II. hónap 12-e',              # arab, római és szövegesen kiírt számokat / sorszámokat is felismer
          'február 4-én',
          'másodikán',                          # aktuális hónapban
          'március elsején',
          'február huszonnyolcadikán',
          'február harmincegyedikén',           # nincs ilyen nap, "február"-ként értelmezi 
          'Az ünnepséget február végén tartják meg.'        # a dátum-kifejezésnek nem kell a szöveg elején állnia ("február végén")
          ],bSzegedAI)


fn_print('HÉT NAPJAI, ÜNNEPNAPOK',[
          'hétfőn',                     # ezen a héten
          'pénteken',
          'hétvégén',
          'múlt kedden',
          'jövő hét szombaton',
          'karácsonykor',               # ha nincs információ az évről, akkor az idei évben (pontosabban a dt0 argumentum évben)
          'szenteste',
          'szilveszter napján',         
          'újévkor',
          'mindenszentek',
          'húsvét',                     # négy napos
          'húsvét péntek',
          'pünkösd',                    # két napos
          'pünkösd hétfő'
          ],bSzegedAI)




fn_print('IDŐSZAKOK',[
          '2015-ben',
          'februárban',                     # idén
          '2015 január',
          'első félév',                     # idén
          'második negyedév',
          '2020 utolsó negyedéve',
          'tavasszal',                      
          '2020 nyarán',
          'XIX. században',
          "'90-es években",                 # 1990-es évek  (50-től az előző század)
          '2010-es években',
          '1900-as években',
          'az ezredfordulón',               # 2000.01.01
          'az előző századfordulón',        # 1900.01.01
          'a századelőn',                   # 2000.01.01
          'március idusán',
          'a rendszerváltáskor'
          ],bSzegedAI)



fn_print('JELEN MÚLT JÖVŐ',[
            'idén',
            'ebben az évben',
            'jövőre',
            'jövő évben',
            'tavaly',
            'múlt évben',
            'elmúlt évben',
            'múlt héten',
            'jövő héten',
            'következő hétvégén',
            'jövő kedden',
            'előző pénteken',
            'e hónapban',
            'előző hónapban',
            'következő hónapban',
            'múlt félévben',
            'következő negyedévben',
            'két év múlva',
            'három évre rá',
            '4 hónappal ezelőtt',
            'két nappal ezelőtt',
            '10 hét múlva',
            '3 éve',
            'öt napja',
            'tavaly január 10-én',
            'tavaly februárban',
            'jövő nyáron',
            'jövő május 12-én',
            'jövő év tavaszán',
            'következő nyáron'          # nem "jövő év nyarán" vagy "jövő nyáron" a jelentése, hanem az időben legközelebb következő (ami még nem kezdődött el)
            ],bSzegedAI)




fn_print('ELEJÉN KÖZEPÉN VÉGÉN, SORSZÁMOZOTT IDŐSZAKOK',[
            'a hét közepén',                # középső harmad (időszak)
            'jövő hét harmadik napján',   
            'múlt hónap közepén',           # középső harmad
            'a hónap második felében',
            'a hónap utolsó hetében',       # csonka hét is lehet
            'március végén',                # utolsó harmad márciusban (10 nap)
            'a második negyedév végén',     # utolsó harmad a negyedévben (30 nap)
            'az év utolsó hónapjában',      # december
            'idei év végén',                # utolsó harmad (4 hónap)
            'az év első felében',
            'az év 5. hetében',
            '2025 első felében',
            '2025 harmadik negyedévében',
            '2025 negyedik hónapjában',
            'karácsony második napján',             
            'XIX. század harmadik harmadában',
            'az évtized végén',                     # utolsó harmad, (kb. 3.3 év)
            'az előző évtized utolsó negyedében',
            'az évszázad első felében'
            ],bSzegedAI)



fn_print('UTÁN ELŐTT',[
            'múlt péntek előtt két héttel',             
            'jövő hétvége után két nappal',
            'december 1 előtt 12 nappal',
            'múlt év második negyedéve előtt',          # kezdődátum: 0001.01.01
            'következő nyár után',                      # záródátum: 9999.12.31
            'hétvége utáni második nap',            
            'múlt hét péntek előtti 2 hét',             # időstartam; a pénteki nap nincs már benne
            '2022 utáni 3 év',
            'múlt év előtti év'
            ],bSzegedAI)




fn_print('DÁTUMTÓL DÁTUMIG',[
            
            '2015-2018','2015 és 2022 között',              # inkluzív, tehát a kezdő és a záró dátum is benne van
            '2022 előtt',                                   # 0001.01.01 a kezdődátum
            '2021 január 2-től 2024 április 3-ig',
            '2021.02.05 - 2021.04.03',
            '2021.02.05-10',
            'februártól májusig',                           # inkluzv (május 31-ig)
            'tavalyelőtt február 5 és 10 között',
            '2021 januártól 2024 áprilisig',
            '2021 januártól áprilisig',
            '2021 második hónaptól a hatodik hónapig',      # hiányzó évszám esetén a kifejezésben korábban előforduló évszám
            '2021 tavasztól 2022 őszig',
            '2021 tavasztól őszig',
            '2021 második negyedévtől a harmadik negyedévig',
            'hétfőtől péntekig',
            'múlt hét hétfőtől jövő hét péntekig',
            'szerdától a jövő hét végéig',
            'április közepétől augusztus elejéig',
            'múlt év április elejétől a közepéig',
            'a hét közepétől a végéig',
            'húsvét péntektől pünkösd hétfőig',
            'a XIX. századtól a XX. századig',          # inkluzív (a XX. század is benne van)
            'a nyolcvanas évektől 2000-ig',
            'az ezredfordulótól 2020-ig'
            ],bSzegedAI)


fn_print('ÖSSZETETT KIFEJEZÉSEK',[
            'ebben az évben a tizenkettedik héten',
            'következő tavasz elején',
            'következő év szeptember közepén',
            'jövő hónap harmadikán',
            '2023 második féléve harmadik hetének közepén',         # többszörös beágyazást is értelmez (a példa 4-szeresen beágyazott)
            'három évvel ezelőtt decemberben',
            'két hét múlva pénteken',
            'három hete hétfőn',
            'múlt héten a második napon',
            'két hónappal ezután 5-én',
            'két éve januárban',
            'jövő karácsony utáni második hétvégén',
            'tavaly szilveszter előtti szerdán'
            ],bSzegedAI)



input('\nBezárás: enter')








