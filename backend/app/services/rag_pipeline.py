class RAGPipeline:
    def __init__(self):
        self._embedder = None
        self._vdb = None

    @property
    def embedder(self):
        if not self._embedder:
            self._embedder = Embeddings()
        return self._embedder

    @property
    def vdb(self):
        if not self._vdb:
            self._vdb = VectorStore()
        return self._vdb
