import tkinter as tk
from tkinter import scrolledtext
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Define the template and model
template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer: 
"""
model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Define the chatbot class with a UI
class ChatBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI ChatBot")
        self.context = ""

        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", width=60, height=20, bg="white", fg="black", font=("Arial", 12))
        self.chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # User input area
        self.user_input = tk.Entry(root, width=50, font=("Arial", 12))
        self.user_input.grid(row=1, column=0, padx=10, pady=5)

        # Send button
        self.send_button = tk.Button(root, text="Send", command=self.handle_user_input, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.send_button.grid(row=1, column=1, padx=5, pady=5)

        # Bind Enter key to send messages
        root.bind("<Return>", lambda event: self.handle_user_input())

    def handle_user_input(self):
        user_message = self.user_input.get().strip()
        if user_message.lower() == "exit" or user_message == "":
            self.root.quit()

        # Display user message in the chat area
        self.display_message("You", user_message)

        # Get the chatbot's response
        result = chain.invoke({"context": self.context, "question": user_message})
        bot_response = result.strip()

        # Display bot message in the chat area
        self.display_message("Bot", bot_response)

        # Update context
        self.context += f"\nUser: {user_message}\nAI: {bot_response}"

        # Clear the input field
        self.user_input.delete(0, tk.END)

    def display_message(self, sender, message):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)


# Run the chatbot app
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatBotApp(root)
    root.mainloop()
