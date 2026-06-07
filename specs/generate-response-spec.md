# Spec: `generate_response()`

**File:** `generator.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user query and a list of retrieved rule chunks, generate a response that directly answers the question using only the retrieved text as context. The response must be grounded — it should not draw on the model's general knowledge of board games, only on what was retrieved.

---

## Input / Output Contract

**Inputs:**


| Parameter          | Type         | Description                                                                             |
| ------------------ | ------------ | --------------------------------------------------------------------------------------- |
| `query`            | `str`        | The user's original question                                                            |
| `retrieved_chunks` | `list[dict]` | Ranked list of chunks from `retrieve()`, each with `"text"`, `"game"`, and `"distance"` |


**Output:** `str`

A plain string containing the response to show the user. The response should:

- Answer the question using only the retrieved rule text
- Identify which game the answer comes from
- Acknowledge clearly when the answer is not found in the loaded rules

Returns a fallback string (not an error) when `retrieved_chunks` is empty.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Context formatting

*How will you format the retrieved chunks before passing them to the LLM? Describe the structure — not the code. Consider: will you label chunks by game? Include distance scores? Separate chunks with delimiters?*

```
`retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "game"     : the game name
      - "distance" : similarity score (you can use this to filter weak matches)

The chunks passed to the LLM will get labeled with its game name and a separator so the LLM can clearly attribute rules:

[Catan]
The first player to reach 10 victory points on their turn wins...
---
[Pandemic]
Players win collectively if all four diseases are cured before...
---
[Catan]
Victory points are earned by building settlements, cities...

Distance scores are excluded because they are meaningless to the LLM and would waste tokens.
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
You are a board game rules assistant. Answer questions using only the rule excerpts provided in the context below. Do not use your general knowledge about any game.
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
When answering, always state which game the rule comes from, using the game name shown in brackets in the context.

Example: "According to the Catan rules, ..."
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
If the answer is not present in the provided excerpts, say: "I don't see that covered in the loaded rules."
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
Filter chunks above a distance threshold (e.g. 0.75) before building context.

Tradeoff: clearer context and reduces hallucination risk, but requires tuning and may over-filter for niche queries. 
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
messages = [
    {
        "role": "system",
        "content": <grounding instruction + citation instruction>
    },
    {
        "role": "user",
        "content": f"Context:\n{context_block}\n\nQuestion: {query}"
    }
]

System message holds the behavioral constraints (grounding + citation). Kept here rather than in the user message so the model treats them as standing instructions, not part of the question.

User message holds both the context block and the question together. Putting them in the same turn mirrors how RAG prompts are conventionally structured: context is evidence the user is supplying, and the question follows naturally from it.
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: [your test query]
Response: [abbreviated response]
Correctly grounded? [yes / no]
Cited the right game? [yes / no]
```

**One thing you changed from your original spec after seeing the actual output:**

```
[your answer here]
```

