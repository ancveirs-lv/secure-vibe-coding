# INPUT-001 — Fail-closed novērtējuma ievade

**Statuss: auditēts izstrādes hardening posms; tas nav v0.2.0 izlaiduma apgalvojums.**

INPUT-001 aizver PILOT-001 konstatēto atkārtotu JSON atslēgu parsera problēmu un nostiprina tiešo `assess.py` ievades robežu, nemainot 32 kontroļu modeli vai `BLOCKED` / `CONDITIONAL` / `READY` semantiku.

## Ievades noteikumi

- JSON objekta atslēgām jābūt unikālām visos ligzdojuma līmeņos.
- Nestandarta JSON konstantes, piemēram, `NaN` un `Infinity`, tiek noraidītas.
- Ievadei jābūt derīgam UTF-8 un ne lielākai par 1 MiB.
- Augšējā līmeņa lauki ir tikai `assessment_id`, `version` un `answers`.
- Esošie kontroļu ID, stāvokļu, pierādījumu piezīmju, N/A un CI gate noteikumi paliek spēkā.
- Derīga nepilnīga ievade joprojām ir atļauta, bet izlaistās kontroles kļūst par `UNKNOWN`, tāpēc tā nevar nemanāmi kļūt par `READY`.

Šis hardening posms pārbauda sintaksi un ievades kontraktu. Tas **neapstiprina** pierādījumu patiesumu, N/A pamatojuma faktisko pareizību vai produkta drošību.

## Palaišana

```bash
python3 pilots/INPUT-001/run_input_pilot.py --check
python3 -m unittest discover -s tests -v
```

Sākotnējais PILOT-001 duplicate-key atradums tiek saglabāts kā vēsturiska atsauce un INPUT-001 to atzīmē kā novērstu.
