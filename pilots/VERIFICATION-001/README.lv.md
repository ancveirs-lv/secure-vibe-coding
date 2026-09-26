# VERIFICATION-001 — Parakstīta verifikācijas ieraksta provenance

**Statuss: auditēts izstrādes pamats; tas nav v0.2.0 izlaiduma apgalvojums un nav neatkarīga drošības sertifikācija.**

VERIFICATION-001 virs EVIDENCE-001 pievieno parakstītu verifikācijas ierakstu. Precīzs JSON ieraksts tiek pārbaudīts ar detached SSH parakstu pret operatora norādītu OpenSSH `allowed_signers` trust-store. Ieraksts tiek piesaistīts arī precīzam produkta commit un EVIDENCE-001 manifesta SHA-256.

## Deklarētās assurance klases

Ierakstā var norādīt vienu no četrām **deklarētām** klasēm:

- `SELF_REPORTED`
- `TOOL_VERIFIED`
- `HUMAN_REVIEWED`
- `INDEPENDENTLY_VERIFIED`

Vārds **deklarēta** ir būtisks. `INDEPENDENTLY_VERIFIED` gadījumā verifierim jānorāda `EXTERNAL` attiecība un parakstam jāiziet trust-store pārbaude. Tas kriptogrāfiski piesaista precīzo paziņojumu atslēgai, kuru operators ir atļāvis konkrētajai identitātes etiķetei.

Tas joprojām **nepierāda**, ka atslēga pieder nosauktajai reālās pasaules personai vai organizācijai, ka pārbaudītājs faktiski ir neatkarīgs, ka pierādījumi ir patiesi, ka produkts ir drošs vai ka tā izlaišana ir atļauta. Šiem secinājumiem vajadzīga ārēja pārvaldība.

## Komanda

```bash
python3 scripts/verify_verification.py   --record /path/to/verification-record.json   --evidence-report /path/to/evidence-report.json   --signature /path/to/verification-record.json.sig   --allowed-signers /path/to/allowed_signers
```

Precīzo ierakstu paraksta ar fiksētu namespace:

```bash
ssh-keygen -Y sign   -f /path/to/private_key   -n secure-vibe-coding-verification-v1   /path/to/verification-record.json
```

Trust-store sasaistes uzturēšana ir operatora atbildība. Assurance vēsturei kopā jāsaglabā verifikācijas ieraksts, paraksts, `allowed_signers` politikas versija, EVIDENCE-001 pārskats un evidence manifests.
