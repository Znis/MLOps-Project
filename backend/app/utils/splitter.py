# Inspired by LlamaIndex's Sentence Splitter
# https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/node_parser/text/sentence.py
import nltk
from functools import partial
from app.tokenizer import token_size


class FixedSizeCharSplitter:
    """Split text into fixed-size chunks by character count with overlap."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        text = text.strip()
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            start = end - self.chunk_overlap
        return chunks

    def __call__(self, text: str) -> list[str]:
        return self.split(text)

sentence_tokenizer = nltk.tokenize.PunktSentenceTokenizer()

def split_by_separator(text, sep):
    splits = text.split(sep)
    res = [s + sep for s in splits[:-1]]
    if splits[-1]:
        res.append(splits[-1])
    return res

def split_sentences(text):
    spans = [s[0] for s in sentence_tokenizer.span_tokenize(text)] + [len(text)]
    return [text[spans[i]:spans[i+1]] for i in range(len(spans) - 1)]


class TextSplitter:
    def __init__(self, chunk_size, chunk_overlap=0):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitters = [
            partial(split_by_separator, sep='\n\n'),
            partial(split_by_separator, sep='\n'),
            split_sentences,
            partial(split_by_separator, sep=' ')
        ]
    
    def _split_recursive(self, text, level=0):
        if token_size(text) <= self.chunk_size or level == len(self.splitters):
            return [text]
        
        splits = []
        for s in self.splitters[level](text):
            if token_size(s) <= self.chunk_size:
                splits.append(s)
            else:
                splits.extend(self._split_recursive(s, level + 1))
        return splits

    def _merge_splits(self, splits):
        chunks = []
        current_chunk = ''
        current_splits = []

        for split in splits:
            if current_chunk and (token_size(current_chunk + split) > self.chunk_size):
                trimmed_chunk = current_chunk.strip()
                if trimmed_chunk:
                    chunks.append(trimmed_chunk)
                # Add overlap to next chunk
                last_splits = current_splits
                current_splits = []
                current_chunk = ''
                for s in reversed(last_splits):
                    if (token_size(s + current_chunk) > self.chunk_overlap or
                        token_size(s + current_chunk + split) > self.chunk_size
                    ):
                        break
                    current_chunk = s + current_chunk
                    current_splits.insert(0, s)

            current_chunk += split
            current_splits.append(split)
        
        trimmed_chunk = current_chunk.strip()
        if trimmed_chunk:
            chunks.append(trimmed_chunk)
        return chunks
    
    def split(self, text):
        splits = self._split_recursive(text)
        chunks = self._merge_splits(splits)
        return chunks
    
    def __call__(self, text):
        return self.split(text)
