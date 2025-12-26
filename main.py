import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyttsx3
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
import PyPDF2
import threading
import os

class TextToolDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Text Tool Dashboard")
        self.root.geometry("900x700")
        self.root.configure(bg="#2C3E50")

        # Initialize Engines
        self.engine = pyttsx3.init()
        self.translator = Translator()
        
        # --- GUI LAYOUT ---
        
        # Header
        header_frame = tk.Frame(root, bg="#1ABC9C", height=80)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="TEXT TOOL DASHBOARD", font=("Arial", 24, "bold"), 
                 bg="#1ABC9C", fg="white").pack(pady=20)

        # Main Content Area
        content_frame = tk.Frame(root, bg="#2C3E50")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Side: Text Input
        left_frame = tk.Frame(content_frame, bg="#2C3E50")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="Enter Text or Open PDF:", fg="white", bg="#2C3E50", font=("Arial", 12)).pack(anchor="w")
        
        self.text_area = tk.Text(left_frame, height=20, font=("Arial", 12), bg="#ECF0F1", fg="#2C3E50")
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=10)

        # Right Side: Controls
        right_frame = tk.Frame(content_frame, bg="#34495E", width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))

        # --- CONTROLS ---

        # 1. Voice Settings
        self.create_section_label(right_frame, "Voice Settings")
        
        self.rate_label = tk.Label(right_frame, text="Speed:", bg="#34495E", fg="white")
        self.rate_label.pack()
        self.speed_scale = tk.Scale(right_frame, from_=50, to=300, orient=tk.HORIZONTAL, bg="#34495E", fg="white")
        self.speed_scale.set(150)
        self.speed_scale.pack(fill=tk.X, padx=10)

        self.voice_var = tk.StringVar(value="Male")
        tk.Radiobutton(right_frame, text="Male", variable=self.voice_var, value="Male", bg="#34495E", fg="white", selectcolor="#1ABC9C").pack(anchor="w", padx=10)
        tk.Radiobutton(right_frame, text="Female", variable=self.voice_var, value="Female", bg="#34495E", fg="white", selectcolor="#1ABC9C").pack(anchor="w", padx=10)

        # 2. Operations Buttons
        self.create_section_label(right_frame, "Operations")

        self.btn_speak = self.create_button(right_frame, "🔊 Speak Text", self.speak_text)
        self.btn_speech_to_text = self.create_button(right_frame, "🎤 Speech to Text", self.speech_to_text)
        self.btn_open_pdf = self.create_button(right_frame, "wf Open PDF", self.open_pdf)
        
        # 3. Translation
        self.create_section_label(right_frame, "Translation")
        
        # Language Dropdown
        self.lang_code_list = list(LANGUAGES.keys())
        self.lang_name_list = list(LANGUAGES.values())
        self.lang_combo = ttk.Combobox(right_frame, values=self.lang_name_list)
        self.lang_combo.set("english")
        self.lang_combo.pack(pady=5, padx=10, fill=tk.X)

        self.btn_translate = self.create_button(right_frame, "🌐 Translate", self.translate_text)

        # Status Bar
        self.status_label = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def create_section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Arial", 14, "bold"), bg="#34495E", fg="#1ABC9C", pady=10).pack(fill=tk.X)

    def create_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, font=("Arial", 11), bg="#1ABC9C", fg="white", 
                        activebackground="#16A085", activeforeground="white", command=command)
        btn.pack(pady=5, padx=10, fill=tk.X)
        return btn

    def set_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    # --- FUNCTIONALITY ---

    def speak_text(self):
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Text area is empty!")
            return

        def run_speak():
            self.set_status("Speaking...")
            voices = self.engine.getProperty('voices')
            # Try to select voice based on gender (0 is usually male, 1 female on most systems)
            if self.voice_var.get() == "Female" and len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)
            else:
                self.engine.setProperty('voice', voices[0].id)
            
            self.engine.setProperty('rate', self.speed_scale.get())
            self.engine.say(text)
            self.engine.runAndWait()
            self.set_status("Ready")

        threading.Thread(target=run_speak).start()

    def speech_to_text(self):
        def run_listen():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.set_status("Listening... Speak now.")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    self.set_status("Processing audio...")
                    text = recognizer.recognize_google(audio)
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, text)
                    self.set_status("Speech recognized.")
                except sr.UnknownValueError:
                    messagebox.showerror("Error", "Could not understand audio")
                    self.set_status("Error: Unknown Audio")
                except sr.RequestError:
                    messagebox.showerror("Error", "Could not request results. Check internet.")
                    self.set_status("Error: Connection Failed")
                except Exception as e:
                    self.set_status("Ready")

        threading.Thread(target=run_listen).start()

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.set_status(f"Reading {os.path.basename(file_path)}...")
            try:
                text = ""
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, text)
                self.set_status("PDF Loaded Successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read PDF: {e}")
                self.set_status("Error loading PDF")

    def translate_text(self):
        target_lang_name = self.lang_combo.get()
        if not target_lang_name:
            return

        # Find code for selected language name
        target_code = "en"
        for code, name in LANGUAGES.items():
            if name == target_lang_name:
                target_code = code
                break
        
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            return

        def run_translate():
            self.set_status("Translating...")
            try:
                translated = self.translator.translate(text, dest=target_code)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, translated.text)
                self.set_status("Translation Complete")
            except Exception as e:
                messagebox.showerror("Translation Error", f"Failed: {e}")
                self.set_status("Translation Failed")

        threading.Thread(target=run_translate).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToolDashboard(root)
    root.mainloop()
