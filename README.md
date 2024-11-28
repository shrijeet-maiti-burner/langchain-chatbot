
# LangChain Knowledge Base Chatbot

This project is a **LangChain-powered chatbot** designed to answer user queries using a customizable knowledge base. Users can interact with the chatbot via a web interface, upload or type new knowledge bases, and experience memory-enabled conversational capabilities.

---

## **Features**

### **1. Knowledge Base Management**
- View and edit the current knowledge base (default or user-provided).
- Options to upload a `.txt` file or type a new knowledge base.

### **2. AI Chatbot**
- Provides real-time answers by retrieving context from the knowledge base.
- Retains conversation history for contextual and personalized interactions using LangChain's memory system.

### **3. Responsive Web Interface**
- Built with **Flask** for backend and **Bootstrap** for modern, responsive design.

---

## **Setup Instructions**

### **1. Install Dependencies**
Ensure you have Python 3.10+ installed. Install the required libraries manually:
```bash
pip install flask python-dotenv
pip install langchain langchain-cohere language-coomunity faiss-cpu cohere
```

### **2. Set Up the Environment**
1. Create a `.env` file in the project directory.
2. Add your **Cohere API Key**:
   ```env
   COHERE_API_KEY=your-cohere-api-key
   ```

### **3. Run the Application**
Start the Flask application:
```bash
python app.py
```
Visit the app at:
```
http://127.0.0.1:5000
```