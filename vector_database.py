"""Main class for interfacing with the vector database"""
import lancedb
import pyarrow as pa


class VectorDatabase:
    def __init__(self, db_path: str="./lancedb_data") -> None:
        self.db = lancedb.connect(db_path)

        # since we are using Gemma 3, it generates vectors of length 768
        self.schema = pa.schema([
            pa.field("vector", pa.list_(pa.float32(), 768)),
            pa.field("text", pa.string()),
            pa.field("filename", pa.string()),
            pa.field("chunk_id", pa.int32()),
            pa.field("collection_id", pa.string()), # For filtering later
            pa.field("timestamp", pa.float64())
        ])

        try:
            self.table = self.db.open_table("documents")
        except FileNotFoundError:
            self.table = self.db.create_table("documents", schema=self.schema)
