#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import sys
import os
from janus_swi import query_once, consult


class DavisPutnamGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Davis-Putnam SAT Solver")
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
        self.strategies = []
        
        self.create_widgets()
        self.load_prolog_file()
        self.load_strategies()
    
    
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
            text="Davis-Putnam SAT Solver", 
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
        problem_frame = ttk.LabelFrame(main_frame, text="Select Problem and Strategy", padding="10")
        problem_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        problem_frame.columnconfigure(1, weight=1)
        
        ttk.Label(problem_frame, text="Problem:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.problem_var = tk.StringVar()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        kb_dir = os.path.join(current_dir, "kbs")
        
        self.problems = {}
        if os.path.exists(kb_dir):
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
        problem_combo.grid(row=0, column=1, padx=10, pady=5)
        if self.problems:
            problem_combo.current(0)
        
        ttk.Label(problem_frame, text="Strategy:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.strategy_var = tk.StringVar()
        self.strategy_combo = ttk.Combobox(
            problem_frame, 
            textvariable=self.strategy_var, 
            values=self.strategies,
            state='readonly',
            width=40
        )
        self.strategy_combo.grid(row=1, column=1, padx=10, pady=5)
        
        run_btn = ttk.Button(
            problem_frame, 
            text="Run DP Solver", 
            command=self.run_dp_solver, 
            style='Accent.TButton'
        )
        run_btn.grid(row=0, column=2, padx=10, rowspan=2)
        
        compare_btn = ttk.Button(
            problem_frame, 
            text="Compare Strategies", 
            command=self.compare_strategies,
            style='Compare.TButton'
        )
        compare_btn.grid(row=0, column=3, padx=10, rowspan=2)
        
        # Configure button styles
        style = ttk.Style()
        style.configure(
            'Accent.TButton', 
            foreground='blue', 
            font=('Arial', 10, 'bold')
        )
        style.configure(
            'Compare.TButton', 
            foreground='green', 
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
        prolog_file = "dp_sat.pl"
        
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
    
    
    def load_strategies(self):
        if not self.prolog_loaded:
            return
        
        try:
            result = query_once("current_predicate(select_atom_most_balanced/2)")
            if result:
                self.strategies.append("select_atom_most_balanced")
            
            result = query_once("current_predicate(select_atom_shortest_clause/2)")
            if result:
                self.strategies.append("select_atom_shortest_clause")
            
            if self.strategies:
                self.strategy_combo['values'] = self.strategies
                self.strategy_combo.current(0)
                self.log_result(f"Loaded strategies: {', '.join(self.strategies)}\n\n")
            
        except Exception as e:
            self.log_result(f"Error loading strategies: {str(e)}\n")
    
    
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
        
        strategy = self.strategy_var.get()
        if not strategy:
            messagebox.showwarning("Warning", "Please select a strategy!")
            return
        
        try:
            self.log_result(f"\n{'='*60}\n")
            self.log_result(f"Loading KB from file: {file_path}\n")
            self.log_result(f"Strategy: {strategy}\n")
            self.log_result(f"{'='*60}\n\n")
            
            # Use the new formatted predicate
            query_str = f"run_dp_file_formatted('{file_path}', {strategy}, ResultType, ModelStr, Steps)"
            result = query_once(query_str)
            
            if result and 'Steps' in result:
                steps = result['Steps']
                result_type = result.get('ResultType', 'unknown')
                model_str = result.get('ModelStr', '')
                
                if result_type == 'UNSAT':
                    self.log_result(f"Result: UNSATISFIABLE\n")
                    self.status_var.set(f"UNSAT - Steps: {steps}")
                else:
                    self.log_result(f"Result: SATISFIABLE\n")
                    if model_str:
                        self.log_result(f"Model: [{model_str}]\n")
                    self.status_var.set(f"SAT - Steps: {steps}")
                
                self.log_result(f"Steps: {steps}\n\n")
            else:
                self.log_result("Query failed or returned no results.\n\n")
                self.status_var.set("Query failed")
        
        except Exception as e:
            self.log_result(f"Error: {str(e)}\n\n")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Error running DP solver:\n{str(e)}")
    
    
    def run_dp_solver(self):
        if not self.prolog_loaded:
            messagebox.showerror("Error", "Prolog file not loaded! Cannot run DP solver.")
            return
        
        problem_display = self.problem_var.get()
        problem_path = self.problems.get(problem_display)
        
        if not problem_path:
            messagebox.showwarning("Warning", "Please select a problem!")
            return
        
        strategy = self.strategy_var.get()
        if not strategy:
            messagebox.showwarning("Warning", "Please select a strategy!")
            return
        
        self.log_result(f"\n{'='*60}\n")
        self.log_result(f"Running: {problem_display}\n")
        self.log_result(f"Strategy: {strategy}\n")
        self.log_result(f"{'='*60}\n\n")
        
        try:
            # Use the new formatted predicate
            query_str = f"run_dp_file_formatted('{problem_path}', {strategy}, ResultType, ModelStr, Steps)"
            result = query_once(query_str)
            
            if result and 'Steps' in result:
                steps = result['Steps']
                result_type = result.get('ResultType', 'unknown')
                model_str = result.get('ModelStr', '')
                
                if result_type == 'UNSAT':
                    self.log_result(f"Result: UNSATISFIABLE\n")
                    self.status_var.set(f"UNSAT - Steps: {steps}")
                else:
                    self.log_result(f"Result: SATISFIABLE\n")
                    if model_str:
                        self.log_result(f"Model: [{model_str}]\n")
                    self.status_var.set(f"SAT - Steps: {steps}")
                
                self.log_result(f"Steps: {steps}\n\n")
            else:
                self.log_result("Query failed or returned no results.\n\n")
                self.status_var.set("Query failed")
        
        except Exception as e:
            self.log_result(f"Error: {str(e)}\n\n")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Error running DP solver:\n{str(e)}")
    
    
    def compare_strategies(self):
        if not self.prolog_loaded:
            messagebox.showerror("Error", "Prolog file not loaded!")
            return
        
        problem_display = self.problem_var.get()
        problem_path = self.problems.get(problem_display)
        
        if not problem_path:
            messagebox.showwarning("Warning", "Please select a problem!")
            return
        
        if len(self.strategies) < 2:
            messagebox.showwarning("Warning", "Need at least 2 strategies to compare!")
            return
        
        self.log_result(f"\n{'='*60}\n")
        self.log_result(f"COMPARING STRATEGIES\n")
        self.log_result(f"Problem: {problem_display}\n")
        self.log_result(f"{'='*60}\n")
        
        results = []
        
        for strategy in self.strategies:
            self.log_result(f"\nStrategy: {strategy}\n")
            self.log_result(f"{'-'*40}\n")
            
            try:
                # Use the new formatted predicate
                query_str = f"run_dp_file_formatted('{problem_path}', {strategy}, ResultType, ModelStr, Steps)"
                result = query_once(query_str)
                
                if result and 'Steps' in result:
                    steps = result['Steps']
                    result_type = result.get('ResultType', 'unknown')
                    model_str = result.get('ModelStr', '')
                    
                    if result_type == 'UNSAT':
                        self.log_result(f"Result: UNSATISFIABLE\n")
                    else:
                        self.log_result(f"Result: SATISFIABLE\n")
                        if model_str:
                            self.log_result(f"Model: [{model_str}]\n")
                    
                    self.log_result(f"Steps: {steps}\n")
                    results.append((strategy, steps))
                else:
                    self.log_result("Query failed\n")
                    results.append((strategy, None))
                    
            except Exception as e:
                self.log_result(f"Query failed\n")
                results.append((strategy, None))
        
        self.log_result(f"\n{'='*60}\n")
        self.log_result(f"COMPARISON SUMMARY\n")
        self.log_result(f"{'='*60}\n")
        
        for strategy, steps in results:
            if steps is not None:
                self.log_result(f"{strategy}: {steps} steps\n")
            else:
                self.log_result(f"{strategy}: Failed\n")
        
        valid_results = [(s, st) for s, st in results if st is not None]
        if len(valid_results) >= 2:
            best = min(valid_results, key=lambda x: x[1])
            worst = max(valid_results, key=lambda x: x[1])
            
            self.log_result(f"\nBest: {best[0]} ({best[1]} steps)\n")
            if best[1] != worst[1]:
                diff = worst[1] - best[1]
                self.log_result(f"Difference: {diff} steps\n")
        
        self.log_result("\n")
        self.status_var.set("Comparison completed")
    
    
    def log_result(self, message):
        """Append message to result text area"""
        self.result_text.insert(tk.END, message)
        self.result_text.see(tk.END)
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = DavisPutnamGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()