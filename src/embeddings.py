"""Embedding utilities used throughout the MyJob project.

The original codebase expected a module ``src.embeddings`` with a single helper
function ``embed_text`` that returns a NumPy array representing the semantic
embedding of a piece of text.  The module was missing, which caused import
errors in the clustering and evaluation scripts.

Implementation details
----------------------
* The Sentence‑Transformer model name can be overridden via an environment
  variable ``EMBEDDING_MODEL``.  If not set we fall back to the small,
  fast‑loading model ``all-MiniLM-L6-v2`` which is already listed in the
  project's ``requirements.txt``.
* The model is loaded **once** (lazy singleton) so repeated calls are cheap.
* ``embed_text`` accepts either a single string or a list of strings.  It always
  returns a ``numpy.ndarray`` of shape ``(dim,)`` for a single string or
  ``(n, dim)`` for a list.
* ``embed_text`` strips leading/trailing whitespace and skips empty strings –
  empty inputs return a zero‑vector of the appropriate dimensionality.
"""

import os
import logging
from typing import Iterable, Union
import numpy as np

# Lazy‑loaded singleton model instance
_MODEL = None
_LOGGER = logging.getLogger(__name__)


def _load_model():
    """Load the SentenceTransformer model based on ``EMBEDDING_MODEL``.

    The function is called only once; the global ``_MODEL`` variable holds the
    loaded instance for subsequent calls.
    """
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        _LOGGER.error("sentence_transformers not installed – please run `pip install -r requirements.txt`")
        raise exc
    model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    _LOGGER.info("Loading embedding model %s", model_name)
    _MODEL = SentenceTransformer(model_name)
    return _MODEL


def embed_text(text_or_texts: Union[str, Iterable[str]]) -> np.ndarray:
    """Return a dense embedding for the given text.

    Parameters
    ----------
    text_or_texts: ``str`` or an iterable of ``str``
        If a single string is supplied, a **1‑D** ``np.ndarray`` of shape
        ``(embedding_dim,)`` is returned.  If an iterable is supplied, a **2‑D**
        array of shape ``(n_samples, embedding_dim)`` is returned.

    Notes
    -----
    * Empty strings are replaced with a zero‑vector to keep dimensions stable.
    * The function always returns ``float32`` data for memory efficiency.
    """
    model = _load_model()
    if isinstance(text_or_texts, str):
        texts = [text_or_texts.strip()]
    else:
        texts = [t.strip() for t in text_or_texts]
    # Replace completely empty strings with a placeholder that yields a zero vector.
    empty_placeholder = "placeholder"
    empty_indices = [i for i, t in enumerate(texts) if not t]
    for i in empty_indices:
        texts[i] = empty_placeholder
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    embeddings = np.asarray(embeddings, dtype=np.float32)
    if empty_indices:
        embeddings[empty_indices] = 0.0
    if isinstance(text_or_texts, str):
        return embeddings[0]
    return embeddings

# Optional helper for batch encoding (used by some scripts)
def embed_texts(texts: Iterable[str]) -> np.ndarray:
    """Convenience wrapper that always returns a 2‑D array.

    Equivalent to ``embed_text(texts)`` but keeps the return type consistent.
    """
    return embed_text(list(texts))

