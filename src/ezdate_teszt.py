''' hundate tesztelése
Példaszövegek megjelenítése a példákból kivonatolt dátumokkal.
Ha a hun-date-parser is telepítve van, akkor összehasonlítási lehetőség.
Kimenet:  console ablak
Részletes leírás:  https://github.com/COREtxt/hundate-core
'''

import sys
from datetime import date, datetime, timedelta

print('HUNDATE TESZT')


# Előfeltétel:  "pip install hundate"
try:
    from hundate.ezdate import fn_printteszt, text2date
except:
    # Installálás nélküli telepítési modell (a három fájl másolása egy tetszőleges mappába, majd a jelen fáj futtatása fájlkezelőből)
    try:
        from ezdate import fn_printteszt, text2date
    except:
        print('Nem sikerült elinditani a teszt programot.\n\n' +

              'Két telepítési koreográfia alkalmazható:\n' +
              'A változat: "pip install hundate" egy cmb-alakban, majd a jelen fájl futtatása közvetlenül a fájlkezelőből vagy python környezetből\n' +
              'B változat: a három py fájl másolása egy tetszőleges mappába, majd a jelen fájl indítása fájlekezelőből (pl. kettős klikk)\n\n' +

              'A python előzetes telepítése mindkét esetben szükséges (3.7 vagy későbbi)\n'
              'Az "A" változat előnye, hogy a további szükséges python modulok telepítése vagy verzióváltása ' +
              'is automatikusan megtörténik (numpy, python-dateutil).')


# Összehasonlítási lehetőség a https://github.com/szegedai/hun-date-parser oldalról letölthető szoftverrel
# - előfeltétel:   "pip install hun_date_parser"
# - ha nincs telepítve, akkor a tesztelés csak a hundate kimeneti értékeit mutatja a felsorolt példákra
bSzegedAI = True
try:
    from hun_date_parser import text2datetime
except:
    bSzegedAI = False
bSzegedAI = False



# teszteset = 'múlt szilveszter előtt egy héttel'
# out = text2date(teszteset, outtype='all+')
# print(teszteset + '\n' + str(out))
# # exit()



fn_printteszt('ISSUE', [
    'február 5. utáni első hétköznap',
    'február 5 utáni első hétköznap',
    'jövő héten kedd-szerda',
    'halottak napja utáni szombat',
    'jövő héten kedd vagy szerda',
    'két héttel ezelőtt',
    'múlt szilveszter után egy héttel'
], bSzegedAI)



# Tesztesetek, kategóriánként csoportosítva
fn_printteszt('ELEMI DÁTUMKIFEJEZÉSEK', [
    'most, ma, mai napon, mai napig',   # ragozott alakok is jók
    'holnap, holnapután, holnap után',  # külön írt változat is jó
    'tegnap, tegnapelőtt, tegnap előtt, Tegnapelött', # ékezet eltérés nem okoz problémát
    'tegnapelöött', # az elgépeléseket jelenleg nem kezeli (nem fuzzy jellegű a keresés; a mintát az elírás miatt "tegnap..."-nak értelmezi)            
    '2022.01.02, 2022-01-03, 20220104, 2022 01 02',
    '0105, 02 03',
    '2022. január 10, 2022. II.hó 3.',
    'a 2000. év II. hónapjának 20. napján',
    'MMXXI. II. hónap 12-e',    # arab, római és szövegesen kiírt számokat / sorszámokat is felismer
    '12-én',                    # aktuális hónapban
    'február 4-én',             # aktuális évben
    'másodikán',                # aktuális hónapban (ha nincs előtte konkrét év vagy hónap információ)
    'március elsején',
    'február huszonnyolcadikán',
    'február harmincegyedikén',           # nincs ilyen nap, "február"-ként értelmezi
    'Az ünnepséget február végén tartják meg.'   # a dátum-kifejezésnek nem kell a szöveg elején állnia ("február végén")
], bSzegedAI)


fn_printteszt('HÉT NAPJAI, ÜNNEPNAPOK', [
    'hétfőn',                     # ezen a héten
    'pénteken',
    'hétvégén',
    'múlt kedden',
    'jövő hét szombaton',
    # ha nincs információ az évről, akkor az idei évben (pontosabban a dt0 argumentum évben)
    'karácsonykor',
    'szenteste',
    'szilveszter napján',
    'újévkor',
    'mindenszentek',
    'húsvét',                     # négy napos
    'húsvét péntek',
    'pünkösd',                    # két napos
    'pünkösd hétfő'
], bSzegedAI)


fn_printteszt('IDŐSZAKOK', [
    '2015-ben',
    'februárban',                     # idén
    'III',                            # idén
    '2015 január',
    'első félév',                     # idén
    'második negyedév',
    '2020 utolsó negyedéve',
    'tavasszal',
    '2020 nyarán',
    'XIX. században',
    "'90-es években",                # 1990-es évek  (50 felet a XX. században, felette a XXI-ben)
    '2010-es években',
    '1900-as években',
    'az ezredfordulón',               # 2000.01.01
    'az előző századfordulón',        # 1900.01.01
    'a századelőn',                   # 2000.01.01
    'március idusán',
    'a rendszerváltáskor'
], bSzegedAI)


fn_printteszt('JELEN MÚLT JÖVŐ', [
    'idén, ebben az évben',
    'jövőre, jövő évben',
    'tavaly, múlt évben, elmúlt évben',
    'múlt héten, jövő héten',
    'következő hétvégén',
    'jövő kedden, előző pénteken',
    'e hónapban, előző hónapban, következő hónapban',
    'múlt félévben',
    'következő negyedévben',
    'két év múlva, három évre rá',
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
    # nem "jövő év nyarán" vagy "jövő nyáron" a jelentése, hanem az időben legközelebb következő (ami még nem kezdődött el)
    'következő nyáron'
], bSzegedAI)


fn_printteszt('ELEJÉN KÖZEPÉN VÉGÉN, SORSZÁMOZOTT IDŐSZAKOK', [
    'a hét közepén',                # középső harmad (időszak)
    'jövő hét harmadik napján',
    'múlt hónap közepén',           # középső harmad
    'a hónap második felében',
    'a hónap utolsó hetében',       # csonka hét is lehet
    'március végén',                # utolsó harmad márciusban (10 nap)
    # utolsó harmad a negyedévben (30 nap)
    'a második negyedév végén',
    'az év utolsó előtti hónapjában',
    'idei év végén',                # utolsó harmad (4 hónap)
    'az év első felében',
    'az év 5. hetében',
    '2025 első felében',
    '2025 harmadik negyedévében',
    '2025 negyedik hónapjában',
    'karácsony második napján',
    'XIX. század harmadik harmadában',
    # utolsó harmad, (kb. 3.3 év)
    'az évtized végén',
    'az előző évtized utolsó negyedében',
    'az évszázad első felében',
    'az évtized utolsó előtti hetében',
    'az évszázad első két évtizede',
    'jövő hét utolsó három napja',
    'a hónap utolsó két hete'
], bSzegedAI)


fn_printteszt('UTÁN ELŐTT', [
    'múlt péntek előtt két héttel',
    'jövő hétvége után két nappal',
    'december 1 előtt 12 nappal',
    'múlt év második negyedéve előtt',          # kezdődátum: 0001.01.01
    'következő nyár után',                      # záródátum: 9999.12.31
    'hétvége utáni második nap',
    # időtartam; a pénteki nap nincs már benne
    'múlt hét péntek előtti 2 hét',
    '2022 utáni 3 év',
    'múlt év előtti év'
], bSzegedAI)


fn_printteszt('DÁTUMTÓL DÁTUMIG', [

    # inkluzív, tehát a kezdő és a záró dátum is benne van
    '2015-2018',
    '2015 és 2022 között',
    '2022 előtt',                                   # 0001.01.01 a kezdődátum
    '2021 január 2-től 2024 április 3-ig',
    '2021.02.05 - 2021.04.03',
    '2010 VII-IX',
    '2021.02.05-10',
    # inkluzív (május 31-ig)
    'februártól májusig',
    'tavalyelőtt február 5 és 10 között',
    '2021 januártól 2024 áprilisig',
    '2021 januártól áprilisig',
    # hiányzó évszám esetén a kifejezésben korábban előforduló évszám
    '2021 második hónaptól a hatodik hónapig',
    '2021 tavasztól 2022 őszig',
    '2021 tavasztól őszig',
    '2021 második negyedévtől a harmadik negyedévig',
    'december első hetétől a harmadikig',
    'hétfőtől péntekig',
    'a hét második napjától az ötödik napjáig',
    'a hét közepétől a végéig',
    'múlt hét hétfőtől jövő hét péntekig',
    'szerdától a jövő hét végéig',
    'április közepétől augusztus elejéig',
    'múlt év április elejétől a közepéig',
    'húsvét péntektől pünkösd hétfőig',
    # inkluzív (a XX. század is benne van)
    'a XIX. századtól a XX. századig',
    'a nyolcvanas évektől 2000-ig',
    'az ezredfordulótól 2020-ig',
    'hétfőtől 5 napig',
    'péntek utáni második héten',               # naptári hét
    'péntektől számított két héten belül',
    'péntekig három nap',                       # "három nap péntekig" is jó
    'péntektől kezdődő két hét',
    'decemberben lezáruló három hónap',
    'decemberig tartó három hónap',
    'péntek után következő három hónap'

], bSzegedAI)


fn_printteszt('ÖSSZETETT KIFEJEZÉSEK', [
    'ebben az évben a tizenkettedik héten',
    'március második hetében keddtől csütörtökig',
    'március második hetétől két hétig',
    'április első hétfőjétől számított második hét közepéig',
    '2020 tavasz elejétől a következő év nyaráig',
    'következő év szeptember közepén',
    'jövő hónap harmadikán',
    # többszörös beágyazást is értelmez (a példa 4-szeresen beágyazott)
    '2023 második féléve harmadik hetének közepén',
    'három évvel ezelőtt decemberben',
    'két hét múlva pénteken',
    'három hete hétfőn',
    'múlt héten a második napon',
    'két hónappal ezután 5-én',
    'két éve januárban',
    'jövő karácsony utáni második hétvégén',
    'tavaly szilveszter előtti szerdán'
], bSzegedAI)

fn_printteszt('TÖBB DÁTUMOT TARTALMAZÓ MONDATOK', [
    'Tavaly május 10-én indultak útnak és két hét múlva érkeztek meg.',
    'Január 12-én kezdődött, és egy hétre rá érte el a két hónappal korábban mért szintet.',
    '2020 január és február között, majd a következő év május 5-én'
], bSzegedAI)

input('\nBezárás: enter')




# # SEBESSÉG TESZT
# # Eredmény: 1-2 msec / mondat
# from ezhelper import stopperstart,stopper
# teszteset='A projekt február 5-e után az első hétköznapon kezdődik és 10 nappal utána fejeződik be.'
# t=stopperstart()
# for i in range(1000):
#     dates=text2date(teszteset,outtype='tuple')
# stopper(t)
# print(dates)

# exit()
