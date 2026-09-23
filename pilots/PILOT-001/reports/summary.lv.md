# PILOT-001 — Sintētiskā izmēģinājuma rezultāti

**Rezultāts: PASS tikai strukturētajai CLI darbībai.** Nav pārbaudīts neviens reāls produkts.

Pamats: `v0.1.1` commit `94f4a47ad8c6400d9b6fd15b9d7d6f904f0cc519`; 32 kontroles, astoņas jomas un 16 diagnostiski indikatori.

| Scenārijs | Sagaidāmais | EN rezultāts | LV rezultāts | Bloķējošās nepilnības | Visas nepilnības |
| --- | --- | --- | --- | ---: | ---: |
| `blocked` | `BLOCKED` | `BLOCKED` | `BLOCKED` | 8 | 9 |
| `conditional` | `CONDITIONAL` | `CONDITIONAL` | `CONDITIONAL` | 0 | 3 |
| `ready` | `READY` | `READY` | `READY` | 0 | 0 |

Noraidīti **13** kļūdainas ievades vektori abās valodās.
Pārbaudītas **12** CI atgriešanās kodu kombinācijas.
Nepilnīgas atbildes bloķē izlaišanu (`BLOCKED`).

## Apzināti fiksētie ierobežojumi

- **LIM-EVIDENCE-001:** izdomātas, netukšas pierādījumu virknes var radīt `READY`. Rīks pārbauda **esamību, nevis patiesumu**.
- **LIM-APPLICABILITY-002:** tur, kur atļauts N/A, netukšs pamatojums tiek pieņemts bez faktu pārbaudes.
- **LIM-DUPLICATE-003:** atkārtotas JSON atbilžu atslēgas parsētājs apstrādā, saglabājot pēdējo vērtību; agrākas atbildes var palikt nemanītas.
- **LIM-SYNTHETIC-004:** scenāriji nepierāda neviena reāla produkta drošību.

**Interpretācija:** `READY` šajā izmēģinājumā pierāda formālu novērtēšanas loģiku, nevis atļauju izvietot programmatūru.
