# Provenance

Repository: `ancveirs-lv/secure-vibe-coding`
Current published repository release: `v0.1.1`
Unreleased repository candidate: `v0.2.0`
Assessment contract version: `0.1.1`
Assessment baseline date: `2026-09-23`
Status: `v0.2.0-pre-release-audited-candidate`
Author: Zigmārs Ancveirs

The machine-readable JSON files under `data/` are the source of truth for the assessment model. Human-readable baseline documents are generated deterministically and checked in CI.

## Version semantics

Git tags and `CITATION.cff` version the repository/toolkit release. `data/meta.json["version"]` versions the assessment contract consumed by answer files, evidence manifests and verification records.

These versions may intentionally differ. The v0.2.0 candidate adds input hardening, Git/SHA-256 evidence binding, signed verification provenance and end-to-end integration without changing the 32-control assessment model, states or gate semantics. Therefore the assessment contract remains `0.1.1` unless those assessment semantics are deliberately revised.

Control and indicator wording is original project wording informed by registered sources. A source reference means rationale/alignment; it does not mean copied official wording, certification, compliance or publisher endorsement.

The initial public baseline incorporated a five-direction skeptical audit before publication. See `audits/2026-09-23-skeptical-audit.md`.

The v0.2.0 candidate has a separate five-direction pre-release audit. See `audits/2026-09-26-v0.2.0-pre-release-audit.md`.

The release gate intentionally avoids an aggregate security score.
