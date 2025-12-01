"""Script responsible for embedding text and inserting it into the vector database"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from sentence_transformers import SentenceTransformer

import asyncio

EMBEDDING_MODEL = "google/embeddinggemma-300m"

class DocumentChunker:
    def __init__(self, chunk_size=512, overlap=50):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", "- ", " ", ""]
        )

    def process_file(self, file_path: Path) -> list[str]:
        """Chooses which file chunking function to use based on the file type

        For now it only supports text files

        Returns a list of the document's chunks"""

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return self._process_text(text)
        
    def _process_text(self, text: str) -> list[str]:
        return self.text_splitter.split_text(text)

class EmbeddingsGenerator:
    def __init__(self) -> None:
        self.model = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
        self.chunker = DocumentChunker()

    async def generate_vectors(self, document_path: Path) -> None:
        """Chunk the document at the given file path and generate the vectors for it"""
        text_chunks = self.chunker.process_file(document_path)

        loop = asyncio.get_running_loop()

        vectors = await loop.run_in_executor(
                None, 
                lambda: self.model.encode(text_chunks)
        )
        return vectors
        
