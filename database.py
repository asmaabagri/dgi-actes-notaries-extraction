import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="dgi_db", collection_name="actes_enregistrement"):
        """
        Initialize the MongoDB connection.

        Args:
            uri (str): MongoDB connection URI.
            db_name (str): The name of the database to use.
            collection_name (str): The name of the collection to store the documents.
        """
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None

        self.connect()

    def connect(self):
        """Establishes connection to the MongoDB server."""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')

            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info(f"Successfully connected to MongoDB at {self.uri}")
            logger.info(f"Using Database: '{self.db_name}', Collection: '{self.collection_name}'")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB server: {e}")
            logger.error("Please ensure MongoDB is running locally on port 27017.")
            self.client = None

    def insert_document(self, document_data, source_filename):
        """
        Inserts a structured document into the collection.

        Args:
            document_data (dict): The JSON data extracted by the AI.
            source_filename (str): The name of the original PDF file.

        Returns:
            str: The inserted document's ID as a string, or None if failed.
        """
        if not self.client or not self.collection is not None:
            logger.error("Cannot insert document: Database connection not established.")
            return None

        try:
            # Wrap the AI extracted data with metadata
            record = {
                "source_file": source_filename,
                "status": "processed",
                "extracted_data": document_data
            }

            result = self.collection.insert_one(record)
            logger.info(f"Successfully inserted document from '{source_filename}' with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except OperationFailure as e:
            logger.error(f"MongoDB operation failed during insertion: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during database insertion: {e}")
            return None

    def close(self):
        """Closes the database connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

if __name__ == "__main__":
    # Test example
    # db = DatabaseManager()
    # dummy_data = {"type_acte": "Test", "montant": 1000}
    # db.insert_document(dummy_data, "test_file.pdf")
    # db.close()
    pass
