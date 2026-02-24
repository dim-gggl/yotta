# Scaffolding Remarques — Implementation Plan

> **Date :** 2025-12-19 | **Mis à jour :** 2026-02-17
> **Status :** En attente d'implémentation

**Objectif :** Corriger les problèmes de robustesse des commandes de scaffolding (`startproject`, `startapp`) : métadonnées pyproject, délai artificiel, détection du projet racine, validation des noms d'app.

**Architecture :** Ajustements ciblés sur les templates startproject et le flux startapp. Les options CLI existantes et les sorties sont préservées.

**Stack :** Python 3.10+, uv, click/rich-click, ops filesystem.

---

### Task 1: Ajouter `[build-system]` au pyproject.toml généré ⬜

**Fichiers :**
- Modifier : `yotta/core/management/commands/startproject.py` → `get_pyproject_template()`
- Test : vérification manuelle + test unitaire sur le contenu généré

**Problème :** Le template pyproject.toml généré par `startproject` ne contient pas de section `[build-system]`, ce qui empêche un `pip install -e .` correct.

**Étapes :**
1. Ajouter `[build-system]` avec `requires = ["setuptools", "wheel"]` et `build-backend = "setuptools.backends._legacy:_Backend"`
2. S'assurer que le flat layout et le src layout sont couverts
3. Vérifier que `uv pip install -e .` fonctionne sur un projet généré

---

### Task 2: Supprimer le `time.sleep(1)` dans startproject ⬜

**Fichiers :**
- Modifier : `yotta/core/management/commands/startproject.py` → méthode `run`, ligne 59

**Problème :** Un `time.sleep(1)` artificiel ralentit la création de projet sans raison fonctionnelle.

**Étapes :**
1. Supprimer `time.sleep(1)` à la ligne 59
2. Vérifier que le spinner entoure toujours l'appel à `create_structure`
3. Tester visuellement que l'affichage reste cohérent

---

### Task 3: Détection robuste du projet racine pour startapp ⬜

**Fichiers :**
- Modifier : `yotta/core/management/commands/startapp.py` → méthode `run`
- Ajouter : helper `_find_project_root()` dans le même module
- Tests : `yotta/core/tests/test_scaffolding.py` (étendre)

**Problème :** `project_name = os.path.basename(os.getcwd())` est fragile — il ne fonctionne que si l'utilisateur est à la racine du projet. Si l'utilisateur est dans un sous-dossier, le nom sera faux.

**Étapes :**
1. Implémenter `_find_project_root()` : remonter depuis `cwd` en cherchant des marqueurs (`manage.py`, `pyproject.toml`, `.yotta`)
2. Résoudre le package root en respectant `src/<project>` existant ; éviter les segments dupliqués
3. Maintenir `--dst` comme override prioritaire
4. Ajouter des tests unitaires simulant différentes positions cwd

---

### Task 4: Valider `app_name` avant génération ⬜

**Fichiers :**
- Modifier : `yotta/core/management/commands/startapp.py` → méthode `run`
- Tests : `yotta/core/tests/test_scaffolding.py` (étendre)

**Problème :** Aucune validation du nom d'app. Des noms avec séparateurs de chemin, mots-clés Python, ou caractères invalides sont acceptés silencieusement.

**Étapes :**
1. Rejeter les noms contenant des séparateurs de chemin (`/`, `\`)
2. Vérifier `str.isidentifier()` + `keyword.iskeyword()`
3. Émettre un message d'erreur clair et abort avant toute écriture de fichier
4. Ajouter des tests pour les cas limites

---

### Vérification finale

```bash
uv run python -m pytest                   # Tous les tests passent
uv run python -m compileall yotta          # Pas d'erreurs de syntaxe
```

Test manuel : générer un projet complet (`startproject` → `startapp`) et vérifier la structure.
