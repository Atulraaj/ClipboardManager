import pyperclip #for accessing clipboard
import tkinter as tk #for gui
from tkinter import messagebox, scrolledtext #for alerts
from PIL import Image, ImageTk  #for images
import threading
import time
import queue

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Manager")
        self.root.geometry('600x450')
        self.clipboard_history = []
        self.running = True
        self.clipboard_queue = queue.Queue()

        self.setup_gui() #load the logos
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard)
        self.monitor_thread.start()
        self.root.after(100, self.check_clipboard_queue)

    def setup_gui(self):
    
        self.load_logo()      

        self.textbox = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=('Courier', 12))
        self.textbox.pack(expand=True, fill='both', padx=10, pady=10) #textbox

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=5)

        show_button = tk.Button(button_frame, text="Show Latest", command=self.show_latest_clipboard)
        show_button.pack(side='left', padx=5)

        delete_button = tk.Button(button_frame, text="Delete Selected", command=self.delete_selected_clipboard)
        delete_button.pack(side='left', padx=5)

        clear_button = tk.Button(button_frame, text="Clear History", command=self.clear_history)
        clear_button.pack(side='left', padx=5)

    def load_logo(self):
        try:
            
            logo_img = Image.open('logo.png')  
            logo_img = logo_img.resize((500, 100), Image.LANCZOS)  #logo 
            logo_photo = ImageTk.PhotoImage(logo_img) 

            # logo display
            logo_label = tk.Label(self.root, image=logo_photo)
            logo_label.image = logo_photo  
            logo_label.pack(pady=10)
        except FileNotFoundError:
            print("Logo file not found")

    def monitor_clipboard(self):
        previous_clipboard = ""
        while self.running:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != previous_clipboard and current_clipboard.strip():
                    self.clipboard_queue.put(current_clipboard)
                    previous_clipboard = current_clipboard
            except:
                pass
            time.sleep(0.5)

    def check_clipboard_queue(self):
        try:
            while True:
                item = self.clipboard_queue.get_nowait()
                if item not in self.clipboard_history:
                    self.clipboard_history.append(item)
                    self.update_clipboard_history()
        except queue.Empty:
            pass
        self.root.after(100, self.check_clipboard_queue)

    def update_clipboard_history(self):
        self.textbox.delete(1.0, tk.END)
        for idx, item in enumerate(reversed(self.clipboard_history), start=1):
            self.textbox.insert(tk.END, f"{idx}. {item}\n\n")

    def show_latest_clipboard(self):
        if self.clipboard_history:
            messagebox.showinfo("Latest Clipboard", self.clipboard_history[-1])
        else:
            messagebox.showinfo("Latest Clipboard", "Clipboard history is empty.")

    def delete_selected_clipboard(self):
        try:
            selected_text = self.textbox.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if selected_text in self.clipboard_history:
                self.clipboard_history.remove(selected_text)
                self.update_clipboard_history()
                messagebox.showinfo("Deleted", "Selected clipboard item deleted.")
            else:
                messagebox.showerror("Error", "Selected item not found in history.")
        except Exception:
            messagebox.showerror("Error", "No text selected.")

    def clear_history(self):
        self.clipboard_history.clear()
        self.textbox.delete(1.0, tk.END)
        messagebox.showinfo("Cleared", "Clipboard history cleared.")

    def stop_monitoring(self):
        self.running = False
        self.monitor_thread.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardManager(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_monitoring)
    root.mainloop() #this run the infinte loop to keep the gui open
