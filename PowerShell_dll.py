import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import clr
from threading import Thread
import re
import pyperclip
import sys
import ctypes

# Add reference to PowerShell assembly
dll_path = r"C:\WINDOWS\Microsoft.Net\assembly\GAC_MSIL\System.Management.Automation\v4.0_3.0.0.0__31bf3856ad364e35\System.Management.Automation.dll"
clr.AddReference(dll_path)

from System.Management.Automation import PowerShell
from System.Management.Automation.Runspaces import RunspaceFactory


class PowerShellIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("PowerShell IDE")
        self.root.geometry("1200x800")


        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, 'powershell_folder_icon_250656.ico')


        try:
            self.root.iconbitmap(icon_path)  # Set the icon for the window
        except Exception as e:
            print(f"Error setting window icon: {e}")


        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)



        # Modern color scheme
        self.colors = {
            'background': '#2c3e50',  # Dark blue-gray
            'foreground': '#ecf0f1',  # Light gray
            'accent': '#3498db',      # Bright blue
            'toolbar': '#34495e',     # Slightly lighter dark blue-gray
            'editor': '#2980b9',      # Deeper blue
            'console': '#2c3e50',     # Same as background
        }


        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme as a base for customization


        style.configure("TFrame", background=self.colors['background'])
        style.configure("TLabel",
            background=self.colors['background'],
            foreground=self.colors['foreground'],
            font=('Segoe UI', 10)
        )
        style.configure("TButton",
            background=self.colors['accent'],
            foreground='white',
            font=('Segoe UI', 10, 'bold')
        )
        style.map('TButton',
            background=[('active', '#2980b9'), ('pressed', '#3498db')]
        )

        self.setup_menu()
        self.setup_toolbar()
        self.setup_editor()
        self.setup_console()


        self.current_file = None
        self.is_modified = False
        self.script_editor.edit_modified(False)
        self.script_editor.bind('<<Modified>>', self.on_text_modified)

        # Set up keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.save_ps1_file())
        self.root.bind('<Control-o>', lambda e: self.open_ps1_file())
        self.root.bind('<F5>', lambda e: self.run_powershell_script())

        # Configure syntax highlighting
        self.setup_syntax_highlighting()

        # Configure root window style
        self.root.configure(bg=self.colors['background'])



    def setup_menu(self):
        self.menu_bar = tk.Menu(
            self.root,
            bg=self.colors['toolbar'],
            fg=self.colors['foreground'],
            activebackground=self.colors['accent']
        )
        self.root.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors['toolbar'], fg=self.colors['foreground'])
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open...", command=self.open_ps1_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_ps1_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As...", command=self.save_as_ps1_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_closing)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors['toolbar'], fg=self.colors['foreground'])
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=lambda: self.script_editor.edit_undo(), accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=lambda: self.script_editor.edit_redo(), accelerator="Ctrl+Y")

        self.run_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors['toolbar'], fg=self.colors['foreground'])
        self.menu_bar.add_cascade(label="Run", menu=self.run_menu)
        self.run_menu.add_command(label="Run Script", command=self.run_powershell_script, accelerator="F5")

    def setup_toolbar(self):
        self.toolbar = ttk.Frame(self.root, style="TFrame")
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

        self.run_button = ttk.Button(
            self.toolbar,
            text="Run Script (F5)",
            command=self.run_powershell_script
        )
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_button = ttk.Button(
            self.toolbar,
            text="Stop Execution",
            command=self.stop_script,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.status_label = ttk.Label(
            self.toolbar,
            text="Ready",
            font=('Segoe UI', 10, 'italic')
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)

    def setup_editor(self):
        self.paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Script Editor Frame
        editor_frame = ttk.Frame(self.paned)
        self.paned.add(editor_frame, weight=3)

        self.script_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            undo=True,
            font=('Consolas', 10),
            bg=self.colors['editor'],
            fg=self.colors['foreground'],
            insertbackground=self.colors['foreground'],  # Cursor color
            selectbackground=self.colors['accent']
        )
        self.script_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_console(self):
        # Console Frame
        console_frame = ttk.Frame(self.paned)
        self.paned.add(console_frame, weight=1)

        # Add console toolbar
        console_toolbar = ttk.Frame(console_frame)
        console_toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Add Clear and Copy buttons
        self.clear_button = ttk.Button(
            console_toolbar,
            text="Clear Output",
            command=self.clear_console
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.copy_button = ttk.Button(
            console_toolbar,
            text="Copy Output",
            command=self.copy_console
        )
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.console = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            height=10,
            font=('Consolas', 10),
            bg=self.colors['console'],
            fg=self.colors['foreground'],
            insertbackground=self.colors['foreground']
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.console.config(state=tk.DISABLED)

    def setup_syntax_highlighting(self):
        self.keywords = [
            'function', 'if', 'else', 'elseif', 'switch', 'while', 'for',
            'foreach', 'return', 'filter', 'in', 'where', 'throw', 'param',
            'begin', 'process', 'end', 'try', 'catch', 'finally', 'trap'
        ]

        # Configure syntax highlighting colors
        self.script_editor.tag_configure('keyword', foreground='#e74c3c')  # Bright red for keywords
        self.script_editor.tag_configure('string', foreground='#2ecc71')   # Green for strings
        self.script_editor.tag_configure('comment', foreground='#95a5a6')  # Gray for comments

        self.script_editor.bind('<KeyRelease>', self.highlight_syntax)
    def highlight_syntax(self, event=None):
        for tag in ['keyword', 'string', 'comment']:
            self.script_editor.tag_remove(tag, '1.0', tk.END)

        content = self.script_editor.get('1.0', tk.END)

        for keyword in self.keywords:
            start = '1.0'
            while True:
                start = self.script_editor.search(r'\b' + keyword + r'\b', start, tk.END, regexp=True)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                self.script_editor.tag_add('keyword', start, end)
                start = end

        # Highlight strings (basic implementation)
        start = '1.0'
        while True:
            start = self.script_editor.search(r'"[^"]*"', start, tk.END, regexp=True)
            if not start:
                break
            content = self.script_editor.get(start, tk.END)
            match = re.match(r'"[^"]*"', content)
            if match:
                end = f"{start}+{len(match.group(0))}c"
                self.script_editor.tag_add('string', start, end)
                start = end
            else:
                break

        # Highlight comments
        start = '1.0'
        while True:
            start = self.script_editor.search('#', start, tk.END)
            if not start:
                break
            line_end = self.script_editor.search('\n', start, tk.END)
            if not line_end:
                line_end = tk.END
            self.script_editor.tag_add('comment', start, line_end)
            start = line_end
    def highlight_syntax(self, event=None):
        for tag in ['keyword', 'string', 'comment']:
            self.script_editor.tag_remove(tag, '1.0', tk.END)

        content = self.script_editor.get('1.0', tk.END)

        for keyword in self.keywords:
            start = '1.0'
            while True:
                start = self.script_editor.search(r'\b' + keyword + r'\b', start, tk.END, regexp=True)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                self.script_editor.tag_add('keyword', start, end)
                start = end

        start = '1.0'
        while True:
            start = self.script_editor.search(r'"[^"]*"', start, tk.END, regexp=True)
            if not start:
                break
            content = self.script_editor.get(start, tk.END)
            match = re.match(r'"[^"]*"', content)
            if match:
                end = f"{start}+{len(match.group(0))}c"
                self.script_editor.tag_add('string', start, end)
                start = end
            else:
                break

        start = '1.0'
        while True:
            start = self.script_editor.search('#', start, tk.END)
            if not start:
                break
            line_end = self.script_editor.search('\n', start, tk.END)
            if not line_end:
                line_end = tk.END
            self.script_editor.tag_add('comment', start, line_end)
            start = line_end

    def new_file(self):
        if self.check_unsaved_changes():
            self.script_editor.delete(1.0, tk.END)
            self.current_file = None
            self.is_modified = False
            self.root.title("PowerShell IDE - New Script")

    def open_ps1_file(self):
        if self.check_unsaved_changes():
            file_path = filedialog.askopenfilename(
                defaultextension=".ps1",
                filetypes=[("PowerShell Scripts", "*.ps1"), ("All Files", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.script_editor.delete(1.0, tk.END)
                        self.script_editor.insert(tk.END, content)
                        self.current_file = file_path
                        self.is_modified = False
                        self.root.title(f"PowerShell IDE by idan less- {os.path.basename(file_path)}")
                        self.highlight_syntax()
                except Exception as e:
                    messagebox.showerror("File Open Error", str(e))

    def save_ps1_file(self):
        if not self.current_file:
            return self.save_as_ps1_file()
        return self.save_file(self.current_file)

    def save_as_ps1_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ps1",
            filetypes=[("PowerShell Scripts", "*.ps1"), ("All Files", "*.*")]
        )
        if file_path:
            return self.save_file(file_path)
        return False

    def save_file(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                content = self.script_editor.get(1.0, tk.END)
                file.write(content)
            self.current_file = file_path
            self.is_modified = False
            self.root.title(f"PowerShell IDE by idan less- {os.path.basename(file_path)}")
            return True
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            return False

    def run_powershell_script(self):
        self.clear_console()
        script_content = self.script_editor.get(1.0, tk.END).strip()
        if not script_content:
            messagebox.showwarning("Warning", "No PowerShell script to run")
            return

        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.console.delete(1.0, tk.END)

        self.execution_thread = Thread(target=self.execute_script, args=(script_content,))
        self.execution_thread.start()

    def execute_script(self, script_content):
        try:
            self.root.after(0, lambda: self.status_label.config(text="Running..."))

            runspace = RunspaceFactory.CreateRunspace()
            runspace.Open()

            ps = PowerShell.Create()
            ps.Runspace = runspace

            try:
                ps.AddScript(script_content)

                results = ps.Invoke()

                self.update_console("=== Script Execution Results ===\n")
                if results and len(results) > 0:
                    for result in results:
                        if result is not None:
                            try:
                                result_str = str(result.ToString())
                            except Exception as e:
                                result_str = str(e)
                            self.update_console(f"{result_str}\n")
                else:
                    self.update_console("Script executed successfully but returned no output.\n")

                if ps.HadErrors:
                    self.update_console("\n=== Script Errors ===\n", "error")
                    for error in ps.Streams.Error:
                        self.update_console(f"{str(error)}\n", "error")

            finally:
                ps.Dispose()
                runspace.Close()

        except Exception as e:
            self.update_console(f"Unexpected error: {str(e)}\n", "error")

        finally:
            self.root.after(0, lambda: self.status_label.config(text="Ready"))
            self.root.after(0, lambda: self.run_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))

    def update_console(self, text, tag=None):
        self.root.after(0, lambda: self.console.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.console.insert(tk.END, text))
        if tag == "error":
            last_line_start = self.console.index("end-1c linestart")
            self.root.after(0, lambda: self.console.tag_add("error", last_line_start, tk.END))
            self.root.after(0, lambda: self.console.tag_config("error", foreground="red"))
        self.root.after(0, lambda: self.console.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.console.see(tk.END))

    def stop_script(self):
        if hasattr(self, 'execution_thread') and self.execution_thread.is_alive():

            self.status_label.config(text="Stopping...")


    def on_text_modified(self, event=None):
        if self.script_editor.edit_modified():
            if not self.is_modified:
                self.root.title(self.root.title() + " *")
                self.is_modified = True
            self.script_editor.edit_modified(False)

    def clear_console(self):
        """Clear the console output"""
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.config(state=tk.DISABLED)

    def copy_console(self):
        """Copy console output to clipboard"""
        output_text = self.console.get(1.0, tk.END).strip()
        if output_text:
            pyperclip.copy(output_text)
            self.status_label.config(text="Output copied to clipboard")
            self.root.after(2000, lambda: self.status_label.config(text="Ready"))
        else:
            self.status_label.config(text="No output to copy")
            self.root.after(2000, lambda: self.status_label.config(text="Ready"))

    def check_unsaved_changes(self):
        if self.is_modified:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Do you want to save changes before continuing?"
            )
            if response is None:  # Cancel
                return False
            if response:  # Yes
                return self.save_ps1_file()
        return True

    def on_closing(self):
        if self.check_unsaved_changes():
            self.root.destroy()



def main():
    root = tk.Tk()
    app = PowerShellIDE(root)
    myappid = 'mycompany.myappname'  # Replace with a unique identifier for your app
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
