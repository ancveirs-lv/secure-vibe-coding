# PILOT-002 — Assurance ķēdes end-to-end integrācija

**Statuss: sintētisks integrācijas pilots v0.2.0 kandidāta ceļam. Tas nav drošības sertifikācija, pentests, atbilstības noteikšana vai izlaišanas atļauja.**

PILOT-002 pārbauda pašreizējo baseline kā vienotu ķēdi, nevis katru slāni izolēti:

`novērtējuma ievade -> READY gate -> EVIDENCE-001 Git/SHA-256 piesaiste -> parakstīts VERIFICATION-001 ieraksts -> gala ierobežotais assurance rezultāts`

Pilots izveido pagaidu sintētisku produkta repozitoriju, vienā commit saglabā novērtējuma ievadi un 32 sintētiskus pierādījumu artefaktus un šo pašu commit izmanto visos turpmākajos posmos.

## Pieņemšanas nosacījumi

- viena un tā pati commit saglabātā novērtējuma ievade dod `READY` EN un LV;
- EVIDENCE-001 piesaista visas 32 kontroles regulāriem Git blobiem pie precīza subject commit;
- parakstītais VERIFICATION-001 ieraksts nes to pašu aprakstošo `repository_hint`, atsaucas uz to pašu commit un precīzu evidence manifesta SHA-256;
- detached paraksts verificējas tikai caur skaidri norādītu `allowed_signers` sasaisti;
- derīgs, bet cits evidence reports, mainīti hash, mainītas parakstītās subject piesaistes, izmaiņas pēc parakstīšanas un viltots `release_authorized=true` reports tiek noraidīti fail-closed;
- gala reports saglabā `false` reālās pasaules identitātei, organizatoriskajai neatkarībai, pierādījumu patiesumam, produkta drošībai un izlaišanas atļaujai.

## Atkārtošana

```bash
python3 pilots/PILOT-002/run_pilot.py --check
```

Deterministiskā commit reporta pārģenerēšanai:

```bash
python3 pilots/PILOT-002/run_pilot.py --write
```

## Interpretācija

`PASS` nozīmē, ka pašreizējie lokālie protokoli šajā sintētiskajā scenārijā savienojas, nezaudējot piesaistes semantiku. Tas **nenozīmē**, ka sintētiskie pierādījumi ir patiesi, ka noteikta reāla pārbaudītāja identitāte, ka organizācija faktiski ir neatkarīga, ka produkts ir drošs vai ka izvietošana ir atļauta.
