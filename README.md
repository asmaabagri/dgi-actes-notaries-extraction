# Système d'Extraction et Structuration de Données Non Structurées (DGI)

Ce projet permet d'automatiser l'extraction d'informations à partir de documents PDF (actes d'enregistrement, ventes, locations, etc.), qu'ils soient natifs ou scannés.
Le système utilise des techniques d'OCR (PaddleOCR) et un Modèle de Langage Local (LLM via Ollama) pour structurer les données en JSON, puis les sauvegarde dans une base de données MongoDB de façon totalement locale (on-premise), assurant la sécurité et la confidentialité des données.

## Prérequis

1. **Python 3.8+** installé sur votre machine.
2. **Ollama** installé et en cours d'exécution.
3. **MongoDB** installé et en cours d'exécution (par défaut sur `localhost:27017`).

## Installation

### 1. Cloner ou télécharger le projet

Ouvrez un terminal dans le dossier du projet.

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
# Sur Windows :
venv\Scripts\activate
# Sur Linux/Mac :
source venv/bin/activate
```

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```
*Note concernant PaddleOCR : L'installation de PaddlePaddle peut nécessiter des commandes spécifiques si vous souhaitez utiliser l'accélération GPU (CUDA). Consultez la [documentation officielle de PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR).*

### 4. Configurer Ollama

Assurez-vous qu'Ollama est installé (téléchargeable sur [ollama.com](https://ollama.com/)).
Téléchargez un modèle performant, par exemple `mistral` (recommandé pour ce type de tâche) ou `llama3`.

```bash
# Dans un terminal séparé, téléchargez le modèle (la première fois) :
ollama pull mistral

# Assurez-vous que le serveur Ollama tourne en arrière-plan :
ollama serve
```

### 5. Configurer MongoDB

Assurez-vous qu'une instance locale de MongoDB tourne. Le script va s'y connecter par défaut via `mongodb://localhost:27017/` et créera automatiquement la base `dgi_db` et la collection `actes_enregistrement`.

---

## Utilisation

1. Placez vos fichiers PDF à analyser dans le dossier `input_documents/` (le script le créera s'il n'existe pas).
2. Lancez le script principal :

```bash
python main.py
```

### Options de ligne de commande

Vous pouvez personnaliser l'exécution du script via des arguments :

```bash
# Spécifier un autre dossier d'entrée, un autre modèle Ollama, ou la langue de l'OCR ('fr' ou 'ar' ou 'en')
python main.py --input "./mes_pdf" --model "llama3" --lang "fr"
```

## Structure du Code

*   `main.py` : Script d'orchestration principal.
*   `extractor.py` : Module gérant l'extraction du texte (PyMuPDF pour le texte natif, PaddleOCR pour les images scannées).
*   `ai_parser.py` : Module gérant la communication avec Ollama et la structuration du JSON via des prompts spécifiques.
*   `database.py` : Module gérant la connexion et l'insertion dans MongoDB.
*   `requirements.txt` : Liste des dépendances.

## Fonctionnement du pipeline

1. **Lecture** : Le script parcourt le dossier spécifié.
2. **Extraction** : Pour chaque PDF, il tente de lire le texte natif. Si une page contient moins de 50 caractères, il la convertit en image et applique PaddleOCR.
3. **Structuration** : Le texte complet est envoyé au modèle Ollama avec un prompt demandant d'extraire les entités clés (parties, biens, montants) au format JSON.
4. **Sauvegarde** : Le JSON résultant est validé puis inséré dans MongoDB. Une copie locale du JSON est également sauvegardée dans le dossier source pour vérification rapide.
