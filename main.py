import tkinter as tk
import threading
import time
import os
from tkinter import filedialog, messagebox
from generator import generate_cryptarithm_with_progress

class CryptoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Крипторифма Генератор")

        self.wordlist = []
        self.mode = tk.StringVar(value="first")
        self.source = tk.StringVar(value="file")  # "file", "nltk", "russian"
        self.max_tries = tk.IntVar(value=1000)
        self.results = []

        # UI
        tk.Label(root, text="Источник словаря:").pack()
        tk.Radiobutton(root, text="📁 Пользовательский .txt", variable=self.source, value="file").pack()
        tk.Radiobutton(root, text="🇬🇧 NLTK (английский)", variable=self.source, value="nltk").pack()
        tk.Radiobutton(root, text="🇷🇺 Русский словарь", variable=self.source, value="russian").pack()

        tk.Button(root, text="📂 Загрузить слова", command=self.load_words).pack(pady=5)

        tk.Label(root, text="Режим поиска:").pack()
        tk.Radiobutton(root, text="До первого решения", variable=self.mode, value="first").pack()
        tk.Radiobutton(root, text="Полный перебор", variable=self.mode, value="all").pack()

        tk.Label(root, text="Мощность (попыток):").pack()
        tk.Entry(root, textvariable=self.max_tries).pack()

        tk.Button(root, text="🚀 Сгенерировать", command=self.generate).pack(pady=5)
        tk.Button(root, text="💾 Сохранить результат", command=self.save_results).pack(pady=5)

        self.output = tk.Text(root, height=20, width=70)
        self.output.pack()

    def load_words(self):
        self.wordlist.clear()
        source = self.source.get()

        if source == "russian":
            try:
                path = os.path.join("data", "russian-words.txt")
                with open(path, "r", encoding="windows-1251") as f:
                    self.wordlist = [
                        w.strip().upper() for w in f
                        if w.strip().isalpha() and 3 <= len(w.strip()) <= 6
                    ]
                messagebox.showinfo("Успех", f"Загружено слов (3–6 букв): {len(self.wordlist)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить russian-words.txt:\n{e}")

        elif source == "file":
            path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
            if path:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.wordlist = [
                            w.strip().upper() for w in f
                            if w.strip().isalpha() and 3 <= len(w.strip()) <= 6
                        ]
                    messagebox.showinfo("Успех", f"Загружено слов (3–6 букв): {len(self.wordlist)}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

        elif source == "nltk":
            try:
                import nltk
                nltk.download("words", quiet=True)
                from nltk.corpus import words
                self.wordlist = [
                    w.upper() for w in words.words()
                    if w.isalpha() and 3 <= len(w) <= 6
                ]
                messagebox.showinfo("Успех", f"Загружено слов из NLTK (3–6 букв): {len(self.wordlist)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить из NLTK:\n{e}")

    def generate(self):
        self.output.delete(1.0, tk.END)
        self.results.clear()
        if not self.wordlist:
            messagebox.showwarning("Нет словаря", "Пожалуйста, загрузите словарь.")
            return
        threading.Thread(target=self._generate_worker).start()

    def _generate_worker(self):
        start_time = time.time()
        self.output.insert(tk.END, "⏳ Генерация крипторифмы...\n")
        self.root.after(0, lambda: self.root.config(cursor="watch"))

        max_tries = self.max_tries.get()
        update_interval = max(1, max_tries // 50)

        def progress_callback(current):
            if current % update_interval == 0:
                self.output.delete("end-2l", tk.END)
                self.output.insert(tk.END, f"🔁 Попытка: {current}/{max_tries}\n")

        self.results = generate_cryptarithm_with_progress(
            self.wordlist,
            self.mode.get(),
            max_tries,
            progress_callback
        )

        self.root.after(0, lambda: self.root.config(cursor=""))

        self.output.delete(1.0, tk.END)

        if self.results:
            self.output.insert(tk.END, f"✅ Найдено крипторифм: {len(self.results)}\n\n")
            for idx, (expr, mapping) in enumerate(self.results, 1):
                self.output.insert(tk.END, f"{idx}. {expr}\n")
                for k, v in sorted(mapping.items()):
                    self.output.insert(tk.END, f"   {k} = {v}\n")
                self.output.insert(tk.END, "\n")
        else:
            self.output.insert(tk.END, "❌ Крипторифма не найдена\n")

        elapsed = time.time() - start_time
        self.output.insert(tk.END, f"\n⏱ Время генерации: {elapsed:.2f} сек\n")

    def save_results(self):
        if not self.results:
            messagebox.showwarning("Нет результата", "Нечего сохранять.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            for idx, (expr, mapping) in enumerate(self.results, 1):
                f.write(f"{idx}. {expr}\n")
                for k, v in sorted(mapping.items()):
                    f.write(f"   {k} = {v}\n")
                f.write("\n")

        messagebox.showinfo("Сохранено", f"Результат сохранён в:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoGUI(root)
    root.mainloop()
