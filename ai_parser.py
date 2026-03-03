import requests
import json
import logging

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIParser:
    def __init__(self, ollama_host='http://localhost:11434', model_name='mistral'):
        """
        Initialize the AI Parser using a local Ollama instance.

        Args:
            ollama_host (str): URL of the Ollama server.
            model_name (str): The name of the model to use (e.g., 'mistral', 'llama3', 'llama2:7b').
        """
        self.ollama_host = ollama_host
        self.model_name = model_name
        self.api_url = f"{self.ollama_host}/api/generate"
        logger.info(f"Initialized AIParser with model: {self.model_name} at {self.ollama_host}")

    def generate_prompt(self, extracted_text):
        """
        Generates the prompt instructing the LLM to extract specific entities as JSON.

        Args:
            extracted_text (str): The raw text extracted from the document.

        Returns:
            str: The full prompt for the LLM.
        """
        prompt = f"""Tu es un expert juridique et data analyst travaillant pour la Direction Générale des Impôts (DGI).
Ta tâche est d'analyser le texte suivant, qui est un acte d'enregistrement (ex: vente, location, etc.),
et d'en extraire toutes les informations clés de manière structurée.

Voici le texte de l'acte :
--- DEBUT DU TEXTE ---
{extracted_text}
--- FIN DU TEXTE ---

Extrais les entités suivantes si elles sont présentes. Si une information est manquante, mets `null`.
Format de sortie attendu : UN SEUL OBJET JSON VALIDE (ne rajoute pas de texte avant ou après le JSON).

Structure JSON attendue (à adapter selon les infos trouvées) :
{{
    "type_acte": "Nature de l'acte (ex: Vente immobilière, Cession de parts, etc.)",
    "date_acte": "Date de rédaction ou d'enregistrement de l'acte (format AAAA-MM-JJ si possible)",
    "parties_impliquees": [
        {{
            "role": "ex: Vendeur, Acheteur, Bailleur, Locataire",
            "nom": "Nom complet ou raison sociale",
            "cin_ou_rc": "Numéro de carte d'identité ou Registre de Commerce",
            "adresse": "Adresse complète"
        }}
    ],
    "biens_concernes": [
        {{
            "description": "Description du bien (ex: Appartement, terrain, etc.)",
            "adresse": "Adresse ou localisation du bien",
            "titre_foncier": "Numéro du titre foncier s'il existe",
            "superficie": "Superficie avec unité"
        }}
    ],
    "montant_transaction": {{
        "valeur": "Montant numérique (ex: 500000)",
        "devise": "Devise (ex: MAD, EUR)"
    }},
    "notaire_ou_redacteur": "Nom du notaire ou du cabinet ayant rédigé l'acte"
}}

Génère UNIQUEMENT le code JSON, sans aucun autre commentaire.
"""
        return prompt

    def parse_text(self, extracted_text):
        """
        Sends the extracted text to the local LLM and parses the JSON response.

        Args:
            extracted_text (str): The raw text from the document.

        Returns:
            dict: A dictionary containing the parsed JSON data, or None if extraction fails.
        """
        prompt = self.generate_prompt(extracted_text)

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json" # Ollama supports enforcing JSON output for supported models
        }

        try:
            logger.info(f"Sending request to Ollama ({self.model_name})...")
            response = requests.post(self.api_url, json=payload, timeout=1200)
            response.raise_for_status()

            result_json = response.json()
            generated_text = result_json.get("response", "")

            # Clean up potential markdown formatting around JSON if 'format: json' wasn't strictly respected by older models
            generated_text = generated_text.strip()
            if generated_text.startswith("```json"):
                generated_text = generated_text[7:]
            if generated_text.endswith("```"):
                generated_text = generated_text[:-3]
            generated_text = generated_text.strip()

            # Parse the string into a Python dictionary
            structured_data = json.loads(generated_text)
            logger.info("Successfully extracted structured data via LLM.")
            return structured_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Ollama server: {e}")
            logger.error("Make sure Ollama is running locally (e.g., 'ollama serve') and the model is downloaded ('ollama run <model>').")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode LLM response into JSON: {e}")
            logger.error(f"Raw LLM output was:\n{generated_text}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during AI parsing: {e}")
            return None

if __name__ == "__main__":
    # Test example
    # parser = AIParser(model_name="mistral")
    # test_text = "Acte de vente. Entre Monsieur Jean Dupont (Vendeur, CIN: AB12345) et Madame Marie Curie (Acheteuse). Le bien vendu est un appartement situé à Paris pour un montant de 300000 EUR."
    # data = parser.parse_text(test_text)
    # print(json.dumps(data, indent=2, ensure_ascii=False))
    pass
