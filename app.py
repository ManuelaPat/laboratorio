
chiave = st.secrets["superkey"] # evita di copiare la chiave di openai

import streamlit as st

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.chat_models import ChatOpenAI

st.header("VoldeBot")

from PIL import Image # serve a gestile le immagini
logo = Image.open("VoldeBot.PNG") #serve per aprire il file del logo
st.image(logo) #serve per visualizzare l'immagine

with st.sidebar:
  st.title("Carica i tuoi documenti")
  file = st.file_uploader("Carica il tuo file", type="pdf")

from PyPDF2 import PdfReader

if file is not None:
    testo_letto = PdfReader(file)

    testo = ""
    for pagina in testo_letto.pages:
        testo = testo + pagina.extract_text()
        # st.write(testo)

    # Usiamo il text splitter di Langchain
    testo_spezzato = RecursiveCharacterTextSplitter(
        separators="\n",
        chunk_size=1000, # Numero di caratteri per chunk
        chunk_overlap=150,
        length_function=len
        )

    pezzi = testo_spezzato.split_text(testo)
    #st.write(pezzi)

    #Generazione embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=chiave)

    # Vector store - FAISS (by Facebook)
    vector_store = FAISS.from_texts(pezzi, embeddings)

    # Prompt
    domanda = st.text_input("Chiedi al chatbot:")
    
    if domanda:
        st.write("Sto cercado le informazioni che mi hai richiesto...")
        rilevanti = vector_store.similarity_search(domanda)
        # st.write(match)
        
        # Definiamo l'LLM  
        #i pezzi rilevanti li mettiamo dentro openAI per generare la risposta
        llm = ChatOpenAI( 
            openai_api_key = chiave,
            temperature = 1.0,
            max_tokens = 1000,
            model_name = "gpt-3.5-turbo-0125") 
        # questo modello è buono sia per costi che per le ricerche
        # https://platform.openai.com/docs/models/compare

        # Output
        # Chain: prendi la domanda, individua i frammenti rilevanti,
        # passali all'LLM, genera la risposta
        chain = load_qa_chain(llm, chain_type="stuff") 
        risposta = chain.run(input_documents = rilevanti, question = domanda)
        st.write(risposta)
