"""Text cleaning and normalization functions."""

import re
import unicodedata


def clean_text(text: str) -> str:
    if not text:
        return ""

    # Normalisation Unicode
    text = unicodedata.normalize("NFC", text)

    # Supprimer marqueurs de page
    text = re.sub(r'---\s*Page\s*\d+\s*(?:\(OCR\))?\s*---', '', text)

    # Suppression des tirets 

    # Ligne entière de tirets 
    text = re.sub(r'^\s*[-=~_]{2,}\s*$', '', text, flags=re.MULTILINE)

    # Tirets en fin de ligne après du texte
    text = re.sub(r'\s*[-]{2,}\s*$', '', text, flags=re.MULTILINE)

    # Tirets en début de ligne avant du texte
    text = re.sub(r'^\s*[-]{2,}\s*', '', text, flags=re.MULTILINE)

    # Tirets au milieu entre deux parties de texte
    text = re.sub(r'\s*[-]{2,}\s*', ' ', text)

    # Espaces multiples
    text = re.sub(r'[ \t]+', ' ', text)

    # Sauts de ligne excessifs
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Guillemets typographiques
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")

    # Reconstruire titres espacés "A R T I C L E" → "ARTICLE"
    for _ in range(10):
        prev = text
        text = re.sub(r'([A-Z]) ([A-Z])', r'\1\2', text)
        if prev == text:
            break

    # Normaliser montants
    def normalize_amount(match):
        return re.sub(r'(\d)\s+(\d)', r'\1\2', match.group(0))

    text = re.sub(
        r'\d[\d\s.,]+(?:DH|dirhams?|euros?|€|\$)',
        normalize_amount,
        text,
        flags=re.IGNORECASE
    )

    # Normaliser N°
    text = re.sub(r'N\s+°', 'N°', text)

    # Strip lignes + supprimer lignes vides
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    text = '\n'.join(lines)

    return text
