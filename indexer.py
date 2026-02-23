
import os, glob, json
import concurrent.futures
from openai import OpenAI
import faiss
import numpy as np
from dotenv import load_dotenv

load_dotenv()

def get_clients():
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"]
    )
    return client

def embed(client, text):
    return client.embeddings.create(
        model=os.environ.get("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
        input=text
    ).data[0].embedding

def chunk(text, size=600):
    words = text.split()
    for i in range(0, len(words), size):
        yield " ".join(words[i:i+size])

def process_chunk(client, idx, ch, path):
    emb = embed(client, ch)
    return {
        "emb": emb,
        "doc": {
            "id": f"{os.path.basename(path)}#chunk{idx}",
            "content": ch,
            "source": os.path.basename(path)
        }
    }

def main():
    client = get_clients()
    docs = []
    embeddings = []
    
    # Gather all chunks first
    tasks = []
    for path in glob.glob("sample_docs/*.md"):
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        for idx, ch in enumerate(chunk(txt)):
            tasks.append((idx, ch, path))
            
    print(f"Found {len(tasks)} chunks to embed...")
    
    # Process chunks in parallel (max 10 threads to avoid rate limits)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_chunk, client, t[0], t[1], t[2]) for t in tasks]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            embeddings.append(res["emb"])
            docs.append(res["doc"])
    
    if len(docs) > 0:
        emb_matrix = np.array(embeddings).astype("float32")
        d = emb_matrix.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(emb_matrix)
        faiss.write_index(index, "vector_index.bin")
        
        with open("metadata.json", "w", encoding="utf-8") as f:
            json.dumps(docs)
            json.dump(docs, f, indent=2)
            
    print(f"Uploaded {len(docs)} chunks locally")

if __name__ == "__main__":
    main()
