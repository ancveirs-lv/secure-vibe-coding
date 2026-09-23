# PILOT-001 — Izlaišanas nosacījumu darbības pārbaude

**Statuss: kontrolēts sintētisks izmēģinājums, nevis reāla produkta drošības novērtējums.**

Šajā izmēģinājumā tiek pārbaudīta publicētās Anti-AI-Slop `v0.1.1` versijas novērtēšanas loģika, nemainot tās pierādījumu nepilnību modeli bez kopējā punktu skaita. Katrā scenārijā ir visas 32 kontroles. Visas `VERIFIED` pierādījumu virknes ir skaidri apzīmētas ar **SYNTHETIC TEST TOKEN**; tās nepierāda reālu drošības verifikāciju.

## Trīs scenāriji

| Scenārijs | Sintētiskā situācija | Sagaidāmais rezultāts | Svarīgākā interpretācija |
| --- | --- | --- | --- |
| `blocked` | Nepilnības arhitektūrā, servera puses autorizācijā, lietotāju izolācijā, noslēpumos, atkarību pārbaudē, aģenta tiesībās un drošības testos | `BLOCKED` | Astoņas bloķējošas nepilnības — bez pietiekamiem pierādījumiem nevar apstiprināt izlaišanas gatavību. |
| `conditional` | Bloķējošās kontroles ir deklarētas kā izpildītas, bet nepietiek draudu modelēšanas, atjaunošanas un rollback pierādījumu | `CONDITIONAL` | Trīs nebloķējošas nepilnības; tas nav drošības apstiprinājums. |
| `ready` | Visām 32 kontrolēm ir `VERIFIED` un netukši **izdomāti demonstrācijas pierādījumi** | `READY` | Pierāda tikai strukturēto atbilžu pieņemšanu. Tas **nepierāda** produkta drošību vai pierādījumu patiesumu. |

## Palaišana

```bash
python3 pilots/PILOT-001/run_pilot.py --check
python3 pilots/PILOT-001/run_pilot.py --write
python3 -m unittest discover -s tests -v
```

`--check` salīdzina sagaidāmos rezultātus un pārbauda saglabātos deterministiskos pārskatus. `--write` pēc tām pašām pārbaudēm pārģenerē pārskatus. Izmēģinājums izmanto tikai Python standarta bibliotēku, nesūta tīkla pieprasījumus un neizvieto ievainojamu aplikāciju.

## Metodoloģiskās robežas

1. Identifikators, versija, 32 kontroles un atbilžu semantika ir piesaistīti publicētajam `v0.1.1` modelim.
2. Katrs pamatscenārijs tiek pārbaudīts **EN un LV**; rezultātiem, nepilnību ID un procesa statusiem jāsakrīt.
3. Visiem trim rezultātiem pārbaudām gan `--fail-on-blocked`, gan `--require-ready` atgriešanās kodus.
4. Pārbaudām kļūdainas ievades, neatbalstītus laukus un nepamatotu `NOT_APPLICABLE`. Nepilnīgas atbildes nedrīkst dot `READY`.
5. Apzināti fiksējam **pierādījumu autentiskuma ierobežojumu**: izdomāta, bet netukša pierādījuma virkne var radīt `READY`. Arī `NOT_APPLICABLE` pamatojuma patiesums netiek pārbaudīts; atkārtotas JSON atbilžu atslēgas parsētājs pašlaik apstrādā, saglabājot pēdējo vērtību. Tās ir konstatētas nepilnības nākamajai `v0.2.0` versijai, nevis noklusēti panākumi.

Rezultāti: `reports/results.json`, `reports/summary.en.md`, `reports/summary.lv.md`.

## Pieņemšanas robeža

PILOT-001 ir izturēts, ja tiek precīzi reproducēta aprakstītā **strukturālā** uzvedība un atklāti norādīti ierobežojumi. Rezultāts nav pamats reāla produkta publiskai izvietošanai — šeit nav reāla produkta vai autentificētu pierādījumu.

Nākamajā posmā jāievieš pierādījumu manifests, kas piesaistīts faktiskajiem commitiem, artefaktiem, pārbaudītāja identitātei un testa rezultātiem, un pēc tam jāveic neatkarīgi pārskatīts izmēģinājums ar konkrētu produktu.
