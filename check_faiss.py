import pickle
import faiss
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Just load the pkl to see if we can read it
with open("data/index/katekese_faiss_local/index.pkl", "rb") as f:
    data = pickle.load(f)
    print(type(data))
    
    # Let's inspect the first element
    docstore = data[0] # Usually a tuple (docstore, index_to_docstore_id)
    print(f"Total documents in docstore: {len(docstore._dict)}")

# Load the FAISS index
index = faiss.read_index("data/index/katekese_faiss_local/index.faiss")
print(f"Total vectors in index: {index.ntotal}")

try:
    vec = index.reconstruct(0)
    print(f"Success! Vector dimension: {len(vec)}")
except Exception as e:
    print(f"Cannot reconstruct: {e}")
