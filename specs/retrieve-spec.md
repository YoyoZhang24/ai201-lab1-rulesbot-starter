# Spec: `retrieve()`

**File:** `retriever.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user's natural language query, find the most relevant chunks from the vector store using semantic similarity search. Return them ranked by relevance so that `generate_response()` can use them as context.

---

## Input / Output Contract

**Inputs:**


| Parameter   | Type  | Description                                                                |
| ----------- | ----- | -------------------------------------------------------------------------- |
| `query`     | `str` | The user's natural language question                                       |
| `n_results` | `int` | Maximum number of chunks to return (default: `N_RESULTS` from `config.py`) |


**Output:** `list[dict]`

Each dict in the returned list must contain exactly these keys:


| Key          | Type    | Description                                                   |
| ------------ | ------- | ------------------------------------------------------------- |
| `"text"`     | `str`   | The chunk text                                                |
| `"game"`     | `str`   | The game name this chunk came from                            |
| `"distance"` | `float` | Cosine distance score — lower means more similar to the query |


Results should be ordered from most to least relevant (lowest to highest distance). Returns an empty list `[]` if the collection contains no documents.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Query approach

*Describe how you will use `_collection.query()` to find relevant chunks. What arguments will you pass, and why?*

```
_collection.query() takes 3 arguments: 

query_texts=[query], which wraps the user's question in a list. ChromaDB embeds this text using the same embedding function that was used during ingestion, so query and stored chunks live in the same vector space.

n_results=n_results, which controls how many top-K chunks to return. The default is based on the cofig file. ChromaDB finds the first n_results stored vectors who cosine distance is smallest from the query vector.

include=["documents", "metadatas", "distances"] requests three parallel arrays back (the raw chunk text to pass to the generator, the dict stored for each chunk so the users can know which game the rule came from, and the cosine distance score for filtering low-quality matches.
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
{
      "text": doc, 
      "game": meta["game"], 
      "distance": dist
}

results["documents"][0][i]: the raw chunk string stored during embed_and_store()
results["metadatas"][0][i]["game"]: the dict stored as {"game": c["game"]} in embed_and_store()
results["distances"][0][i]: cosine distance computed by ChromaDB's HNSW index
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
The nesting exists because query_texts accepts a batch of queries. You could pass ["question 1", "question 2"] and get back two inner lists, one per query. Even when you pass a single query, the API returns the same shape. Index [0] selects the results for your one query.

results["documents"][0]   # list of N chunk texts
results["metadatas"][0]   # list of N metadata dicts
results["distances"][0]   # list of N distance floats
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
The current implementation has no threshold filtering but returns all n_results regardless of distance.  

No threshold is simple but always returns something. It lets the generator decide but may return semantically irrelevant chunks if no good match exists.

Filtrering prevents hallucination-inducing noise from reaching the LLM, but may return an empty list for valid questions if threshold is poorly tuned.
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
(a) Collection is empty
Handled explicitly. It returns [] immediately before calling _collection.query(). Without it, ChromaDB would raise an error since you can't query zero vectors.

(b) Query matches no chunks well
ChromaDB always returns the closest n_results vectors it has, even if they're poor matches. The returned dicts will have high distance scores. The function returns them unchanged so the generator receives weak context. This is a known tradeoff of the no-threshold approach above.

(c) Query matches chunks from multiple games
Works naturally. The top-K results are ranked purely by distance, regardless of which game they come from. A query like "how do you draw cards?" might return chunks from Uno, Pandemic, and Codenames all in the same list. Each dict carries its "game" field so the generator can attribute each rule to the right game in its response.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: [your test query]
Top result game: [game name]
Distance score: [score]
Does it make sense? [yes / no / explain]
```

**One thing about the query results that surprised you:**

```
[your answer here]
```

