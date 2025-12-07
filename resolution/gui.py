#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import sys
import os
from io import StringIO
from janus_swi import query_once, consult


class ResolutionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Resolution Algorithm")
        width = 900
        height = 700
        self.root.geometry(f'{width}x{height}')
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        style = ttk.Style()
        style.theme_use('alt')
        
        self.file_path = tk.StringVar()
        self.prolog_loaded = False
        
        self.create_widgets()
        self.load_prolog_file()
    
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Resolution Algorithm", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Knowledge Base File", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W)
        
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=50)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2, padx=5)
        
        load_file_btn = ttk.Button(
            file_frame, 
            text="Load from File", 
            command=self.load_from_file
        )
        load_file_btn.grid(row=0, column=3, padx=5)
        
        # Problem selection frame
        problem_frame = ttk.LabelFrame(main_frame, text="Select Problem", padding="10")
        problem_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(problem_frame, text="Problem:").grid(row=0, column=0, sticky=tk.W)
        
        self.problem_var = tk.StringVar()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        kb_dir = os.path.join(current_dir, "kbs")
        
        self.problems = {}
        for fname in os.listdir(kb_dir):
            if fname.endswith(".pl"):
                problem_name = fname[:-3].replace('_', ' ').title()
                filepath = os.path.join(kb_dir, fname)
                self.problems[problem_name] = filepath
        
        problem_combo = ttk.Combobox(
            problem_frame, 
            textvariable=self.problem_var, 
            values=list(self.problems.keys()), 
            state='readonly',
            width=40
        )
        problem_combo.grid(row=0, column=1, padx=10)
        problem_combo.current(0)
        
        run_btn = ttk.Button(
            problem_frame, 
            text="Run Resolution", 
            command=self.run_resolution, 
            style='Accent.TButton'
        )
        run_btn.grid(row=0, column=2, padx=10)
        
        # Configure accent button style
        style = ttk.Style()
        style.configure(
            'Accent.TButton', 
            foreground='blue', 
            font=('Arial', 10, 'bold')
        )
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(
            results_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=25,
            font=('Courier', 10)
        )
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
    
    
    def load_prolog_file(self):
        prolog_file = "resolution.pl"
        
        if not os.path.exists(prolog_file):
            self.log_result(f"Warning: {prolog_file} not found in current directory.\n")
            self.log_result(f"Please make sure {prolog_file} is in the same directory as this script.\n")
            self.status_var.set("Prolog file not found")
            return
        
        try:
            consult(prolog_file)
            
            self.prolog_loaded = True
            
            self.log_result(f"Successfully loaded {prolog_file}\n")
            self.log_result("="*60 + "\n\n")
            self.status_var.set("Prolog file loaded successfully")
            
        except Exception as e:
            self.log_result(f"Error loading Prolog file: {str(e)}\n")
            self.status_var.set("Error loading Prolog file")
            messagebox.showerror("Error", f"Failed to load Prolog file:\n{str(e)}")
    
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Knowledge Base File",
            filetypes=[
                ("Prolog files", "*.pl"),
            ]
        )
        if filename:
            self.file_path.set(filename)
    
    
    def load_from_file(self):
        file_path = self.file_path.get()
        
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            return
        
        if not self.prolog_loaded:
            messagebox.showerror("Error", "Prolog file not loaded!")
            return
        
        try:
            self.log_result(f"\n{'='*60}\n")
            self.log_result(f"Loading KB from file: {file_path}\n")
            self.log_result(f"{'='*60}\n\n")
            
            result = query_once(f"run_resolution_file('{file_path}', Result)")
            
            if result:
                res_value = result.get('Result', 'unknown')
                self.log_result(f"Resolution Result: {res_value}\n\n")
                self.status_var.set(f"Completed - Result: {res_value}")
            else:
                self.log_result("Query failed or returned no results.\n\n")
                self.status_var.set("Query failed")
        
        except Exception as e:
            self.log_result(f"Error: {str(e)}\n\n")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Error running resolution:\n{str(e)}")
    
    
    def run_resolution(self):
        if not self.prolog_loaded:
            messagebox.showerror("Error", "Prolog file not loaded! Cannot run resolution.")
            return
        
        problem_display = self.problem_var.get()
        problem_path = self.problems.get(problem_display)
        
        if not problem_path:
            messagebox.showwarning("Warning", "Please select a problem!")
            return
        
        self.log_result(f"\n{'='*60}\n")
        self.log_result(f"Running: {problem_display}\n")
        
        try:
            self.log_result(f"\n{'='*60}\n")
            self.log_result(f"Loading KB from file: {problem_path}\n")
            self.log_result(f"{'='*60}\n\n")
            
            result = query_once(f"run_resolution_file('{problem_path}', Result)")
            
            if result:
                res_value = result.get('Result', 'unknown')
                self.log_result(f"Resolution Result: {res_value}\n\n")
                self.status_var.set(f"Completed - Result: {res_value}")
            else:
                self.log_result("Query failed or returned no results.\n\n")
                self.status_var.set("Query failed")
        
        except Exception as e:
            self.log_result(f"Error: {str(e)}\n\n")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Error running resolution:\n{str(e)}")
    
    
    def log_result(self, message):
        """Append message to result text area"""
        self.result_text.insert(tk.END, message)
        self.result_text.see(tk.END)
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = ResolutionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()