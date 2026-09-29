"""
RETRIEVER MODULE
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass
import time

@dataclass
class RetrievalMetrics:
    query: str
    retrieved_count: int
    retrieval_time_ms: float
    top_k: int
    relevance_scores: List[float]
    precision_at_k: float = None
    recall_at_k: float = None
    mrr: float = None

class InstrumentedRetriever:
    def __init__(self, vector_db, top_k: int = 5):
        self.vector_db = vector_db
        self.top_k = top_k
        self.metrics_log = []
    
    def retrieve(self, query: str, ground_truth_doc_ids: List[str] = None) -> Tuple[List[Dict], RetrievalMetrics]:
        start_time = time.time()
        results = self.vector_db.search(query, k=self.top_k)
        retrieval_time = (time.time() - start_time) * 1000
        
        documents = []
        relevance_scores = []
        retrieved_doc_ids = []
        
        for result in results:
            documents.append({
                'id': result.get('id'),
                'text': result.get('text'),
                'metadata': result.get('metadata', {}),
                'score': result.get('score')
            })
            relevance_scores.append(result.get('score', 0.0))
            retrieved_doc_ids.append(result.get('id'))
        
        metrics = RetrievalMetrics(
            query=query,
            retrieved_count=len(documents),
            retrieval_time_ms=retrieval_time,
            top_k=self.top_k,
            relevance_scores=relevance_scores
        )
        
        if ground_truth_doc_ids:
            metrics.precision_at_k = self._precision_at_k(retrieved_doc_ids, ground_truth_doc_ids)
            metrics.recall_at_k = self._recall_at_k(retrieved_doc_ids, ground_truth_doc_ids)
            metrics.mrr = self._mean_reciprocal_rank(retrieved_doc_ids, ground_truth_doc_ids)
        
        self.metrics_log.append(metrics)
        return documents, metrics
    
    def _precision_at_k(self, retrieved_ids: List[str], ground_truth_ids: List[str]) -> float:
        if not retrieved_ids:
            return 0.0
        retrieved_set = set(retrieved_ids[:self.top_k])
        ground_truth_set = set(ground_truth_ids)
        relevant_count = len(retrieved_set & ground_truth_set)
        return relevant_count / len(retrieved_set)
    
    def _recall_at_k(self, retrieved_ids: List[str], ground_truth_ids: List[str]) -> float:
        if not ground_truth_ids:
            return 0.0
        retrieved_set = set(retrieved_ids[:self.top_k])
        ground_truth_set = set(ground_truth_ids)
        relevant_count = len(retrieved_set & ground_truth_set)
        return relevant_count / len(ground_truth_set)
    
    def _mean_reciprocal_rank(self, retrieved_ids: List[str], ground_truth_ids: List[str]) -> float:
        ground_truth_set = set(ground_truth_ids)
        for rank, doc_id in enumerate(retrieved_ids[:self.top_k], 1):
            if doc_id in ground_truth_set:
                return 1.0 / rank
        return 0.0
