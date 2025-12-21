import customtkinter as ctk
import sys
import os
import io
from tabulate import tabulate

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ParserSimulationPlayer:
    """Canvas-based visualization player for step-by-step parsing"""
    
    def __init__(self, parent_frame, steps, parse_table=None):
        self.steps = steps
        self.current_step = 0
        self.is_playing = False
        self.play_speed = 1000  # ms
        self.parse_table = parse_table
        
        # Store parent for widget creation
        self.parent = parent_frame
        
        # Create the player UI
        self.create_controls()
        self.create_visualization()
        self.create_results_area()
        
        # Show first step
        self.show_step(0)
    
    def create_controls(self):
        """Create player control buttons"""
        controls_frame = ctk.CTkFrame(self.parent)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Step navigation
        nav_frame = ctk.CTkFrame(controls_frame)
        nav_frame.pack(side="left", padx=10)
        
        # First button (text instead of emoji)
        self.first_btn = ctk.CTkButton(
            nav_frame, text="First", width=60, height=30,
            command=lambda: self.show_step(0)
        )
        self.first_btn.grid(row=0, column=0, padx=2)
        
        # Previous button
        self.prev_btn = ctk.CTkButton(
            nav_frame, text="Prev", width=60, height=30,
            command=self.prev_step
        )
        self.prev_btn.grid(row=0, column=1, padx=2)
        
        # Pause/Play button
        self.play_btn = ctk.CTkButton(
            nav_frame, text="Play", width=60, height=30,
            command=self.toggle_play
        )
        self.play_btn.grid(row=0, column=2, padx=2)
        
        # Next button
        self.next_btn = ctk.CTkButton(
            nav_frame, text="Next", width=60, height=30,
            command=self.next_step
        )
        self.next_btn.grid(row=0, column=3, padx=2)
        
        # Last button
        self.last_btn = ctk.CTkButton(
            nav_frame, text="Last", width=60, height=30,
            command=lambda: self.show_step(len(self.steps)-1)
        )
        self.last_btn.grid(row=0, column=4, padx=2)
        
        # Step counter
        self.step_label = ctk.CTkLabel(
            controls_frame, 
            text="Step: 0/0",
            font=("Arial", 15)
        )
        self.step_label.pack(side="left", padx=20)
        
        # Speed control (BELOW navigation in separate frame)
        speed_frame = ctk.CTkFrame(controls_frame)
        speed_frame.pack(side="right", padx=10, fill="x", expand=True)
        
        ctk.CTkLabel(speed_frame, text="Speed:", font=("Arial", 14)).pack(side="left", padx=5)
        
        self.speed_slider = ctk.CTkSlider(
            speed_frame, from_=500, to=2000, 
            number_of_steps=5, width=150,
            command=self.update_speed
        )
        self.speed_slider.set(1000)
        self.speed_slider.pack(side="left", padx=10)
        
        self.speed_label = ctk.CTkLabel(
            speed_frame, text="1.0s", font=("Arial", 14)
        )
        self.speed_label.pack(side="left", padx=5)
    
    def create_visualization(self):
        """Create canvas for stack and input visualization"""
        vis_frame = ctk.CTkFrame(self.parent)
        vis_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Title
        ctk.CTkLabel(
            vis_frame, text="Live Parser State Visualization",
            font=("Arial", 17, "bold")
        ).pack(pady=5)
        
        # Canvas for drawing
        self.canvas = ctk.CTkCanvas(
            vis_frame, bg="#2b2b2b", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=20, pady=10)
    
    def create_results_area(self):
        """Create split area for trace table and parse table reference"""
        results_frame = ctk.CTkFrame(self.parent)
        results_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Configure grid for split view
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_columnconfigure(1, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Left side: Trace Table
        trace_frame = ctk.CTkFrame(results_frame)
        trace_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            trace_frame, text="Step Trace Table",
            font=("Arial", 17, "bold")
        ).pack(pady=5)
        
        # Create text widget for trace table
        self.trace_text = ctk.CTkTextbox(
            trace_frame, font=("Courier New", 15), height=150
        )
        self.trace_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.trace_text.configure(state="disabled")
        
        # Right side: Parse Table Reference
        parse_table_frame = ctk.CTkFrame(results_frame)
        parse_table_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            parse_table_frame, text="Parse Table Reference",
            font=("Arial", 17, "bold")
        ).pack(pady=5)
        
        # Create text widget for parse table
        self.parse_table_text = ctk.CTkTextbox(
            parse_table_frame, font=("Courier New", 15), height=150
        )
        self.parse_table_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.parse_table_text.configure(state="disabled")
        
        # Initialize trace table
        self.update_trace_table()
        
        # Display parse table if available
        if self.parse_table:
            self.display_parse_table()
    
    def display_parse_table(self):
        """Display the parse table in the reference panel"""
        if not self.parse_table:
            return
            
        self.parse_table_text.configure(state="normal")
        self.parse_table_text.delete("1.0", "end")
        
        try:
            # Collect all unique terminals (excluding 'e' for epsilon)
            terminals = set()
            for nt in self.parse_table:
                for terminal in self.parse_table[nt]:
                    if terminal != 'e':
                        terminals.add(terminal)
            
            sorted_terminals = sorted(terminals)
            
            # Build table data
            table_data = []
            for nt in sorted(self.parse_table.keys()):
                row = [nt]
                for terminal in sorted_terminals:
                    production = self.parse_table[nt].get(terminal)
                    if production:
                        row.append(production)
                    else:
                        row.append("")
                table_data.append(row)
            
            # Create headers
            headers = ["NT"] + sorted_terminals
            
            # Format with tabulate using grid format for solid lines
            result_text = tabulate(table_data, headers=headers, tablefmt="grid", stralign="left")
            
            self.parse_table_text.insert("1.0", result_text)
            self.parse_table_text.configure(state="disabled")
            
        except Exception as e:
            self.parse_table_text.insert("1.0", f"Parse table error: {str(e)}")
            self.parse_table_text.configure(state="disabled")
    
    def update_trace_table(self):
        """Update trace table using tabulate for proper formatting"""
        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", "end")
        
        # Prepare table data for tabulate
        table_data = []
        for i in range(self.current_step + 1):
            step_data = self.steps[i]
            
            # Format stack
            stack_str = str(step_data['stack'])
            if len(stack_str) > 20:
                stack_str = stack_str[:17] + "..."
            
            # Format input
            input_from_lookahead = step_data['input'][step_data['lookahead_index']:]
            input_str = ' '.join(input_from_lookahead)
            if len(input_str) > 15:
                input_str = input_str[:12] + "..."
            
            # Format action
            if step_data['action'] == 'expand':
                action_str = f"Expand: {step_data['production']}"
            else:
                action_str = f"Match: {step_data['input'][step_data['lookahead_index']]}"
            
            # Mark current step with arrow
            if i == self.current_step:
                step_num = f"→ {i+1}"
            else:
                step_num = str(i+1)
            
            table_data.append([step_num, stack_str, input_str, action_str])
        
        # Create headers
        headers = ["Step", "Stack", "Input", "Action"]
        
        # Format with tabulate
        result_text = tabulate(table_data, headers=headers, tablefmt="grid", stralign="left")
        
        self.trace_text.insert("1.0", result_text)
        self.trace_text.configure(state="disabled")
        self.trace_text.see("end")
    
    def draw_stack(self, stack):
        """Draw stack visualization on canvas"""
        self.canvas.delete("stack")
        
        box_width = 60
        box_height = 40
        start_x = 100
        start_y = 50
        
        # Draw stack label ABOVE
        self.canvas.create_text(
            start_x + box_width/2, start_y - 25,
            text="STACK (Top ↓)", 
            fill="#3a7ebf", font=("Arial", 15, "bold"),
            tags="stack"
        )
        
        # Draw stack boxes
        for i, symbol in enumerate(stack):
            y = start_y + (len(stack) - i - 1) * (box_height + 5)
            
            self.canvas.create_rectangle(
                start_x, y, start_x + box_width, y + box_height,
                fill="#3a7ebf", outline="#1f538d", width=2,
                tags="stack"
            )
            
            self.canvas.create_text(
                start_x + box_width/2, y + box_height/2,
                text=symbol, fill="white", font=("Arial", 15, "bold"),
                tags="stack"
            )
            
            if i == len(stack) - 1:
                self.canvas.create_rectangle(
                    start_x-2, y-2, start_x + box_width+2, y + box_height+2,
                    outline="#5dade2", width=3,
                    tags="stack"
                )
    
    def draw_input(self, input_buffer, lookahead_index):
        """Draw input buffer visualization on canvas"""
        self.canvas.delete("input")
        
        box_width = 50
        box_height = 40
        start_x = 300
        start_y = 50
        
        # Draw input label ABOVE
        self.canvas.create_text(
            start_x + len(input_buffer) * (box_width + 5) / 2, 
            start_y - 25,
            text="INPUT BUFFER", 
            fill="#2e7d32", font=("Arial", 15, "bold"),
            tags="input"
        )
        
        # Draw input boxes
        for i, token in enumerate(input_buffer):
            x = start_x + i * (box_width + 5)
            
            self.canvas.create_rectangle(
                x, start_y, x + box_width, start_y + box_height,
                fill="#2e7d32", outline="#1b5e20", width=2,
                tags="input"
            )
            
            self.canvas.create_text(
                x + box_width/2, start_y + box_height/2,
                text=token, fill="white", font=("Arial", 14, "bold"),
                tags="input"
            )
            
            if i == lookahead_index:
                self.canvas.create_rectangle(
                    x-2, start_y-2, x + box_width+2, start_y + box_height+2,
                    outline="#58d68d", width=3,
                    tags="input"
                )
                
                arrow_y = start_y - 15
                self.canvas.create_line(
                    x + box_width/2, arrow_y,
                    x + box_width/2, start_y,
                    arrow="last", fill="#58d68d", width=2,
                    tags="input"
                )
                
                self.canvas.create_text(
                    x + box_width/2, arrow_y - 10,
                    text=f"Lookahead",
                    fill="#58d68d", font=("Arial", 12, "bold"),
                    tags="input"
                )
    
    def show_step(self, step_index):
        """Show specific step in visualization"""
        if 0 <= step_index < len(self.steps):
            self.current_step = step_index
            step = self.steps[step_index]
            
            self.canvas.delete("all")
            self.draw_stack(step['stack'])
            self.draw_input(step['input'], step['lookahead_index'])
            
            self.update_trace_table()
            
            self.step_label.configure(
                text=f"Step: {step_index+1}/{len(self.steps)}"
            )
            
            self.prev_btn.configure(state="normal" if step_index > 0 else "disabled")
            self.next_btn.configure(state="normal" if step_index < len(self.steps)-1 else "disabled")
            self.first_btn.configure(state="normal" if step_index > 0 else "disabled")
            self.last_btn.configure(state="normal" if step_index < len(self.steps)-1 else "disabled")
            
            if step_index == len(self.steps) - 1 and self.is_playing:
                self.is_playing = False
                self.play_btn.configure(text="Play")
    
    def next_step(self):
        """Move to next step"""
        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
    
    def prev_step(self):
        """Move to previous step"""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def toggle_play(self):
        """Toggle auto-play"""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_btn.configure(text="Pause")
            self.play()
        else:
            self.play_btn.configure(text="Play")
    
    def play(self):
        """Auto-play animation"""
        if self.is_playing and self.current_step < len(self.steps) - 1:
            self.next_step()
            self.parent.after(self.play_speed, self.play)
        else:
            self.is_playing = False
            self.play_btn.configure(text="Play")
    
    def update_speed(self, value):
        """Update play speed"""
        self.play_speed = int(value)
        self.speed_label.configure(text=f"{value/1000:.1f}s")


class LL1ParserGUI:
    """Main GUI application for LL(1) Parser Visualizer"""
    
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("LL(1) Parser Visualizer")
        # Set window to fullscreen
        self.window.attributes('-fullscreen', True)
        # Bind Escape key to exit fullscreen
        self.window.bind('<Escape>', lambda e: self.toggle_fullscreen())
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.create_info_page()
        self.info_page.pack(fill="both", expand=True)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.window.attributes('-fullscreen', not self.window.attributes('-fullscreen'))
    
    def create_info_page(self):
        """Build Page 1: Information about LL(1) parsing"""
        self.info_page = ctk.CTkFrame(self.window)
        
        title = ctk.CTkLabel(
            self.info_page,
            text="LL(1) Parser Visualizer",
            font=("Arial", 36, "bold")
        )
        title.pack(pady=20)
        
        info_text = """LL(1) PARSING OVERVIEW

- LL(1) = Left-to-right, Leftmost derivation, 1 token lookahead
- Uses predictive parsing table
- Requires FIRST() and FOLLOW() sets
- No left recursion allowed

HOW TO USE

1. Enter grammar (one production per line)
2. Enter input string (space-separated tokens)
3. Click 'Calculate FIRST/FOLLOW'
4. View parse table
5. Parse input
6. View parse tree & simulation

GRAMMAR EXAMPLE

E -> T E'
E' -> + T E'
E' -> e
T -> F T'
T' -> * F T'
T' -> e
F -> ( E )
F -> id

RULES:
- Use '->' arrow
- One production per line
- Space-separated symbols
- Use 'e' for epsilon"""
        
        info_label = ctk.CTkLabel(
            self.info_page,
            text=info_text,
            font=("Courier New", 16),
            justify="left"
        )
        info_label.pack(pady=20, padx=20)
        
        test_button = ctk.CTkButton(
            self.info_page,
            text="Test Parser",
            command=self.go_to_parser,
            height=40,
            font=("Arial", 18)
        )
        test_button.pack(pady=20)
    
    def go_to_parser(self):
        """Switch from info page to parser page"""
        self.info_page.pack_forget()
        self.create_parser_page()
        self.parser_page.pack(fill="both", expand=True)
    
    def create_parser_page(self):
        """Build Page 2: Parser workspace with grammar input and results"""
        self.parser_page = ctk.CTkFrame(self.window)
        
        self.parser_page.grid_columnconfigure(0, weight=1)
        self.parser_page.grid_columnconfigure(1, weight=1)
        self.parser_page.grid_columnconfigure(2, weight=2)
        self.parser_page.grid_rowconfigure(0, weight=1)
        
        self.create_grammar_column()
        self.create_controls_column()
        self.create_results_column()
    
    def create_grammar_column(self):
        """Left column: Grammar input area"""
        grammar_frame = ctk.CTkFrame(self.parser_page)
        grammar_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        grammar_label = ctk.CTkLabel(
            grammar_frame,
            text="Grammar Input",
            font=("Arial", 18, "bold")
        )
        grammar_label.pack(pady=10)
        
        instructions = """Enter grammar (one production per line):

Example:
E -> T E'
E' -> + T E'
E' -> e
T -> F T'
T' -> * F T'
T' -> e
F -> ( E )
F -> id

Rules:
- Use '->' arrow
- Space-separated symbols
- Use 'e' for epsilon"""
        
        instructions_label = ctk.CTkLabel(
            grammar_frame,
            text=instructions,
            font=("Courier New", 13),
            justify="left"
        )
        instructions_label.pack(pady=10, padx=10)
        
        self.grammar_textbox = ctk.CTkTextbox(
            grammar_frame,
            font=("Courier New", 14),
            height=300
        )
        self.grammar_textbox.pack(pady=10, padx=10, fill="both", expand=True)
        
        example_grammar = "E -> T E'\nE' -> + T E'\nE' -> e\nT -> F T'\nT' -> * F T'\nT' -> e\nF -> ( E )\nF -> id"
        self.grammar_textbox.insert("1.0", example_grammar)
    
    def create_controls_column(self):
        """Middle column: Input string and control buttons"""
        controls_frame = ctk.CTkFrame(self.parser_page)
        controls_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        controls_label = ctk.CTkLabel(
            controls_frame,
            text="Parser Controls",
            font=("Arial", 18, "bold")
        )
        controls_label.pack(pady=10)
        
        input_label = ctk.CTkLabel(
            controls_frame,
            text="Input String:",
            font=("Arial", 16)
        )
        input_label.pack(pady=5)
        
        self.input_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="id + id * id",
            font=("Courier New", 14),
            width=200
        )
        self.input_entry.pack(pady=5)
        self.input_entry.insert(0, "id + id * id")
        
        buttons_frame = ctk.CTkFrame(controls_frame)
        buttons_frame.pack(pady=20)
        
        first_follow_btn = ctk.CTkButton(
            buttons_frame,
            text="Calculate FIRST/FOLLOW",
            command=self.calculate_first_follow,
            width=180,
            height=35
        )
        first_follow_btn.grid(row=0, column=0, padx=5, pady=5)
        
        table_btn = ctk.CTkButton(
            buttons_frame,
            text="Show Parse Table",
            command=self.show_parse_table,
            width=180,
            height=35
        )
        table_btn.grid(row=1, column=0, padx=5, pady=5)
        
        parse_btn = ctk.CTkButton(
            buttons_frame,
            text="Parse Input",
            command=self.parse_input,
            width=180,
            height=35
        )
        parse_btn.grid(row=2, column=0, padx=5, pady=5)
        
        sim_btn = ctk.CTkButton(
            buttons_frame,
            text="Step-by-Step Simulation",
            command=self.show_simulation,
            width=180,
            height=35,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        sim_btn.grid(row=3, column=0, padx=5, pady=5)
        
        back_btn = ctk.CTkButton(
            controls_frame,
            text="Back to Info",
            command=self.go_back_to_info,
            fg_color="gray30",
            hover_color="gray40",
            height=30
        )
        back_btn.pack(pady=20)
    
    def create_results_column(self):
        """Right column: Results display area"""
        results_frame = ctk.CTkFrame(self.parser_page)
        results_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        results_label = ctk.CTkLabel(
            results_frame,
            text="Results",
            font=("Arial", 18, "bold")
        )
        results_label.pack(pady=10)
        
        self.results_notebook = ctk.CTkTabview(results_frame)
        self.results_notebook.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.results_notebook.add("FIRST/FOLLOW")
        self.results_notebook.add("Parse Table")
        self.results_notebook.add("Parse Tree")
        self.results_notebook.add("Simulation")
        
        self.first_follow_text = ctk.CTkTextbox(
            self.results_notebook.tab("FIRST/FOLLOW"),
            font=("Courier New", 14),
            wrap="none"
        )
        self.first_follow_text.pack(fill="both", expand=True)
        self.first_follow_text.insert("1.0", "FIRST and FOLLOW sets will appear here...")
        self.first_follow_text.configure(state="disabled")
        
        self.parse_table_text = ctk.CTkTextbox(
            self.results_notebook.tab("Parse Table"),
            font=("Courier New", 14),
            wrap="none"
        )
        self.parse_table_text.pack(fill="both", expand=True)
        self.parse_table_text.insert("1.0", "Parse table will appear here...")
        self.parse_table_text.configure(state="disabled")
        
        parse_tree_frame = ctk.CTkFrame(self.results_notebook.tab("Parse Tree"))
        parse_tree_frame.pack(fill="both", expand=True)
        
        self.tree_view_notebook = ctk.CTkTabview(parse_tree_frame)
        self.tree_view_notebook.pack(fill="both", expand=True)
        
        self.tree_view_notebook.add("Graphviz Tree")
        self.tree_view_notebook.add("ASCII Tree")
        
        self.tree_image_label = ctk.CTkLabel(
            self.tree_view_notebook.tab("Graphviz Tree"),
            text="Graphviz tree will appear here...\n\nParse input to generate visualization.",
            font=("Arial", 16)
        )
        self.tree_image_label.pack(expand=True, pady=50)
        
        self.ascii_tree_text = ctk.CTkTextbox(
            self.tree_view_notebook.tab("ASCII Tree"),
            font=("Courier New", 14)
        )
        self.ascii_tree_text.pack(fill="both", expand=True)
        self.ascii_tree_text.insert("1.0", "ASCII tree will appear here...")
        self.ascii_tree_text.configure(state="disabled")
        
        self.simulation_tab = self.results_notebook.tab("Simulation")
        ctk.CTkLabel(
            self.simulation_tab,
            text="Click 'Step-by-Step Simulation' to launch full-screen simulation",
            font=("Arial", 16)
        ).pack(expand=True, pady=50)
    
    def calculate_first_follow(self):
        """Handler for Calculate FIRST/FOLLOW button"""
        try:
            grammar_text = self.grammar_textbox.get("1.0", "end-1c")
            grammar_lines = [line.strip() for line in grammar_text.split('\n') if line.strip()]
            
            from first import first
            from follow import follow
            
            first_sets = first(grammar_lines)
            follow_sets = follow(grammar_lines)
            
            first_table = []
            for nt in sorted(first_sets.keys()):
                first_table.append([nt, ", ".join(sorted(first_sets[nt]))])
            
            follow_table = []
            for nt in sorted(follow_sets.keys()):
                follow_table.append([nt, ", ".join(sorted(follow_sets[nt]))])
            
            result_text = "════════════════════════════════════════════\n"
            result_text += "                 FIRST SETS\n"
            result_text += "════════════════════════════════════════════\n\n"
            result_text += tabulate(first_table, headers=["Non-Terminal", "FIRST Set"], 
                                   tablefmt="grid", stralign="left")
            
            result_text += "\n\n════════════════════════════════════════════\n"
            result_text += "                 FOLLOW SETS\n"
            result_text += "════════════════════════════════════════════\n\n"
            result_text += tabulate(follow_table, headers=["Non-Terminal", "FOLLOW Set"], 
                                   tablefmt="grid", stralign="left")
            
            self.first_follow_text.configure(state="normal")
            self.first_follow_text.delete("1.0", "end")
            self.first_follow_text.insert("1.0", result_text)
            self.first_follow_text.configure(state="disabled")
            self.results_notebook.set("FIRST/FOLLOW")
            
        except Exception as e:
            self.first_follow_text.configure(state="normal")
            self.first_follow_text.delete("1.0", "end")
            self.first_follow_text.insert("1.0", f"Error: {str(e)}\n\nCheck your grammar format.")
            self.first_follow_text.configure(state="disabled")
            self.results_notebook.set("FIRST/FOLLOW")
    
    def show_parse_table(self):
        """Handler for Show Parse Table button"""
        try:
            grammar_text = self.grammar_textbox.get("1.0", "end-1c")
            grammar_lines = [line.strip() for line in grammar_text.split('\n') if line.strip()]
            
            from create_parse_table import create_parse_table
            
            parse_table = create_parse_table(grammar_lines)
            self.last_parse_table = parse_table
            
            terminals = set()
            for nt in parse_table:
                for terminal in parse_table[nt]:
                    if terminal != 'e':
                        terminals.add(terminal)
            
            sorted_terminals = sorted(terminals)
            
            table_data = []
            for nt in sorted(parse_table.keys()):
                row = [nt]
                for terminal in sorted_terminals:
                    production = parse_table[nt].get(terminal)
                    if production:
                        row.append(production)
                    else:
                        row.append("")
                table_data.append(row)
            
            headers = ["NT"] + sorted_terminals
            
            result_text = "═══════════════════════════════════════════════════════\n"
            result_text += "                    LL(1) PARSE TABLE\n"
            result_text += "═══════════════════════════════════════════════════════\n\n"
            result_text += tabulate(table_data, headers=headers, tablefmt="grid", stralign="left")
            
            result_text += "\n\n═══════════════════════════════════════════════════════\n"
            result_text += "                          LEGEND\n"
            result_text += "═══════════════════════════════════════════════════════\n"
            result_text += "• Empty cell = No production for that (NT, Terminal) pair\n"
            result_text += "• NT = Non-Terminal\n"
            
            self.parse_table_text.configure(state="normal")
            self.parse_table_text.delete("1.0", "end")
            self.parse_table_text.insert("1.0", result_text)
            self.parse_table_text.configure(state="disabled")
            self.results_notebook.set("Parse Table")
            
        except Exception as e:
            self.parse_table_text.configure(state="normal")
            self.parse_table_text.delete("1.0", "end")
            self.parse_table_text.insert("1.0", f"Error: {str(e)}\n\nCheck your grammar format.")
            self.parse_table_text.configure(state="disabled")
            self.results_notebook.set("Parse Table")
    
    def parse_input(self):
        """Handler for Parse Input button"""
        try:
            grammar_text = self.grammar_textbox.get("1.0", "end-1c")
            grammar_lines = [line.strip() for line in grammar_text.split('\n') if line.strip()]
            
            input_string = self.input_entry.get()
            
            # Ensure parse table exists for simulation
            if not hasattr(self, 'last_parse_table'):
                from create_parse_table import create_parse_table
                self.last_parse_table = create_parse_table(grammar_lines)
            
            from parse_input import parse_input
            parse_tree, steps = parse_input(grammar_lines, input_string)
            
            if parse_tree is None:
                error_text = "Parse failed! Input cannot be parsed by this grammar."
                self.tree_image_label.configure(text=error_text, font=("Arial", 14))
                
                self.ascii_tree_text.configure(state="normal")
                self.ascii_tree_text.delete("1.0", "end")
                self.ascii_tree_text.insert("1.0", error_text)
                self.ascii_tree_text.configure(state="disabled")
            else:
                try:
                    self.show_graphviz_tree(parse_tree)
                except Exception as graphviz_error:
                    error_msg = f"Graphviz failed: {graphviz_error}\n\nShowing ASCII tree only."
                    self.tree_image_label.configure(text=error_msg, font=("Arial", 13))
                
                from anytree import RenderTree
                ascii_tree_text = "Parse Tree (ASCII):\n\n"
                for pre, fill, node in RenderTree(parse_tree):
                    ascii_tree_text += f"{pre}{node.name}\n"
                
                self.ascii_tree_text.configure(state="normal")
                self.ascii_tree_text.delete("1.0", "end")
                self.ascii_tree_text.insert("1.0", ascii_tree_text)
                self.ascii_tree_text.configure(state="disabled")
                
                self.last_parse_steps = steps
            
            self.results_notebook.set("Parse Tree")
            self.tree_view_notebook.set("Graphviz Tree")
            
        except Exception as e:
            error_text = f"Error: {str(e)}\n\nCheck your grammar and input format."
            self.tree_image_label.configure(text=error_text, font=("Arial", 13))
            
            self.ascii_tree_text.configure(state="normal")
            self.ascii_tree_text.delete("1.0", "end")
            self.ascii_tree_text.insert("1.0", error_text)
            self.ascii_tree_text.configure(state="disabled")
            self.results_notebook.set("Parse Tree")
            self.tree_view_notebook.set("Graphviz Tree")
    
    def show_simulation(self):
        """Create NEW FULL PAGE for simulation"""
        try:
            grammar_text = self.grammar_textbox.get("1.0", "end-1c")
            grammar_lines = [line.strip() for line in grammar_text.split('\n') if line.strip()]
            
            # Ensure parse table exists - create it if not already created
            if not hasattr(self, 'last_parse_table'):
                from create_parse_table import create_parse_table
                self.last_parse_table = create_parse_table(grammar_lines)
            
            if not hasattr(self, 'last_parse_steps'):
                input_string = self.input_entry.get()
                
                from parse_input import parse_input
                parse_tree, steps = parse_input(grammar_lines, input_string)
                
                if parse_tree is None:
                    self.results_notebook.set("Simulation")
                    for widget in self.simulation_tab.winfo_children():
                        widget.destroy()
                    ctk.CTkLabel(
                        self.simulation_tab,
                        text="Parse failed! Cannot create simulation.\n\nParse input first to generate steps.",
                        font=("Arial", 16)
                    ).pack(expand=True, pady=50)
                    return
                
                self.last_parse_steps = steps
            
            self.parser_page.pack_forget()
            
            if not hasattr(self, 'simulation_page'):
                self.create_simulation_page()
            
            for widget in self.simulation_page.winfo_children():
                widget.destroy()
            
            self.create_simulation_page()
            self.simulation_page.pack(fill="both", expand=True)
            
        except Exception as e:
            self.results_notebook.set("Simulation")
            for widget in self.simulation_tab.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.simulation_tab,
                text=f"Error: {str(e)}\n\nParse input first to generate steps.",
                font=("Arial", 14)
            ).pack(expand=True, pady=50)
    
    def create_simulation_page(self):
        """Create full-screen simulation page"""
        self.simulation_page = ctk.CTkFrame(self.window)
        
        title_frame = ctk.CTkFrame(self.simulation_page)
        title_frame.pack(fill="x", padx=10, pady=10)
        
        back_btn = ctk.CTkButton(
            title_frame,
            text="← Back to Parser",
            command=self.back_to_parser_from_simulation,
            width=120,
            height=30
        )
        back_btn.pack(side="left", padx=10)
        
        title_label = ctk.CTkLabel(
          title_frame,
            text="Step-by-Step Parser Simulation",
            font=("Arial", 24, "bold")
        )
        title_label.pack(side="left", padx=20)       
        if hasattr(self, 'last_parse_steps') and self.last_parse_steps:
            # Get parse table, create if it doesn't exist
            if not hasattr(self, 'last_parse_table'):
                grammar_text = self.grammar_textbox.get("1.0", "end-1c")
                grammar_lines = [line.strip() for line in grammar_text.split('\n') if line.strip()]
                from create_parse_table import create_parse_table
                self.last_parse_table = create_parse_table(grammar_lines)
            
            parse_table = self.last_parse_table
            self.simulation_player = ParserSimulationPlayer(
                self.simulation_page,
                self.last_parse_steps,
                parse_table
            )
        else:
            ctk.CTkLabel(
                self.simulation_page,
                text="No parse steps available. Please parse input first.",
                font=("Arial", 16)
            ).pack(expand=True, pady=50)
    
    def back_to_parser_from_simulation(self):
        """Go back from simulation page to parser page"""
        self.simulation_page.pack_forget()
        self.parser_page.pack(fill="both", expand=True)
    
    def show_graphviz_tree(self, parse_tree):
        """Generate and display Graphviz tree visualization"""
        try:
            from graphviz import Digraph
            from anytree import PostOrderIter
            from PIL import Image
            
            dot = Digraph(comment='Parse Tree')
            dot.attr(rankdir='TB')
            dot.attr('node', shape='circle', style='filled', fillcolor='lightblue')
            
            node_ids = {}
            for i, node in enumerate(PostOrderIter(parse_tree)):
                node_id = f"node_{i}"
                node_ids[node] = node_id
                dot.node(node_id, label=node.name)
            
            for node in PostOrderIter(parse_tree):
                if node.parent:
                    dot.edge(node_ids[node.parent], node_ids[node])
            
            png_bytes = dot.pipe(format='png')
            image = Image.open(io.BytesIO(png_bytes))
            
            max_size = (500, 500)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            
            self.tree_image_label.configure(image=ctk_image, text="")
            
        except Exception as e:
            self.tree_image_label.configure(
                text=f"Graphviz error: {str(e)}\n\nMake sure Graphviz is installed.",
                font=("Arial", 13)
            )
    
    def go_back_to_info(self):
        """Handler for Back to Info button"""
        self.parser_page.pack_forget()
        self.info_page.pack(fill="both", expand=True)
    
    def run(self):
        """Start the application event loop"""
        self.window.mainloop()


# Application entry point
if __name__ == "__main__":
    app = LL1ParserGUI()
    app.run()

