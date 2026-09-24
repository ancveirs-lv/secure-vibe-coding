# EVIDENCE-001 — Artefaktu piesaiste konkrētam Git commit

**Statuss: auditēts izstrādes pamats; netiek apgalvots, ka v0.2.0 jau ir izlaista.**

Šis izvēles verifikators piesaista pašnovērtējumā deklarētos `IMPLEMENTED` un `VERIFIED` stāvokļus parastiem Git blob objektiem konkrētā lokālā produkta commit. Tas pārbauda SHA-256, noraida atkārtotas JSON atslēgas paša manifestā un piesaistītajās atbildēs, salīdzina EN/LV strukturālos rezultātus un brīdina par neiekomitētām izmaiņām. Esošā `v0.1.1` vērtēšanas loģika netiek mainīta.

## Uzticības robežas

- Hash sakritība apliecina konkrētu baitu atrašanos norādītajā **lokālajā Git commit**, nevis repozitorija autora identitāti vai attālā GitHub repozitorija stāvokli.
- `repository_hint` ir nepārbaudīta aprakstoša etiķete. Git commit SHA nav digitāls paraksts.
- Izdomātam testa žurnālam var būt derīgs SHA-256. `artifact_binding: PASS` apliecina **baitu piesaisti**, nevis kontroles efektivitāti, pierādījumu patiesumu vai neatkarīgu pārskatīšanu.
- `NOT_APPLICABLE` pamatojumu patiesums netiek pārbaudīts. INPUT-001 nostiprina tiešā `assess.py` JSON robežu, tostarp noraida atkārtotas atslēgas, bet tas nepārbauda N/A pamatojumu faktisko patiesumu.
- Rīks vienmēr uzrāda `release_authorized: false` un `evidence_claims_independently_verified: false`. `structural_gates` ir tikai esošie pašdeklarētie `v0.1.1` rezultāti.
- Tiek lasīti tikai konkrētajā commit iekļautie Git blob objekti. Lokālā darba direktorija izmaiņas tos neaizstāj.

## Izmantošana

[EN manifest struktūra un piemērs](README.md). Manifestā jābūt **visām 32 atbildēm**, un katram `IMPLEMENTED` vai `VERIFIED` stāvoklim jāpiesaista vismaz viens artefakts. `UNKNOWN`, `CLAIMED` un `NOT_APPLICABLE` stāvokļiem nevar pievienot verificēta artefakta piesaisti. Pašu manifestu glabā ārpus pārbaudāmā produkta commit, lai neveidotu pašatsauci.

```bash
python3 scripts/verify_evidence.py --repo /path/to/product-git-repository --manifest /path/to/external-manifest.json
python3 pilots/EVIDENCE-001/run_evidence_pilot.py --check
python3 -m unittest discover -s tests -v
```

**Tvērums:** tikai lokālu Git objektu un SHA-256 pārbaude bez tīkla pieprasījumiem. Netiek pārbaudīti paraksti, pārbaudītāja identitāte, pierādījumu patiesums, produkta drošība vai izvietošanas atļauja. Verifikatoru palaid tikai repozitorijiem, kuriem uzticies.
