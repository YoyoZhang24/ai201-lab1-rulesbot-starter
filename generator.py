from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.

    — Milestone 3:

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "game"     : the game name
      - "distance" : similarity score (you can use this to filter weak matches)

    Before writing code, talk through these with your group:
      - How will you format the chunks into a context block for the prompt?
      - What instructions will stop the model from answering beyond what the
        rules say? (Grounding is the whole point — a confident wrong answer
        is worse than an honest "I don't know.")
      - How will you surface which game each answer comes from?

    Your response should:
      1. Answer using only the retrieved context — not the model's general knowledge
      2. Make clear which game the answer comes from
      3. Say so clearly when the answer isn't in the loaded rules

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rule books. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )

    # Your implementation here.
    for i in range(len(retrieved_chunks)):
        retrieved_chunks[i]["text"] = f"[{retrieved_chunks[i]['game']}] {retrieved_chunks[i]['text']}"

    context = "\n---\n".join([chunk["text"] for chunk in retrieved_chunks if chunk["distance"] < 0.75])

    response = _client.chat.completions.create(
      model = LLM_MODEL,
      messages = [
        {
            "role": "system",
            "content": "You are a board game rules assistant. Answer questions using only the rule excerpts provided in the context below. Do not use your general knowledge about any game. Always state which game the rule comes from, using the game name shown in brackets in the context. Example: 'According to the Catan rules, ...' If the answer is not present in the provided excerpts, say: 'I don't see that covered in the loaded rules.'"
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}"
        }
      ],
    )
    return response.choices[0].message.content
