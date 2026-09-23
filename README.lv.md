# Anti-AI-Slop — Drošības minimums MI atbalstītai programmatūras izstrādei

**Latviski** · [English](README.md)

**32 kontroļu divvalodu release gate ar MI palīdzību veidotai programmatūrai · globāls EN pamats · LV lokalizācija**

> MI panāca, ka tas strādā. Kādi pierādījumi rāda, ka to drīkst laist publiski?

Repozitorijs paredzēts izstrādātājiem, dibinātājiem un mazām komandām, kas programmatūras izstrādē intensīvi izmanto MI koda asistentus vai kodēšanas aģentus — tostarp pieeju, ko starptautiski bieži sauc par `vibe coding`.

**Anti-AI-Slop** ir projekta apzīmējums programmatūras izmaiņu noraidīšanai, ja tās tiek pieņemtas vai izvietotas bez pietiekamas izpratnes, ierobežojumiem vai pierādījumiem. Tas **nav** apgalvojums, ka MI ģenerēts kods pats par sevi ir nedrošs.

## Izlaišanas modelis

`MI atbalstīta izmaiņa → izpratne → ierobežojumi → ieviešana → verifikācija → pierādījumi → izlaišanas lēmums`

Rīks apzināti neveido **kopēju drošības punktu skaitu**.

Iespējamie gate rezultāti:

- `BLOCKED` — vismaz viena izlaišanu bloķējoša kontrole nesasniedz prasīto pierādījumu stāvokli;
- `CONDITIONAL` — bloķējošās kontroles ir izpildītas, bet palikušas nebloķējošas nepilnības;
- `READY` — visas attiecināmās kontroles sasniedz prasīto pierādījumu stāvokli.

Rīks pārbauda pierādījuma piezīmes esamību, bet **neapstiprina pašu pierādījumu**; to pārbauda izlaiduma atbildīgais. Ievadē obligāti jānorāda atbilstošs `assessment_id` un `version`; nepazīstami kontroļu ID tiek noraidīti. Izmanto `--fail-on-blocked`, lai `BLOCKED` izraisītu CI kļūdu, vai `--require-ready`, ja jebkurai nepilnībai jāaptur CI.

`VERIFIED` prasa pierādījuma piezīmi. `NOT_APPLICABLE` atļauts tikai kontrolēm, kur tas skaidri paredzēts, un prasa pamatojumu.

## Jomas

1. Atbildība un izpratne
2. Autentifikācija un autorizācija
3. Dati un noslēpumi
4. Atkarības un piegādes ķēde
5. Ievades un biznesa loģika
6. MI aģenti, MCP un rīku piekļuve
7. Izvietošana un izpildvide
8. Izlaišanas pierādījumi

## Anti-AI-Slop indikatori

Repozitorijā ir arī 16 praktiski brīdinājuma signāli — piemēram, akla MI ieteiktu atkarību instalēšana, klienta puses autorizācija, neierobežotas kodēšanas aģenta tiesības, drošības pārbaužu atslēgšana, lai būvējums izietu, vai liela ģenerēta diff mergeošana bez izpratnes.

Šie indikatori ir diagnostikas jautājumi, nevis ievainojamību klasifikācija.

## Ātra palaišana

```bash
python3 scripts/validate.py
python3 scripts/render.py --check
python3 -m unittest discover -s tests -v
python3 scripts/assess.py examples/answers.example.json --lang lv
```

Repozitorija rīki nenosūta novērtējuma atbildes ārpus lokālās vides.

## Avotu pieeja

Kontroļu formulējumi ir oriģināli projekta formulējumi, kas balstīti reģistrētajos avotos.

- NIST SSDF 1.1 ir vispārīgais drošas programmatūras izstrādes pamats.
- OWASP ASVS 5.0.0 dod aplikāciju drošības verifikācijas pamatojumu.
- OWASP Secure Coding with AI sedz MI atbalstītai izstrādei specifiskos riskus.
- OWASP Top 10 for Agentic Applications 2026 tiek izmantots tikai tur, kur būtiska ir agentiska/rīkus izmantojoša uzvedība.
- OpenSSF vadlīnijas palīdz definēt drošas AI code-assistant instrukcijas un cilvēka pārskata robežas.

Avota atsauce nozīmē pamatojumu/saskaņojumu, nevis kopētu oficiālo formulējumu, sertifikāciju vai izdevēja endorsement.

## Audita statuss

`v0.1.1` ir **auditēta pilota bāzes versija**. Pirms publicēšanas kandidāts tika pārbaudīts piecos virzienos: metodoloģija, avotu atbilstība, pārklājums/dublēšanās, EN/LV lokalizācija un release-gate/pierādījumu semantika. Secinājumi un iestrādātie labojumi ir fiksēti `audits/2026-09-23-skeptical-audit.md`.

## Autors

**Zigmārs Ancveirs** — tehnoloģiju vadītājs, programmatūras inženieris un neatkarīgs kiberdrošības pētnieks.

## Licence

Dokumentācija un novērtējuma dati: **CC BY 4.0**. Kods un automatizācija: **MIT**.
