import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain_cohere import CohereEmbeddings
from langchain.vectorstores import FAISS

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("Cohere API key is missing. Please set it in the environment variables or .env file.")

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok = True)

chat_model = ChatCohere(
    model = "command-r-plus",
    cohere_api_key = COHERE_API_KEY
)

memory = ConversationBufferMemory()

default_knowledge_base = """
LangChain is an open-source framework designed to help developers build applications powered by large language models.
It provides tools for chaining prompts, managing memory, and integrating with external data sources.
Python is a versatile programming language used widely in data science, AI, web development, and more.
Generative AI refers to a class of artificial intelligence models capable of generating text, images, or other data types based on input prompts.
"""
with open("default_knowledge_base.txt", "w") as file:
    file.write(default_knowledge_base)

loader = TextLoader("default_knowledge_base.txt")
documents = loader.load()
embedding = CohereEmbeddings(cohere_api_key = COHERE_API_KEY, model = "embed-english-v3.0")
vectorstore = FAISS.from_documents(documents, embedding)


# flask routes
@app.route("/", methods = ["GET", "POST"])
def index():
    global vectorstore
    displayed_knowledge_base = default_knowledge_base

    if request.method == "POST":
        
        typed_knowledge_base = request.form.get("typed_knowledge_base")
        if typed_knowledge_base and typed_knowledge_base.strip():

            with open("typed_knowledge_base.txt", "w") as file:
                file.write(typed_knowledge_base)

            loader = TextLoader("typed_knowledge_base.txt")
            documents = loader.load()
            global embedding
            vectorstore = FAISS.from_documents(documents, embedding)

            displayed_knowledge_base = typed_knowledge_base
            return render_template("index.html", default_knowledge_base = displayed_knowledge_base)

        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)

                loader = TextLoader(filepath)
                documents = loader.load()
                vectorstore = FAISS.from_documents(documents, embedding)

                with open(filepath, "r") as f:
                    displayed_knowledge_base = f.read()

                return render_template("index.html", default_knowledge_base = displayed_knowledge_base)

        # if neither a file nor text was provided
        return redirect(request.url)

    # render homepage with the current or default KB
    return render_template("index.html", default_knowledge_base = displayed_knowledge_base)


@app.route("/chat", methods = ["GET", "POST"])
def chat():
    global vectorstore

    conversation_history = []  # to display on webpage

    if request.method == "POST":
        user_message = request.form.get("message")
        if user_message.lower() == "exit":
            return redirect(url_for("index"))

        docs = vectorstore.similarity_search(user_message, k = 1)
        context = docs[0].page_content if docs else "No relevant information found."

        conversation_history_prompt = "\n".join([
            f"{'You' if isinstance(msg, HumanMessage) else 'AI'}: {msg.content}"
            for msg in memory.chat_memory.messages
        ])
        prompt = (
            f"Conversation History:\n{conversation_history_prompt}\n\n"
            f"Context: {context}\n\n"
            f"User's Query: {user_message}\n"
            f"Respond based on the above context and conversation history."
        )

        response = chat_model.invoke([HumanMessage(content = prompt)])

        memory.chat_memory.add_user_message(user_message)
        memory.chat_memory.add_ai_message(response.content)

        conversation_history = [
            {"sender": "You", "message": msg.content} if isinstance(msg, HumanMessage)
            else {"sender": "AI", "message": msg.content}
            for msg in memory.chat_memory.messages
        ]

    return render_template("chat.html", conversation_history = conversation_history)

if __name__ == "__main__":
    app.run(debug = True)