from pathlib import Path
from langchain.text_splitter import CharacterTextSplitter
import faiss
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import pickle

# data = []
# sources = []
# for p in ps:
#     with open(p) as f:
#         data.append(f.read())
#     sources.append(p)



with open('paper-dir/main.txt') as f:
    paper_text = f.read()

split_chars = ["§", "§.§"]
data = []
for c in split_chars:
    paper_text = paper_text.replace(c, "§")
data = paper_text.split("§")

# metadatas is the rest of the text on the same line as the section symbol
sources = []
for d in data:
    sources.append(d.split("\n")[0].strip())
    # data = [d.split("\n")[1:] for d in data]

sources[0] = "Beginning of paper"

# Here we split the documents, as needed, into smaller chunks.
# We do this due to the context limits of the LLMs.
text_splitter = CharacterTextSplitter(chunk_size=1500, separator="\n")
docs = []
metadatas = []
for i, d in enumerate(data):
    splits = text_splitter.split_text(d)
    docs.extend(splits)
    metadatas.extend([{"source": sources[i]}] * len(splits))

# Here we create a vector store from the documents and save it to disk.
store = FAISS.from_texts(docs, OpenAIEmbeddings(), metadatas=metadatas)
faiss.write_index(store.index, "docs.index")
store.index = None
with open("faiss_store.pkl", "wb") as f:
    pickle.dump(store, f)
