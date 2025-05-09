import time
import re
import pyperclip
import threading
import tkinter as tk
from tkinter import font
import os

LOG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".lunarclient", "offline", "multiver", "logs", "latest.log")

TRIGGERS = {
    "une invasion de zombie et de": "minecraft",
    "1990": "hubble",
    "1492": "colomb",
    "capitale du Portugal": "lisbonne",
    "Quel est le plus grand oc": "pacifique",
    "1989": "mur de berlin",
    "dragon de Yugo": "adamaï",
    "proche du Soleil": "mercure",
    "Yugo a grandi": "emelka",
    "nommé Simba": "le roi lion",
    "corbeau qui affronte": "le corbeau noir",
    "planche et une voile": "planche à voile",
    "Or en 2023" : "messi",
    "grand organe du corps" : "peau",
    "jeu principale à Roland-Garros" : "terre battue",

}

def normalize(s: str) -> str:
    return s.strip().lower()

def evaluate_expression(expression: str):
    exp = expression.replace(" ", "")
    if not re.match(r'^\d+([+\-Xx*]\d+)*$', exp):
        return None
    try:
        safe_exp = exp.replace('X', '*').replace('x', '*')
        result = eval(safe_exp)
        return int(result)
    except Exception:
        return None

class FactionNoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Faction Nox - AutoRépondeur")
        self.root.configure(bg="#0e0e11")
        self.root.geometry("720x400")
        self.root.resizable(False, False)
        self.running = False
        self.thread = None

        # Fonts
        title_font = ("Segoe UI Black", 30)
        subtitle_font = ("Segoe UI", 12)
        result_font = ("Segoe UI Semibold", 14)

        # Title
        self.title_label = tk.Label(root, text="Faction Nox", font=title_font, fg="#00ffe1", bg="#0e0e11")
        self.title_label.pack(pady=(30, 5))

        # Divider
        self.divider = tk.Frame(root, bg="#00ffe1", height=2, width=300)
        self.divider.pack(pady=5)

        # Info
        self.subtitle = tk.Label(
            root,
            text="Lance la surveillance pour détecter et répondre automatiquement aux quiz Minecraft.",
            font=subtitle_font,
            bg="#0e0e11",
            fg="#cccccc",
            wraplength=600,
            justify="center"
        )
        self.subtitle.pack(pady=10)

        # Result box
        self.result_frame = tk.Frame(root, bg="#1a1a1f", bd=0, highlightthickness=1, highlightbackground="#333")
        self.result_frame.pack(pady=20, padx=30, fill=tk.X)

        self.result_label = tk.Label(
            self.result_frame,
            text="🔍 En attente de lancement...",
            font=result_font,
            bg="#1a1a1f",
            fg="white",
            wraplength=660,
            justify="center",
            pady=20
        )
        self.result_label.pack(fill=tk.X)

        # Button
        self.toggle_btn = tk.Button(
            root,
            text="▶ Lancer la surveillance",
            font=("Segoe UI", 13),
            width=24,
            bg="#00cc88",
            fg="white",
            relief="flat",
            activebackground="#00b377",
            activeforeground="white",
            command=self.toggle_watching,
            cursor="hand2"
        )
        self.toggle_btn.pack(pady=10)

    def toggle_watching(self):
        if not self.running:
            self.start_watching()
        else:
            self.stop_watching()

    def start_watching(self):
        self.running = True
        self.toggle_btn.config(text="■ Arrêter et fermer", bg="#cc3333", activebackground="#b32d2d")
        self.result_label.config(text="🟢 Surveillance en cours... En attente de détection.")
        self.thread = threading.Thread(target=self.tail_log, daemon=True)
        self.thread.start()

    def stop_watching(self):
        self.running = False
        self.root.destroy()

    def show_result(self, text):
        self.result_label.config(text=f"{text}\n📋 Réponse copiée dans le presse-papier.")

    def process_line(self, line):
        nl = normalize(line)

        if "combien font" in nl:
            match = re.search(r"combien font\s+([0-9+\-\sXx*]+)", nl)
            if match:
                expression = match.group(1).strip()
                result = evaluate_expression(expression)
                if result is not None:
                    pyperclip.copy(str(result))
                    self.show_result(f"🧮 {expression} = {result}")
                    return

        for phrase, to_copy in TRIGGERS.items():
            if phrase in nl:
                pyperclip.copy(to_copy)
                self.show_result(f"✅ Détection : « {phrase} » → réponse : {to_copy}")
                return

    def tail_log(self):
        try:
            with open(LOG_FILE_PATH, "r", encoding="latin-1") as f:
                f.seek(0, 2)
                while self.running:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    self.process_line(line)
        except Exception as e:
            self.show_result(f"❌ Erreur : {e}")
            self.stop_watching()

if __name__ == "__main__":
    root = tk.Tk()
    app = FactionNoxGUI(root)
    root.mainloop()
