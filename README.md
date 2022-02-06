# hundate-core
NLP modul for hungarian date-entity recognition and translation to specific date values\
NLP modul, magyar nyelvű dátum-kifejezések felismerése és lefordítása konkrét dátum-értékekre

## Telepítés
pip install hundate

Előfeltétel:  Python 3.7 vagy későbbi

Az ezdate_teszt.py fájl "pip install" nélkül is futtatható (github fájlok letöltése egy mappába, majd az ezdate_teszt.py indítása fájlkezelővel).
Ebben az esetben azonban előfordulhat, hogy egyedi módon kell telepíteni további python modulokat (numpy, python-dateutil)

## Importálás
- from hundate import ezdate\
   Hivatkozás: ezdate.text2date()
- from hundate import ezdate as d\
   Hivatkozás: d.text2date()
- from hundate.ezdate import text2date\
   Hivatkozás: text2date()

## Felhasználási terület
- NLP alkalmazások, dátumok kivonatolása, természetes nyelvi szófordulatok értelmezése
- chatbot alkalmazások

## Képességek
- relációs dátum-kifejezések értelmezése
- kontextuális időmeghatározások
- összetett, és akár többszörösen beágyazott dátum-kifejezéseket is képes kezelni
- kezeli a szövegesen megadott számokat, a római számokat, a sorszámokat, a ragokat és a dátumokkal kapcsolatos szinonim szófordulatokat is
- az egyedi dátumokon túlmenően dátum-tartományokat is fel tud ismerni
- érzéketlen a kisbetű-nagybetű, hosszú-rövid ékezet, szóköz, írásjel, ragozás és stopword eltérésekre

**Mit nem tud kezelni**:
- csak dátumbeazonosítás, napon belüli időszakokat és óra-perc időmeghatározásokat nem kezel
- korlátozott méretű (legfeljebb pár mondat terjedelmű) input kezelésére van optimalizálva

**Továbbfejlesztési lehetőségek**:
- a dátumszavak beazonosításakor engedjen meg kismértékű elgépeléseket is (fuzzy search)
- a return-ben adja vissza a beazonosított dátum-kifejezések határ-pozícióit is (ebben az esetben teljes értékű annotációs algoritmusként is alkalmazható)

**Összehasonlítás más szoftverekkel**\
A jelen szoftver fejlesztésének megkezdése előtt egyetlen olyan publikus szoftvert sikerült felkutatni, amely képes a magyar dátumkifejezések viszonylag átfogó beazonosítására és értelmezésére:  "**hun-date-parser**", a "szegedai" fejlesztői git-hub oldalon.
Ugyanehhez a fejlesztői közösséghez tartoznak - részben vagy egészében - a Hungarian NER és a HuSapcy szoftverek, tehát a magyar nyelvű NLP alapkutatásban járatos fejlesztőkről van szó.\
Azért tartottuk szükségesnek egy új, magyar nyelvű dátum-interpretáló szoftver létrehozását, mert a hun-date-parser szoftver (feltehetően) egy viszonylag szorosan lehatárolt fejlesztési scope kiszolgálására jött létre. Ennek megfelelően a magyar nyelvű dátum-kifejezéseknek csak egy relative szűk körét képes kezelni. Az általunk előzetesen felállított példatárnak hozzávetőleg 20 százalékára adott megfelelő megoldást (lásd "ezdate_teszt.py" - ha a hun_date_parser modul is telepítve van, akkor összehasonlítja a két szoftver által ugyanarra a példatárra adott válaszokat).\
Másrészről azonban van olyan részterület is, amiben a "hun-date-parser" többet tud annál, mint amire nekünk szükségünk volt: a hun-date-parser jó teljesítményt nyújt a napon belüli napszak- és óra-perc kifejezések értelmezésében. Mi ehelyett azt a fejlesztési stratégiát követtük, ami a dátum- illetve a napon belüli időpont-beazonosítás szétválasztásából indul ki. Az általunk fejlesztett szoftver vállaltan megáll a nap-szintű időpont-meghatározások részletezési szintjén, de ebben a körben a lehető legszélesebb példatárra igyekszik támaszkodni. Ha ezen túlmenően a napon belüli időpont-meghatározások is relevánsak, akkor egy erre szakosodott másik szoftver párhuzamos használatát láttuk a legjobb megoldásnak (pl. a hun-date-parser szoftverét).

Említést érdemel még a **Duckling** dátum extraktora. Maga a Duckling jelenleg nem sorolja fel a támogatott nyelvek között a magyar nyelvet, mindamellett a wit.ai - ami szoros kapcsolatban áll a Duckling-gal - képes felismerni és konkrét dátumra lefordítani néhány magyar nyelvű dátum-kifejezést (pl. "2021. március 2", "holnapután", "hétfőn", "pénteken", "jövő kedden";  https://wit.ai/, "MyApps" menüpont). Ez azonban csak elenyésző része annak a példatárnak, amire egy komolyan vehető magyar nyelvű dátum-interpretáló alkalmazásnak ki kell terjednie. 

## Röviden az algoritmusról
Ha-akkor elágazásokat tartalmazó "hard" programozási módszertan, amely véges sok (hozzávetőleg 50) generalizált mintázatra és azok rekurzív alkalmazására támaszkodik.
A mintázat-keresés első lépése a szám-szavak illetve egy lookup táblázatban megadott időhatározó és relációs szavak (vagy többszavas kifejezések) annotálása. 
A mintázatok beazonosítása a csökkenő méretű mozgóablakos pásztázás módszerével történik (a mozógablak mérete a szavak számára utal), és minden sikeres rész-beazonosítást követően újrakezdődik.
Az NLP terén a legjobb eredményt a neurális hálózat alapú "soft" algoritmusok és a klasszikus "hard" algoritmusok együttes alkalmazásával lehet elérni (az utóbbira példa a jelen szoftver).

## Példák
- 'múlt hét keddtől a jövő hét végéig'
- 'két év múlva októberben'
- 'két hónappal ezelőtt, 5-én'
- 'március második hetében hétköznapokon'
- 'jövő karácsony utáni második hétvégén'
- '2023 második féléve harmadik hetének elején'
- 'múlt hét péntek előtti három napon'
- 'a múlt század közepén',   'a 70-es évek elején'
- 'Tavaly május 10-én indultak útnak és két hét múlva érkeztek meg.'

  További példák az ezdate_teszt.py fájlban (200 körüli példamondat).


## A modulhoz tartozó függvények
- **text2date()**:   ("Text to date") Magyar nyelvű időmeghatározások lefordítása dátumra vagy dátum tartományra


## Függvények részletezése

**text2date**( text, dt0=None, context='', outtype='all' ):
- **text**:  általában több szavas kifejezés vagy mondat
        A mondatban időhatározókon és számokon kívüli szavak is lehetnek (a dátum bárhol lehet a szövegen belül).
- **dt0**:  relációs dátummeghatározások esetén a kiinduló dátum.
        Ha nincs megadva, akkor a mai nap.
- **tense**: 'future' / 'past'.  A nem egyértelmű időmeghatározások esetén jövőbeli vagy múltbeli dátumot preferáljon a függvény
- **outtype**:
    - '**all**':  a szövegben előforduló összes dátum-kifejezés lefordított értékének vesszős felsorolása, az előfordulás sorrendjében\
              Példa:   '2022.05.12, 2021.12.10-2021.12.20'     (a felsorolásban egyedi dátumok vagy dátumtartományok fordulhatnak elő)
    - '**all+**':  részletező információt is visszaad a beazonosítás folyamatáról  (a beazonosítás ellenőrzésére illetve tesztelésére használható)
    - '**first**':   csak az első előforduló dátumot vagy dátumtartományt adja vissza   (pl. "2022.05.12" )  
    - '**tuple**':   ugyanaz mint az "all", de (datetime1,datetime2) formátumban adja vissza a bazonosított dátum-kifejezéseket (datetime2=None, ha a részkifejezés egyetlen dátumból áll)
