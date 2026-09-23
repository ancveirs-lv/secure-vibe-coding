# Anti-AI-Slop — Drošības minimums MI atbalstītai programmatūras izstrādei

> Šis ir izlaišanas gatavības un pierādījumu nepilnību instruments, nevis sertifikācija, pentests, atbilstības noteikšana vai drošības garantija.

Anti-AI-Slop ir projekta apzīmējums programmatūras izmaiņu noraidīšanai, ja tās tiek pieņemtas vai izvietotas bez pietiekamas izpratnes, ierobežojumiem vai pierādījumiem. Tas nav apgalvojums, ka MI ģenerēts kods pats par sevi ir nedrošs.

## Atbilžu stāvokļi

- `UNKNOWN` — Nezināms: Pašreizējo stāvokli nevar noteikt ar uzticamu informāciju vai pierādījumiem.
- `CLAIMED` — Apgalvots: Prakse tiek apgalvota, bet nav noturīgu ieviešanas vai testa pierādījumu.
- `IMPLEMENTED` — Ieviests: Prakse ir ieviesta produktā vai darba plūsmā un pastāv novērojami ieviešanas pierādījumi.
- `VERIFIED` — Verificēts: Nesens tiešs tests, pārskats vai reproducējams artefakts pamato apgalvojumu; strukturētā ievadē vajadzīga pierādījuma piezīme.
- `NOT_APPLICABLE` — Nav attiecināms: Kontrole patiešām neattiecas uz šo produktu vai darba plūsmu; to drīkst izmantot tikai tur, kur kontrole to pieļauj, un nepieciešams pamatojums.

## Kontroles

### Atbildība un izpratne

#### O01

Nosaukts cilvēks ir atbildīgs par izlaišanas lēmumu un saglabā atbildību par MI atbalstītām izmaiņām.

**Ieteiktā darbība:** Nosaki cilvēku, kurš atbild par izlaidumu, un fiksē, kurš drīkst apstiprināt vai noraidīt drošībai būtiskas izmaiņas.

**Izlaišanas prasība:** `IMPLEMENTED` · blocking=`true` · N/A=nē

**Pierādījumu piemēri:** izlaiduma atbildīgais CODEOWNERS vai izmaiņu ierakstā

**Avoti:** `nist_ssdf11`, `openssf_ai_instructions`

#### O02

Komanda spēj izskaidrot izvietoto arhitektūru, uzticības robežas, datu plūsmas un ārējos servisus, nepaļaujoties uz MI rīku to rekonstruēšanai.

**Ieteiktā darbība:** Uzturi īsu arhitektūras un datu plūsmas aprakstu ar ieejas punktiem, glabātuvēm, ārējiem servisiem un uzticības robežām.

**Izlaišanas prasība:** `IMPLEMENTED` · blocking=`true` · N/A=nē

**Pierādījumu piemēri:** arhitektūras/datu plūsmas shēma vai ADR

**Avoti:** `nist_ssdf11`

#### O03

Pirms publiskas izlaišanas ir identificēti ticami ļaunprātīgas izmantošanas scenāriji un drošībai būtiski uzticības pieņēmumi.

**Ieteiktā darbība:** Pieraksti svarīgākos uzbrucēja mērķus, uzticības pieņēmumus un atteices režīmus un pārvērt tos pārbaudēs.

**Izlaišanas prasība:** `IMPLEMENTED` · blocking=`false` · N/A=nē

**Pierādījumu piemēri:** draudu/ļaunprātīgas izmantošanas piezīme sasaistīta ar testiem

**Avoti:** `nist_ssdf11`, `owasp_asvs_500`

#### O04

MI atbalstītās izmaiņas tiek pārskatītas kā diff, ietverot negaidītas vai ārpus uzdevuma veiktas izmaiņas.

**Ieteiktā darbība:** Pieprasi visa diff pārskatu un noraidi nesaistītas ģenerētas izmaiņas, nevis pieņem lielu necaurspīdīgu patch.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=nē

**Pierādījumu piemēri:** pārskata ieraksts, kas attiecas uz pilnu diff

**Avoti:** `owasp_secure_coding_ai`, `openssf_ai_instructions`

### Autentifikācija un autorizācija

#### A01

Autentifikācijai tiek izmantoti nostiprināti mehānismi, un drošībai būtiskas identitātes plūsmas netiek improvizētas ar ģenerētu kodu.

**Ieteiktā darbība:** Izmanto uzturētas autentifikācijas bibliotēkas vai platformas mehānismus un pārskati pieteikšanās, atkopšanas un sesiju plūsmas.

**Izlaišanas prasība:** `IMPLEMENTED` · blocking=`true` · N/A=nē

**Pierādījumu piemēri:** autentifikācijas dizaina/konfigurācijas pārskats

**Avoti:** `owasp_asvs_500`, `openssf_ai_instructions`

#### A02

Autorizācija tiek īstenota servera pusē katrai aizsargātai darbībai un objektam, nevis tikai lietotāja saskarnē.

**Ieteiktā darbība:** Pievieno servera puses tiesību pārbaudes resursa/darbības robežā un testē aizliegtos ceļus.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=nē

**Pierādījumu piemēri:** negatīvie autorizācijas testi

**Avoti:** `owasp_asvs_500`

#### A03

Kur attiecināms, lietotāju, tenant un objektu līmeņa izolācija ir pārbaudīta ar negatīviem gadījumiem.

**Ieteiktā darbība:** Pārbaudi, vai viena identitāte nevar nolasīt vai mainīt citas identitātes objektus, mainot identifikatorus, maršrutus vai API izsaukumus.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** IDOR/BOLA/tenant izolācijas testa pierādījumi

**Avoti:** `owasp_asvs_500`

#### A04

Administratīvām, atkopšanas un citām augstas ietekmes funkcijām ir stingrākas piekļuves robežas, un tās netiek aizsargātas ar slēpšanu.

**Ieteiktā darbība:** Uzskaiti privileģētās funkcijas, pieprasi skaidru autorizāciju un atsevišķi pārbaudi atkopšanas un administrēšanas plūsmas.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** privileģēto maršrutu uzskaite un negatīvie testi

**Avoti:** `owasp_asvs_500`

### Dati un noslēpumi

#### D01

Noslēpumi nav iekodēti kodā, commitoti, nosūtīti klientam vai ielīmēti MI promptos/kontekstā; produkcijas piekļuves dati tiek glabāti un ierobežoti atbilstoši.

**Ieteiktā darbība:** Pārvieto noslēpumus piemērotā noslēpumu glabātuvē, rotē atklātos piekļuves datus un pievieno repozitorija/konteksta izņēmumus.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=nē

**Pierādījumu piemēri:** noslēpumu skenējums un secret-store/konfigurācijas pierādījumi

**Avoti:** `owasp_secure_coding_ai`, `openssf_ai_instructions`

#### D02

MI rīki saņem tikai minimāli nepieciešamo projekta kontekstu, un sensitīvi faili, kur iespējams, ir izslēgti no rīka konteksta.

**Ieteiktā darbība:** Konfigurē MI rīka ignore/izņēmumu noteikumus un nepakļauj atslēgas, privātus datus, produkcijas dumpus vai regulētus datus nevajadzīgam kontekstam.

**Izlaišanas prasība:** `IMPLEMENTED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** MI konteksta izņēmumu konfigurācija

**Avoti:** `owasp_secure_coding_ai`

#### D03

Sensitīvi dati tiek minimizēti, aizsargāti pārsūtē un glabāšanā un, kur vajadzīgs, izslēgti vai aizklāti žurnālos.

**Ieteiktā darbība:** Dokumentē sensitīvos datus, noņem nevajadzīgu vākšanu un pārbaudi šifrēšanu, piekļuvi un žurnālu uzvedību.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** datu uzskaite un glabāšanas/žurnālu verifikācija

**Avoti:** `owasp_asvs_500`, `openssf_ai_instructions`

#### D04

Svarīgiem pastāvīgiem datiem ir pārbaudīts atkopšanas ceļš, un destruktīvām darbībām ir definēti aizsardzības mehānismi.

**Ieteiktā darbība:** Pārbaudi svarīgu datu atjaunošanu un definē apstiprināšanu, rollback vai līdzvērtīgus aizsardzības mehānismus destruktīvām darbībām.

**Izlaišanas prasība:** `VERIFIED` · blocking=`false` · N/A=jā

**Pierādījumu piemēri:** atjaunošanas tests vai destruktīvas darbības atkopšanas pierādījumi

**Avoti:** `nist_ssdf11`

### Atkarības un piegādes ķēde

#### S01

Katra MI ieteikta ārējā pakotne pirms instalēšanas ir pārbaudīta paredzētajā reģistrā un pārskatīta.

**Ieteiktā darbība:** Pirms pievienošanas pārbaudi pakotnes nosaukumu, reģistru, uzturētāju/vēsturi un nepieciešamību projektā.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** atkarības pārskata ieraksts vai allowlist ieraksts

**Avoti:** `owasp_secure_coding_ai`

#### S02

Atkarību versijas tiek reproducējami atrisinātas, un pirms izlaišanas tiek veikta zināmu ievainojamību pārbaude.

**Ieteiktā darbība:** Commito lockfile vai līdzvērtīgus atrisināšanas datus un CI palaid ekosistēmai atbilstošu ievainojamību pārbaudi.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** lockfile un atkarību audita rezultāts

**Avoti:** `owasp_secure_coding_ai`, `nist_ssdf11`

#### S03

Atkarības tiek minimizētas, un būtiskām jaunām atkarībām ir fiksēts mērķis, licence un uzturēšanas/izcelsmes pārbaude.

**Ieteiktā darbība:** Noņem nevajadzīgas pakotnes un fiksē, kāpēc būtiskas atkarības ir vajadzīgas un uzticamas.

**Izlaišanas prasība:** `IMPLEMENTED` · blocking=`false` · N/A=jā

**Pierādījumu piemēri:** atkarību uzskaite/pārskata piezīme

**Avoti:** `nist_ssdf11`, `openssf_ai_instructions`

#### S04

CI/CD darbības, būvēšanas spraudņi un automatizācijas atkarības ir piesaistītas kontrolētām versijām vai citādi kontrolētas, un to tiesības ir minimizētas.

**Ieteiktā darbība:** Pārskati pipeline atkarības un tiesības; kur praktiski, piesaisti nemainīgām versijām un ierobežo tokenus.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** CI konfigurācijas un tiesību pārskats

**Avoti:** `nist_ssdf11`, `owasp_secure_coding_ai`

### Ievades un biznesa loģika

#### I01

Neuzticama ievade tiek validēta pēc sagaidāmās formas un garuma, un izvades/vaicājumu kontekstos tiek izmantota droša kodēšana vai parametrizācija.

**Ieteiktā darbība:** Definē ievades kontraktus un izmanto framework drošu renderēšanu, parametrizētus vaicājumus un kontekstam atbilstošu kodēšanu.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** injekciju/validācijas testi

**Avoti:** `owasp_asvs_500`, `openssf_ai_instructions`

#### I02

Augsta riska parseriem un sinkiem, piemēram, URL, failiem, shell komandām un servera puses pieprasījumiem, ir skaidra validācija un izolācija.

**Ieteiktā darbība:** Pārskati failu augšupielādi, SSRF, komandu izpildi un parseru robežas; noņem nedrošus universālus izpildes ceļus.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** SSRF/failu/komandu negatīvie testi

**Avoti:** `owasp_asvs_500`

#### I03

Drošībai un naudai būtiskas biznesa invariantes tiek īstenotas servera pusē un, kur attiecināms, testētas pret atkārtojumu, konkurenci vai identifikatoru viltošanu.

**Ieteiktā darbība:** Ievies kritiskās invariantes servera puses loģikā un pievieno negatīvos, idempotences vai konkurences testus augstas ietekmes stāvokļu pārejām.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** biznesa loģikas negatīvie testi

**Avoti:** `owasp_asvs_500`

#### I04

Ārēji sasniedzamām darbībām ir atbilstoši resursu limiti, pieprasījumu ierobežojumi, timeout un droša atteices uzvedība.

**Ieteiktā darbība:** Nosaki ierobežotus pieprasījumu/body/job limitus, rate control un timeout ļaunprātīgi izmantojamām vai dārgām darbībām.

**Izlaišanas prasība:** `IMPLEMENTED` · blocking=`false` · N/A=jā

**Pierādījumu piemēri:** izpildvides limitu konfigurācija

**Avoti:** `owasp_asvs_500`

### MI aģenti, MCP un rīku piekļuve

#### G01

MI kodēšanas aģenti darbojas ar minimāli nepieciešamajām failu sistēmas, shell, tīkla, mākoņa un repozitorija tiesībām.

**Ieteiktā darbība:** Atdali izstrādes un produkcijas piekļuves datus un sandboxo vai ierobežo aģenta piekļuvi konkrētajam uzdevumam.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** aģenta tiesību/sandbox konfigurācija

**Avoti:** `owasp_secure_coding_ai`, `owasp_agentic_top10_2026`

#### G02

Destruktīvām, piekļuves datu sensitīvām un drošības robežu izmaiņām vajadzīgs apzināts cilvēka apstiprinājums, nevis vispārējs auto-accept.

**Ieteiktā darbība:** Atslēdz neierobežotu automātisku apstiprināšanu un definē darbības, kurām vienmēr vajadzīgs cilvēka apstiprinājums.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** aģenta apstiprināšanas politikas konfigurācija

**Avoti:** `owasp_secure_coding_ai`, `owasp_agentic_top10_2026`

#### G03

MCP serveri un citi pieslēgtie rīki ir skaidri uzticēti, ar minimālām tiesībām un ierobežotiem piekļuves datiem.

**Ieteiktā darbība:** Uzturi rīku allowlist, pārskati katra rīka iespējas un ierobežo piekļuves datus un tīkla sasniedzamību.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** MCP/rīku uzskaite un tiesību pārskats

**Avoti:** `owasp_secure_coding_ai`, `owasp_agentic_top10_2026`

#### G04

Issues, pull requesti, repozitorija faili, žurnāli un ielādēts tīmekļa saturs tiek uzskatīts par neuzticamām instrukcijām, ja to patērē MI aģents.

**Ieteiktā darbība:** Pirms aģenta izmantošanas pārskati neuzticamo kontekstu, ierobežo kontekstu/izejošo tīklu un pārbaudi rezultējošās izmaiņas pret netiešas prompt injection sekām.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** aģenta konteksta pārskats vai ierobežota konteksta pierādījumi

**Avoti:** `owasp_secure_coding_ai`, `owasp_agentic_top10_2026`

### Izvietošana un izpildvide

#### P01

Produkcijas konfigurācija ir nostiprināta: debug/test funkcijas un noklusējuma piekļuves dati ir atslēgti vai noņemti.

**Ieteiktā darbība:** Izveido atkārtojamu produkcijas hardening checklist un pārbaudi faktisko izpildvides konfigurāciju.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** faktiskās produkcijas konfigurācijas pārbaude

**Avoti:** `owasp_asvs_500`

#### P02

Ārējā ekspozīcija ir apzināta: TLS, cookies, CORS, drošības galvenes, origins un publiskie endpointi ir konfigurēti produkta vajadzībām.

**Ieteiktā darbība:** Uzskaiti internetā sasniedzamos endpointus un pārbaudi transporta, pārlūka un drošības robežu iestatījumus, nevis pieņem ģenerētus noklusējumus.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** ārējo endpointu un drošības galveņu/konfigurācijas verifikācija

**Avoti:** `owasp_asvs_500`

#### P03

Datubāzes, objektu glabātuves, rindas un administratīvie servisi nav publiski eksponēti, ja vien tas nav skaidri vajadzīgs un aizsargāts.

**Ieteiktā darbība:** Pārbaudi tīkla ekspozīciju, mākoņa IAM un servisu piekļuves datus izvietotajā vidē.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=jā

**Pierādījumu piemēri:** izvietotās vides tīkla/IAM ekspozīcijas pierādījumi

**Avoti:** `owasp_asvs_500`, `nist_ssdf11`

#### P04

Būtiskām kļūmēm pēc izlaišanas pastāv operacionāla žurnālošana, brīdinājumi, rollback un incidenta atbildība.

**Ieteiktā darbība:** Definē, kas tiks monitorēts, kurš saņem brīdinājumus, kā tiek atsaukts slikts izlaidums un kurš pieņem incidenta lēmumus.

**Izlaišanas prasība:** `VERIFIED` · blocking=`false` · N/A=nē

**Pierādījumu piemēri:** monitoringa/brīdinājumu/rollback runbook vai tests

**Avoti:** `nist_ssdf11`, `owasp_asvs_500`

### Izlaišanas pierādījumi

#### R01

Drošībai kritiskiem ceļiem ir automatizēti pozitīvie un negatīvie testi, ietverot aizlieguma gadījumus, nevis tikai happy path.

**Ieteiktā darbība:** Pievieno testus, kas pierāda, ka neautorizētas, nepareizas un nedrošas darbības tiek noraidītas kā paredzēts.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=nē

**Pierādījumu piemēri:** CI testa izpilde ar nosauktiem negatīvajiem drošības testiem

**Avoti:** `openssf_ai_instructions`, `owasp_asvs_500`

#### R02

Drošībai sensitīvas MI ģenerētas izmaiņas saņem pārskatu, kas ir neatkarīgs no tā paša ģenerēšanas soļa.

**Ieteiktā darbība:** Izmanto cilvēka pārskatītāju un/vai deterministiskus drošības rīkus; neuzskati ģenerējošā modeļa pašpārbaudi par vienīgo assurance.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=nē

**Pierādījumu piemēri:** cilvēka pārskats un rīku rezultāti

**Avoti:** `openssf_ai_instructions`, `nist_ssdf11`

#### R03

Pirms izlaišanas tiek palaistas noslēpumu, atkarību un koda/konfigurācijas drošības pārbaudes, un izņēmumiem ir īpašnieks un pamatojums.

**Ieteiktā darbība:** CI palaid atbilstošas automatizētas pārbaudes un fiksē, kāpēc drošības atradums tiek apspiests vai pieņemts.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=nē

**Pierādījumu piemēri:** CI drošības pārbaužu rezultāti un izņēmumu ieraksts

**Avoti:** `nist_ssdf11`, `openssf_ai_instructions`

#### R04

Izlaidumu var sasaistīt ar commit, būvējuma/konfigurācijas stāvokli, atkarību kopu, zināmajām nepilnībām un reproducējamu gate rezultātu.

**Ieteiktā darbība:** Izveido nelielu izlaišanas pierādījumu pakotni, lai vēlāk var rekonstruēt, kas tika izlaists un kāpēc gate tika iziets.

**Izlaišanas prasība:** `VERIFIED` · blocking=`true` · N/A=nē

**Pierādījumu piemēri:** izlaiduma manifests ar commit/būvējuma/gate pierādījumiem

**Avoti:** `nist_ssdf11`


## Anti-AI-Slop indikatori

- `SLOP01` — MI apstiprinājums tiek uzskatīts par pierādījumu, ka kods ir drošs.
- `SLOP02` — Neviens nevar izskaidrot autentifikācijas vai autorizācijas plūsmu, vēlreiz nejautājot MI.
- `SLOP03` — Testi sedz ģenerētos happy path, bet ne aizliegtus vai ļaunprātīgus gadījumus.
- `SLOP04` — Pakotne tika instalēta tāpēc, ka MI to nosauca, nepārbaudot reģistru vai uzturētāju.
- `SLOP05` — Drošības brīdinājums tika noņemts, atslēdzot pārbaudi, nevis novēršot problēmu vai skaidri pieņemot risku.
- `SLOP06` — Klienta puses slēpšana vai maršruta noslēpums tiek izmantots kā autorizācija.
- `SLOP07` — Produkcijas noslēpumi vai dumpi ir pieejami kodēšanas aģenta kontekstam.
- `SLOP08` — Kodēšanas aģentam ikdienas uzdevumiem ir vispārējas shell, tīkla, mākoņa vai produkcijas tiesības.
- `SLOP09` — Neuzticams issue, PR, žurnāla vai tīmekļa saturs tiek tieši dots aģentam, kas var rīkoties repozitorijā.
- `SLOP10` — CORS, glabātuves, datubāzes vai tīkla ekspozīcija tika paplašināta, līdz aplikācija sāka darboties.
- `SLOP11` — Liels MI ģenerēts diff tiek mergeots, nesaprotot nesaistītās izmaiņas.
- `SLOP12` — Tas pats MI ģenerēšanas cikls ir vienīgais drošībai kritiskā koda pārskatītājs un testu autors.
- `SLOP13` — Neviens nezina, kura versija/konfigurācija faktiski tika izvietota.
- `SLOP14` — Nav pārbaudīta rollback vai atkopšanas ceļa sliktam izlaidumam vai destruktīvai datu izmaiņai.
- `SLOP15` — Drošības atradumi tiek apspiesti bez nosaukta īpašnieka un pamatojuma.
- `SLOP16` — Produkts ir publisks, lai gan kritiskas kontroles paliek UNKNOWN vai tikai CLAIMED.
