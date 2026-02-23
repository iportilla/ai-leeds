
import os, json
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv()

def get_clients():
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"]
    )
    
    # Load index and metadata once
    index = faiss.read_index("vector_index.bin")
    with open("metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    return client, index, metadata

def embed_text(client, text):
    emb = client.embeddings.create(
        model=os.environ.get("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
        input=text
    )
    return emb.data[0].embedding

def retrieve(client, index, metadata, question, k=5):
    q_emb = embed_text(client, question)
    q_matrix = np.array([q_emb]).astype("float32")
    
    distances, indices = index.search(q_matrix, k)
    
    blocks = []
    for idx_num in indices[0]:
        if idx_num >= 0 and idx_num < len(metadata):
            meta = metadata[idx_num]
            blocks.append({
                "id": meta["id"],
                "content": meta["content"],
                "source": meta["source"]
            })
    return blocks

def generate_answer(client, question, evidence_blocks):
    user_prompt = build_user_prompt(question, evidence_blocks)
    resp = client.chat.completions.create(
        model=os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    return resp.choices[0].message.content
