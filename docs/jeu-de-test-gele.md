# Procedure de gel du jeu de test — Binome TTS

## Principe

Le jeu de test (echantillons de reference + dataset de validation audio de David)
doit etre **gele** avant toute adaptation du modele (notamment le fine-tuning LoRA
prevu semaines 6-8), conformement au garde-fou du projet :
*"Jeux de test geles avant adaptation."*

Geler signifie : figer une version precise, versionnee et identifiable, qui sert
de reference stable pour toute comparaison avant/apres modification du modele.

## Contenu concerne par le gel

- `eval/reference_samples/` — echantillons de reference (Mahefa, Voice Design VoxCPM2)
- `eval/audio_validator/dataset/` — jeu de test du validateur audio (David)

## Procedure de gel

1. Verifier que le contenu est stable (plus de modification prevue avant adaptation).
2. Verifier qu'aucune donnee sensible n'est presente (garde-fou projet).
3. Creer un tag Git dedie, horodate :

```bash
   git tag -a jeu-test-gele-v1 -m "Gel du jeu de test S1-2 - baseline avant adaptation LoRA"
   git push origin jeu-test-gele-v1
```

4. Documenter le gel ci-dessous (section "Historique des gels").
5. Toute modification ulterieure du contenu gele necessite une nouvelle version
   (`jeu-test-gele-v2`, etc.) et une revue inter-binomes, conformement au point
   de vigilance du dossier projet ("Les interfaces sont gelees tot...").

## Convention de version

- `jeu-test-gele-v1` : version initiale, mois 1 (baseline pre-adaptation)
- `jeu-test-gele-v2` : a creer si modification necessaire avant adaptation LoRA (S6)
- Toute version geleee reste accessible via `git checkout jeu-test-gele-vX`

## Historique des gels

| Version | Date | Contenu | Valide par | Commentaire |
|---|---|---|---|---|
| v1 | 07/08/2026 | reference_samples (5 echantillons) + audio_validator/dataset (24 fichiers) | Mahefa + David | Premiere version, voix 100% synthetique (Voice Design), aucune donnee sensible |

## Verification avant chaque gel (checklist)

- [ ] Aucun fichier `.env` ou secret dans le contenu gele
- [ ] Aucune voix humaine reelle sans consentement documente
- [ ] Manifest/documentation a jour et coherente avec les fichiers reels
- [ ] Contenu teste et reproductible (scripts relances avec succes)
- [ ] Validation croisee Mahefa + David effectuee
