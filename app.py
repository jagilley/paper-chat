import datetime
import os
from langchain.chains import VectorDBQAWithSourcesChain
import gradio as gr
import langchain
import weaviate
from langchain.vectorstores import Weaviate
import faiss
import pickle
from langchain import OpenAI
from arxiv import get_paper
from ingest_faiss import create_vector_store

def get_vectorstore(suffix):
    index = faiss.read_index(f"{suffix}/docs.index")
    with open(f"{suffix}/faiss_store.pkl", "rb") as f:
        store = pickle.load(f)
    store.index = index
    return store

def set_openai_api_key(api_key, agent):
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        vectorstore = get_vectorstore()
        qa_chain = VectorDBQAWithSourcesChain.from_llm(llm=OpenAI(temperature=0), vectorstore=vectorstore)
        os.environ["OPENAI_API_KEY"] = ""
        return qa_chain

def download_paper_and_embed(paper_arxiv_url, api_key):
    if paper_arxiv_url and api_key:
        paper_text = get_paper(paper_arxiv_url)
        if 'abs' in paper_arxiv_url:
            eprint_url = paper_arxiv_url.replace("https://arxiv.org/abs/", "https://arxiv.org/e-print/")
        elif 'pdf' in paper_arxiv_url:
            eprint_url = paper_arxiv_url.replace("https://arxiv.org/pdf/", "https://arxiv.org/e-print/")
        else:
            raise ValueError("Invalid arXiv URL")
        suffix = 'paper-dir/' + eprint_url.replace("https://arxiv.org/e-print/", "")
        if not os.path.exists(suffix + "/docs.index"):
            create_vector_store(suffix, paper_text)

        os.environ["OPENAI_API_KEY"] = api_key
        vectorstore = get_vectorstore(suffix)
        qa_chain = VectorDBQAWithSourcesChain.from_llm(llm=OpenAI(temperature=0), vectorstore=vectorstore)
        os.environ["OPENAI_API_KEY"] = ""
        return qa_chain

chain = None

def chat(inp, history, paper_arxiv_url, api_key, agent):
    global chain
    if history is None:
        chain = download_paper_and_embed(paper_arxiv_url, api_key)
    history = history or []
    # if agent is None:
    #     history.append((inp, "Please paste your OpenAI key to use"))
    #     return history, history
    print("\n==== date/time: " + str(datetime.datetime.now()) + " ====")
    print("inp: " + inp)
    history = history or []
    agent = chain
    output = agent({"question": inp})
    answer = output["answer"]
    sources = output["sources"]
    history.append((inp, answer))
    history.append(("Sources?", sources))
    print(history)
    return history, history

block = gr.Blocks(css=".gradio-container {background-color: lightgray}")

with block:
    state = gr.State()
    agent_state = gr.State()
    with gr.Row():
        gr.Markdown("<h3><center>PaperChat</center></h3>")

        paper_arxiv_url = gr.Textbox(
            placeholder="Paste the URL of the paper about which you want to ask a question",
            show_label=False,
            lines=1,
            type="url",
        )

        openai_api_key_textbox = gr.Textbox(
            placeholder="Paste your OpenAI API key (sk-...)",
            show_label=False,
            lines=1,
            type="password",
        )

        # # button to download paper
        # download_paper_button = gr.Button(
        #     value="Download paper and make embeddings",
        #     variant="secondary",
        # ).click(
        #     download_paper_and_embed,
        #     inputs=[paper_arxiv_url, openai_api_key_textbox, agent_state],
        #     outputs=[agent_state],
        # )

    chatbot = gr.Chatbot()

    with gr.Row():
        message = gr.Textbox(
            label="What's your question?",
            placeholder="What's the answer to life, the universe, and everything?",
            lines=1,
        )
        submit = gr.Button(value="Send", variant="secondary").style(full_width=False)

    # gr.Examples(
    #     examples=[
    #         "What are agents?",
    #         "How do I summarize a long document?",
    #         "What types of memory exist?",
    #     ],
    #     inputs=message,
    # )

    gr.HTML(
        """This app demonstrates question-answering on any given arxiv paper"""
    )

    gr.HTML(
        "<center>Powered by <a href='https://github.com/hwchase17/langchain'>LangChain 🦜️🔗</a></center>"
    )

    submit.click(chat, inputs=[message, state, paper_arxiv_url, openai_api_key_textbox, agent_state], outputs=[chatbot, state])
    message.submit(chat, inputs=[message, state, paper_arxiv_url, openai_api_key_textbox, agent_state], outputs=[chatbot, state])

    # paper_arxiv_url.change(
    #     download_paper_and_embed,
    #     inputs=[paper_arxiv_url, agent_state],
    #     outputs=[agent_state],
    # )

    # openai_api_key_textbox.change(
    #     set_openai_api_key,
    #     inputs=[openai_api_key_textbox, agent_state],
    #     outputs=[agent_state],
    # )

block.launch(debug=True)
