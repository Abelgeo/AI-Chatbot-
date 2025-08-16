import tkinter as tk
from tkinter import ttk, scrolledtext
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import asyncio
import threading
import json
import os

class ChatBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced AI ChatBot")
        self.root.geometry("700x500")
        self.context = ""
        self.is_dark_mode = False
        self.model = OllamaLLM(model="llama3")
        self.prompt = ChatPromptTemplate.from_template("""
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer: 
""")
        self.chain = self.prompt | self.model

        # Apply theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(
            self.main_frame, wrap=tk.WORD, state="disabled", width=60, height=20,
            font=("Arial", 12), bg="#ffffff", fg="#000000"
        )
        self.chat_area.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # User input area
        self.user_input = ttk.Entry(self.main_frame, width=50, font=("Arial", 12))
        self.user_input.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.user_input.focus()

        # Send button
        self.send_button = ttk.Button(
            self.main_frame, text="Send", command=self.handle_user_input, style="TButton"
        )
        self.send_button.grid(row=1, column=1, padx=5, pady=5)

        # Clear chat button
        self.clear_button = ttk.Button(
            self.main_frame, text="Clear Chat", command=self.clear_chat, style="TButton"
        )
        self.clear_button.grid(row=1, column=2, padx=5, pady=5)

        # Theme toggle button
        self.theme_button = ttk.Button(
            self.main_frame, text="Toggle Dark Mode", command=self.toggle_theme, style="TButton"
        )
        self.theme_button.grid(row=2, column=0, columnspan=3, pady=5)

        # Bind Enter key
        self.root.bind("<Return>", lambda event: self.handle_user_input())

        # Load conversation history
        self.load_history()

        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.chat_area.configure(bg="#2b2b2b", fg="#ffffff")
            self.style.configure("TButton", background="#4CAF50", foreground="#ffffff")
        else:
            self.chat_area.configure(bg="#ffffff", fg="#000000")
            self.style.configure("TButton", background="#4CAF50", foreground="#ffffff")

    def display_message(self, sender, message):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)

    def clear_chat(self):
        self.chat_area.config(state="normal")
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state="disabled")
        self.context = ""
        if os.path.exists("chat_history.json"):
            os.remove("chat_history.json")

    def save_history(self):
        history = {"context": self.context}
        with open("chat_history.json", "w") as f:
            json.dump(history, f)

    def load_history(self):
        if os.path.exists("chat_history.json"):
            with open("chat_history.json", "r") as f:
                history = json.load(f)
                self.context = history.get("context", "")
                if self.context:
                    self.display_message("History", self.context)

    def handle_user_input(self):
        user_message = self.user_input.get().strip()
        if user_message.lower() == "exit":
            self.save_history()
            self.root.quit()
            return
        if not user_message:
            return

        # Display user message
        self.display_message("You", user_message)
        self.user_input.delete(0, tk.END)

        # Show typing indicator
        self.display_message("Bot", "Typing...")
        self.root.update()

        # Run model in a separate thread to avoid freezing
        threading.Thread(target=self.run_model, args=(user_message,), daemon=True).start()

    def run_model(self, user_message):
        try:
            result = self.chain.invoke({"context": self.context, "question": user_message})
            bot_response = result.strip()

            # Remove typing indicator
            self.chat_area.config(state="normal")
            self.chat_area.delete("end-2l", "end-1l")
            self.chat_area.config(state="disabled")

            # Display bot response
            self.display_message("Bot", bot_response)

            # Update context
            self.context += f"\nUser: {user_message}\nAI: {bot_response}"
            self.save_history()

        except Exception as e:
            self.chat_area.config(state="normal")
            self.chat_area.delete("end-2l", "end-1l")
            self.chat_area.config(state="disabled")
            self.display_message("Bot", f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatBotApp(root)
    root.mainloop()