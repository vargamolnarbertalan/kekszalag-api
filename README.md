
# Kékszalag API parser by Varga-Molnár Bertalan

## Futtatás
A legújabb release letöltése és a *.zip* kicsomagolása. Ezután futtatni kell a `kekszalagApi.exe` alkalmazást. A lekérdezés eredménye a `kekszalag_data.json` fájlban lesz. Ezt kell excelben vagy vMixben, esetleg más feliratozó szoftverben megnyitni.

## Konfigurálás
A `config.json` fájlban lehet beállítani, hogy a következő lekérdezés mit tartalmazzon.
- url1: Fő Kékszalag API végpont teljes útvonala
- url2: Vihar API kiegészítő a bow numberhez teljes útvonala
- sleep: egész szám, másodpercben az az intervallum amilyen gyakran a lekérdezés megtörténjen
- payload: a HTTP POST metódus body-ja az url1 lekérdezéséhez (ezen belül az API saját kulcsait kell megadni pl limit vagy search)

## Mentés
A konfigurációs fájl elmentésekor az új beállítások azonnal, **futási időben** életbe lépnek és a **program újraindítása nélkül** a következő lekérdezés már a friss adatokkal fog történni.

### Megjegyzés
- Ha a `config.json` fájl hibás vagy nem található, akkor az alapértelmezett vagy az utolsó beállított lekérdezéssel fut tovább a program.
- A program nem formáz, csak az API lekérdezést végzi.

### Mellékelt példa xlsm fájl
A tömörített csomagban található *.xlsm* fájl használható előre az API lekérdezésekor szűrt adatokkal natívan vagy akár az összes rekord lekérdezése után az Excelben lehet tovább szűrni és formázni az adatokat. A gtzipek data fieldjeinek key megnevezése egyezzen az *.xlsm* munkafüzet *transp* lapján található kifejezésekkel.

## Licenc
Ez a szoftver nem nyílt forráskódú. A szoftver használata, terjesztése vagy módosítása kizárólag a készítő előzetes írásos engedélyével és díjfizetés ellenében engedélyezett.
A szoftver használatához licencet kell vásárolni.
Licenceléssel kapcsolatos kérdések esetén kérjük, lépjen kapcsolatba az alábbi e-mail címen: [vargamolnarb@gmail.com].
A jogosulatlan használat szigorúan tilos, és jogi következményeket vonhat maga után.