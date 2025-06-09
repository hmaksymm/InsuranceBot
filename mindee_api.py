import asyncio
from mindee import Client, product, AsyncPredictResponse
from config import MINDEE_API_KEY
import traceback
import os

class MindeeClient:
    def __init__(self):
        try:
            self.client = Client(api_key=MINDEE_API_KEY)
            print("Mindee client initialized successfully")
        except Exception as e:
            print(f"Error initializing Mindee client: {str(e)}")
            raise e

    async def recognize_document(self, filepath: str, doc_type: str) -> dict:
        loop = asyncio.get_event_loop()

        def _sync_call():
            try:
                print(f"Processing {doc_type} document: {filepath}")
                input_doc = self.client.source_from_path(filepath)
                print("Document loaded successfully")
                
                # Use DriverLicenseV1 for document processing
                result: AsyncPredictResponse = self.client.enqueue_and_parse(
                    product.DriverLicenseV1,
                    input_doc
                )
                
                # Extract text from the document
                readable_data = {
                    "full_text": str(result.document) if result.document else "No text extracted",
                    "document_type": doc_type
                }
                
                print(f"Extracted data from {doc_type}: {readable_data}")
                return readable_data
                
            except Exception as e:
                print(f"Error in document recognition: {str(e)}")
                print("Full traceback:")
                print(traceback.format_exc())
                raise e
            finally:
                # Clean up the temporary file
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"Cleaned up temporary file: {filepath}")
                except Exception as e:
                    print(f"Error cleaning up file {filepath}: {str(e)}")

        try:
            return await loop.run_in_executor(None, _sync_call)
        except Exception as e:
            print(f"Error in async execution: {str(e)}")
            raise e
