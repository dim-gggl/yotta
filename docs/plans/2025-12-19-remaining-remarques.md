# Remaining Remarques — Implementation Plan

> **Date:** 2025-12-19 | **Updated:** 2026-02-17
> **Status:** En attente d'implémentation

**Objectif :** Corriger les problèmes restants identifiés lors de la review : validation des identifiants dans startcommand, réduction du bruit des tracebacks du loader, alignement du thème du spinner, et mise à jour du Quick Start dans le README.

**Architecture :** Seuls les modules ciblés sont modifiés. Les APIs publiques existantes sont préservées sauf là où une validation plus stricte ou des logs plus discrets sont nécessaires.

**Stack :** Python 3.10+, click/rich, textual, pytest.

---

### Task 1: Valider les identifiants dans startcommand ⬜

**Fichiers :**
- Modifier : `yotta/core/management/commands/startcommand.py`
- Tests : `yotta/core/tests/test_startcommand.py`

**Problème :** `_to_identifier()` fait un simple remplacement de chaîne sans vérifier les mots-clés Python, les chiffres en tête, ni les caractères invalides.

**Étapes :**
1. Écrire des tests en échec pour le rejet de noms invalides (non-identifiants, mots-clés Python via `keyword.iskeyword()`, chiffres en tête)
2. Lancer les tests → échecs attendus
3. Implémenter la validation dans `_prompt_identifier` et `_prompt_command_config` : utiliser `str.isidentifier()` + `keyword.iskeyword()`
4. Re-lancer les tests → tous verts

---

### Task 2: Réduire le bruit des tracebacks du loader ⬜

**Fichiers :**
- Modifier : `yotta/core/loader.py` (classe `_LoaderLogger`, ligne ~60)
- Tests : `yotta/core/tests/test_loader.py`

**Problème :** `traceback.format_exc()` est affiché systématiquement lors d'un `ImportError`, même sans `--verbose` ni `YOTTA_DEBUG`. Cela pollue la sortie en usage normal.

**Étapes :**
1. Ajouter un test vérifiant que le traceback est masqué en mode non-strict/non-verbose (sauf si `YOTTA_DEBUG=1`)
2. Lancer → échec attendu
3. Implémenter la suppression conditionnelle : afficher uniquement un résumé une ligne, traceback complet seulement si `YOTTA_DEBUG` ou `--verbose`
4. Re-lancer les tests → verts

---

### Task 3: Aligner le spinner sur le thème actif ⬜

**Fichiers :**
- Modifier : `yotta/ui/spinner.py` (ligne 9 : `style=DEFAULT_THEME.styles["primary"]`)
- Tests : `yotta/ui/tests/test_spinner.py` (étendre)

**Problème :** Le spinner utilise `DEFAULT_THEME` en dur au lieu de respecter le thème configuré via les settings ou passé au `YottaConsole`.

**Étapes :**
1. Écrire un test vérifiant que le spinner utilise le thème actif (pas `DEFAULT_THEME` forcé)
2. Modifier `yottaSpinner` pour accepter un thème en paramètre ou le résoudre via settings
3. Re-lancer les tests

---

### ~~Task 4: Supprimer le doublon d'alias yottaConsole~~ ✅

**Résolu** — `yotta/ui/console.py` ne contient qu'une seule définition de `yottaConsole`. Pas d'alias redondant.

---

### Task 5: Mettre à jour le Quick Start du README ⬜

**Fichiers :**
- Modifier : `README.md`

**Étapes :**
1. Remplacer les commandes par `uv run yotta startproject ...` / `uv run python manage.py ...`
2. Relire pour cohérence et qualité de l'anglais
3. Ajouter une mention de la version Python minimum (3.10+)

---

### Vérification finale

```bash
uv run python -m pytest                   # Tous les tests passent
uv run python -m compileall yotta          # Pas d'erreurs de syntaxe
```

Relecture manuelle du README après modifications.
