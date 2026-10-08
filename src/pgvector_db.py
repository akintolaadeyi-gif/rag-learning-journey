"""
PGVECTOR DATABASE
Postgres with the pgvector extension (Supabase in production).

Same interface as InMemoryVectorDB, so the retriever and the eval do not
need to know which one they are talking to.

Needs DATABASE_URL in .env, e.g. the Supabase session pooler connection string.
"""
import os
from typing import Dict, List

import psycopg
from dotenv import load_dotenv

load_dotenv()


def to_pgvector(embedding: List[float]) -> str:
    """pgvector accepts vectors written as text: '[0.1,0.2,...]'"""
    return "[" + ",".join(str(float(x)) for x in embedding) + "]"


class PgVectorDB:
    def __init__(self, table: str = "documents", dim: int = 384, url: str = None):
        if not table.replace("_", "").isalnum():
            raise ValueError("table name must be letters, numbers or underscores")
        self.table = table
        url = url or os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL is not set. Add it to your .env file.")
        # prepare_threshold=None keeps this working through Supabase's connection pooler
        self.conn = psycopg.connect(url, autocommit=True, prepare_threshold=None)
        with self.conn.cursor() as cur:
            cur.execute("create extension if not exists vector")
            cur.execute(
                f"create table if not exists {self.table} ("
                "  id text primary key,"
                "  content text not null,"
                f"  embedding vector({dim}) not null"
                ")"
            )

    def add_document(self, doc_id: str, text: str, embedding: List[float]):
        """Insert, or update if the id already exists, so re-indexing is safe."""
        with self.conn.cursor() as cur:
            cur.execute(
                f"insert into {self.table} (id, content, embedding) values (%s, %s, %s::vector) "
                "on conflict (id) do update set content = excluded.content, embedding = excluded.embedding",
                (doc_id, text, to_pgvector(embedding)),
            )

    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """<=> is pgvector's cosine distance. Similarity = 1 - distance."""
        with self.conn.cursor() as cur:
            cur.execute(
                f"select id, content, 1 - (embedding <=> %s::vector) as score "
                f"from {self.table} order by embedding <=> %s::vector limit %s",
                (to_pgvector(query_embedding), to_pgvector(query_embedding), k),
            )
            rows = cur.fetchall()
        return [
            {"id": r[0], "text": r[1], "metadata": {"source": r[0]}, "score": float(r[2])}
            for r in rows
        ]

    def count(self) -> int:
        with self.conn.cursor() as cur:
            cur.execute(f"select count(*) from {self.table}")
            return cur.fetchone()[0]

    def drop(self):
        with self.conn.cursor() as cur:
            cur.execute(f"drop table if exists {self.table}")
