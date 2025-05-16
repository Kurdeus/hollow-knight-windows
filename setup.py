from Crypto.Cipher import AES
import base64
import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
from typing import Dict, Any, Optional
import os
import requests
import base64
import webbrowser


class VersionService:
    def __init__(self):
        self.base_url = "https://api.github.com/repos/Kurdeus/hollow-knight-windows/contents/version"
        self.local_version = "1.0.0"


    def check_version(self):
        
        try:
            response = requests.get(self.base_url, headers={})
            print(response.json())
            response.raise_for_status()
            data = response.json()
            
            # Decode the content from base64
            remote_version = base64.b64decode(data['content']).decode('utf-8').strip()
            
            
            
            # Compare versions (assuming semantic versioning)
            if self._version_comparator(self.local_version, remote_version) < 0:
                return {
                    'update_available': True,
                    'local_version': self.local_version,
                    'remote_version': remote_version
                }
            
            return {'update_available': False}
            
        except Exception as e:
            print(f"Version check failed: {str(e)}")
            return {'update_available': False, 'error': str(e)}
    
    def _version_comparator(self, local_version, remote_version):
        """
        Compare version strings.
        Returns: -1 if local < remote, 0 if equal, 1 if local > remote
        """
        local_parts = [int(x) for x in local_version.split('.')]
        remote_parts = [int(x) for x in remote_version.split('.')]
        
        for i in range(max(len(local_parts), len(remote_parts))):
            local_part = local_parts[i] if i < len(local_parts) else 0
            remote_part = remote_parts[i] if i < len(remote_parts) else 0
            
            if local_part < remote_part:
                return -1
            elif local_part > remote_part:
                return 1
                
        return 0





# Domain Layer: Core business logic for encryption/decryption
class EncryptionService:
    def __init__(self):
        self.c_sharp_header = bytes.fromhex('0001000000FFFFFFFF01000000000000000601000000')
        self.end_header = bytes([11])
        self.aes_key = b'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'
        self.cipher = AES.new(self.aes_key, AES.MODE_ECB)

    def decrypt_data(self, data_as_bytes: bytes) -> Dict[str, Any]:
        decrypted_bytes = self._decode_and_decrypt(data_as_bytes)
        return json.loads(decrypted_bytes.decode('utf-8'))

    def _decode_and_decrypt(self, bytes_: bytes) -> bytes:
        bytes_ = bytes_[len(self.c_sharp_header): len(bytes_) - 1]
        bytes_ = base64.b64decode(bytes_)
        bytes_ = self.cipher.decrypt(bytes_)
        return bytes_[:-bytes_[-1]]

    def encrypt_data(self, data: Dict[str, Any]) -> bytes:
        json_str = json.dumps(data, separators=[',', ':'])
        data_as_bytes = bytes(json_str, encoding='utf-8')
        return self._encrypt_and_encode(data_as_bytes)

    def _encrypt_and_encode(self, bytes_: bytes) -> bytes:
        length = 16 - (len(bytes_) % 16)
        bytes_ += bytes([length]) * length
        bytes_ = self.cipher.encrypt(bytes_)
        bytes_ = base64.b64encode(bytes_)
        bytes_ = self.c_sharp_header + self._c_sharp_length(bytes_) + bytes_ + self.end_header
        return bytes_

    def _c_sharp_length(self, bytes_: bytes) -> bytes:
        bytes_len = len(bytes_)
        values = []
        for i in range(4):
            if bytes_len >> 7 == 0:
                values.append(0x7F & bytes_len)
                bytes_len = bytes_len >> 7
                break
            else:
                values.append(0x7F & bytes_len | 0x80)
                bytes_len = bytes_len >> 7
        if bytes_len != 0:
            values.append(bytes_len)
        return bytes(values)

# Infrastructure Layer: File handling
class FileRepository:
    @staticmethod
    def read_binary_file(file_path: str) -> bytes:
        with open(file_path, 'rb') as binary_file:
            return binary_file.read()

    @staticmethod
    def write_save_file(file_path: str, data: bytes) -> None:
        with open(file_path, 'wb') as f:
            f.write(data)

# Application Layer: Use case handling
class SaveFileUseCase:
    def __init__(self, encryption_service: EncryptionService, file_repository: FileRepository):
        self.encryption_service = encryption_service
        self.file_repository = file_repository

    def load_save_file(self, file_path: str) -> Dict[str, Any]:
        file_data = self.file_repository.read_binary_file(file_path)
        return self.encryption_service.decrypt_data(file_data)

    def save_file(self, file_path: str, data: Dict[str, Any]) -> None:
        encrypted_data = self.encryption_service.encrypt_data(data)
        self.file_repository.write_save_file(file_path, encrypted_data)

# Presentation Layer: UI handling
class HollowKnightEditor:
    def __init__(self, root):
        self.root = root
        self.version_service = VersionService()
        self.root.title(f'Hollow Knight Editor v{self.version_service.local_version}')
        self.root.geometry('900x700')
        self.root.minsize(800, 600)
        
        # Set application icon if available
        if os.path.exists("app.ico"):
            self.root.iconbitmap("app.ico")
        
        self.encryption_service = EncryptionService()
        self.file_repository = FileRepository()
        self.use_case = SaveFileUseCase(self.encryption_service, self.file_repository)
        
        self.current_file: Optional[str] = None
        self.json_data: Optional[Dict[str, Any]] = None
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TButton', padding=6, relief="flat", background="#ccc")
        self.style.configure('TFrame', background="#f0f0f0")
        self.style.configure('TLabel', background="#f0f0f0", font=('Helvetica', 10))
        self.style.configure('StatusBar.TLabel', background="#e0e0e0", padding=3)
        
        self.create_menu()
        self.create_ui()
        
        # Check for updates when application starts
        self.check_for_updates()
        

    def show_help_message(self):
        help_text = """How to Use the Hollow Knight Save Editor:

1. Backup First: Always create a backup of your save file to prevent data loss.
2. Open Save File: Click the "Open Save File" button to load your save file.
3. Edit Data: Browse through the data (health, geo, etc.) and modify as needed.
4. Save Changes: Use "Save Changes" to overwrite the original file, or "Save As" to create a new file.
5. Enjoy: Load your game and enjoy the changes you've made!

Save File Locations:
- PC: %USERPROFILE%\\AppData\\LocalLow\\Team Cherry\\Hollow Knight\\
- Android: /Android/data/com.TeamCherry.HollowKnight/files/
"""
        messagebox.showinfo("How to Use", help_text)

    def check_for_updates(self):
        version_info = self.version_service.check_version()
        if version_info.get('update_available', False):
            result = messagebox.askquestion(
                'Update Available',
                f"A new version is available!\n\n"
                f"Current version: {version_info.get('local_version')}\n"
                f"New version: {version_info.get('remote_version')}\n\n"
                f"Would you like to download the latest version?",
                icon='info'
            )
            if result == 'yes':
                webbrowser.open("https://github.com/Kurdeus/hollow-knight-windows/releases")

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_changes, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="How to Use", command=self.show_help_message)
        help_menu.add_command(label="Check for Updates", command=self.check_for_updates)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda event: self.open_file())
        self.root.bind('<Control-s>', lambda event: self.save_changes())
        self.root.bind('<Control-Shift-S>', lambda event: self.save_as())

    def create_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Toolbar frame
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Toolbar buttons with icons (if available)
        self.open_button = ttk.Button(toolbar_frame, text='Open Save File', command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=2)
        
        self.save_button = ttk.Button(toolbar_frame, text='Save Changes', command=self.save_changes, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=2)
        
        self.save_as_button = ttk.Button(toolbar_frame, text='Save As', command=self.save_as, state=tk.DISABLED)
        self.save_as_button.pack(side=tk.LEFT, padx=2)
        
        self.help_button = ttk.Button(toolbar_frame, text='How to Use', command=self.show_help_message)
        self.help_button.pack(side=tk.LEFT, padx=2)
        
        self.update_button = ttk.Button(toolbar_frame, text='Check for Updates', command=self.check_for_updates)
        self.update_button.pack(side=tk.RIGHT, padx=2)
        
        # Editor area
        editor_frame = ttk.Frame(main_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text editor with syntax highlighting
        self.text_edit = scrolledtext.ScrolledText(
            editor_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 11),
            state=tk.DISABLED,
            background="#ffffff",
            foreground="#000000",
            insertbackground="#000000",
            selectbackground="#c0c0c0",
            padx=5,
            pady=5
        )
        self.text_edit.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.file_label = ttk.Label(
            self.status_frame, 
            text='No file loaded', 
            anchor='w',
            style='StatusBar.TLabel'
        )
        self.file_label.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title='Open Save File',
            filetypes=[('Hollow Knight Save Files', '*.dat'), ('All Files', '*.*')]
        )
        
        if file_path:
            try:
                self.current_file = file_path
                self.json_data = self.use_case.load_save_file(file_path)
                
                formatted_json = json.dumps(self.json_data, indent=4)
                
                self.text_edit.config(state=tk.NORMAL)
                self.text_edit.delete(1.0, tk.END)
                self.text_edit.insert(tk.END, formatted_json)
                
                self.file_label.config(text=f'Editing: {os.path.basename(file_path)}')
                self.save_button.config(state=tk.NORMAL)
                self.save_as_button.config(state=tk.NORMAL)
                
                # Set window title to include filename
                self.root.title(f'Hollow Knight Editor - {os.path.basename(file_path)}')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to open file: {str(e)}')
    
    def save_changes(self):
        if not self.current_file or not self.text_edit.get(1.0, tk.END).strip():
            return
            
        try:
            edited_json = json.loads(self.text_edit.get(1.0, tk.END))
            self.use_case.save_file(self.current_file, edited_json)
            messagebox.showinfo('Success', 'Save file updated successfully!')
        except json.JSONDecodeError:
            messagebox.showerror('Error', 'Invalid JSON format. Please check your edits.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save file: {str(e)}')
    
    def save_as(self):
        if not self.text_edit.get(1.0, tk.END).strip():
            return
            
        file_path = filedialog.asksaveasfilename(
            title='Save As',
            filetypes=[('Hollow Knight Save Files', '*.dat'), ('All Files', '*.*')],
            defaultextension='.dat'
        )
        
        if file_path:
            try:
                edited_json = json.loads(self.text_edit.get(1.0, tk.END))
                self.use_case.save_file(file_path, edited_json)
                self.current_file = file_path
                self.file_label.config(text=f'Editing: {os.path.basename(file_path)}')
                self.root.title(f'Hollow Knight Editor - {os.path.basename(file_path)}')
                messagebox.showinfo('Success', 'Save file created successfully!')
            except json.JSONDecodeError:
                messagebox.showerror('Error', 'Invalid JSON format. Please check your edits.')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save file: {str(e)}')
    
   
    def show_about(self):
        about_text = 'Hollow Knight Save Editor\n\n' \
                     'A tool for editing Hollow Knight save files.\n' \
                     'Version 1.0\n\n' \
                     'For updates, visit:'
        
        about_window = tk.Toplevel(self.root)
        about_window.title('About Hollow Knight Editor')
        about_window.geometry('400x200')
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        
        frame = ttk.Frame(about_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=about_text, justify=tk.CENTER).pack(pady=10)
        url = "https://github.com/Kurdeus/hollow-knight-windows/releases"
        link = ttk.Label(frame, text=url, 
                         foreground="blue", cursor="hand2")
        link.pack(pady=5)
        link.bind("<Button-1>", lambda e: webbrowser.open(url))
        
        ttk.Button(frame, text="Close", command=about_window.destroy).pack(pady=10)

if __name__ == '__main__':
    root = tk.Tk()
    editor = HollowKnightEditor(root)
    root.mainloop()