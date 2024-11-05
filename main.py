# main.py

import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import pyperclip
from utils import load_key, init_db, create_user, authenticate_user, add_credential, get_credentials, get_decrypted_credential

print("Starting Password Vault Application...")

# Load encryption key and initialize database
key = load_key()
init_db()

# Set up the dark theme with a custom color theme
ctk.set_appearance_mode("Dark")  # Dark mode
ctk.set_default_color_theme("dark-blue")  # You can adjust to other themes if needed

# Main application window
class PasswordVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Vault Hub")
        self.geometry("900x550")
        self.resizable(False, False)  # Disable window resizing

        # Set up the main container with a split layout
        self.configure_grid()

        # Load the login screen by default
        self.show_login_screen()

    def configure_grid(self):
        # Configure a 2-column grid layout to mimic the split design
        self.grid_columnconfigure(0, weight=1, uniform="column")
        self.grid_columnconfigure(1, weight=1, uniform="column")
        
        # Left Panel for Form (Glossy, Rounded)
        self.left_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#2b2b2b")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Right Panel for Image / Design element (Glossy Background)
        self.right_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1f1f1f")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)

    def show_login_screen(self):
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        label_title = ctk.CTkLabel(self.left_frame, text="Welcome Back!", font=("Helvetica Neue", 28, "bold"), text_color="#ffffff")
        label_title.pack(pady=(30, 10))

        label_subtitle = ctk.CTkLabel(self.left_frame, text="Enter your info to Sign In", font=("Helvetica Neue", 14), text_color="#a9a9a9")
        label_subtitle.pack(pady=(0, 20))

        self.entry_email = ctk.CTkEntry(self.left_frame, placeholder_text="Email", width=300, height=40, corner_radius=10, fg_color="#333333", text_color="#ffffff")
        self.entry_email.pack(pady=10)

        self.entry_password = ctk.CTkEntry(self.left_frame, placeholder_text="Password", show="*", width=300, height=40, corner_radius=10, fg_color="#333333", text_color="#ffffff")
        self.entry_password.pack(pady=10)

        self.button_login = ctk.CTkButton(self.left_frame, text="Sign In", command=self.login, width=200, height=40, corner_radius=20, fg_color="#007acc", hover_color="#005f99", font=("Helvetica Neue", 14, "bold"))
        self.button_login.pack(pady=(20, 10))

        self.button_create_account = ctk.CTkButton(self.left_frame, text="Create Account", command=self.show_create_account_screen, fg_color="#444444", text_color="white", corner_radius=20, width=200, font=("Helvetica Neue", 12))
        self.button_create_account.pack(pady=(10, 20))

    def show_create_account_screen(self):
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        label_title = ctk.CTkLabel(self.left_frame, text="Create Account", font=("Helvetica Neue", 28, "bold"), text_color="#ffffff")
        label_title.pack(pady=(30, 10))

        label_subtitle = ctk.CTkLabel(self.left_frame, text="Fill in your info to Register", font=("Helvetica Neue", 14), text_color="#a9a9a9")
        label_subtitle.pack(pady=(0, 20))

        self.entry_email = ctk.CTkEntry(self.left_frame, placeholder_text="Email", width=300, height=40, corner_radius=10, fg_color="#333333", text_color="#ffffff")
        self.entry_email.pack(pady=10)

        self.entry_password = ctk.CTkEntry(self.left_frame, placeholder_text="Password", show="*", width=300, height=40, corner_radius=10, fg_color="#333333", text_color="#ffffff")
        self.entry_password.pack(pady=10)

        self.button_register = ctk.CTkButton(self.left_frame, text="Register", command=self.create_account, width=200, height=40, corner_radius=20, fg_color="#007acc", hover_color="#005f99", font=("Helvetica Neue", 14, "bold"))
        self.button_register.pack(pady=(20, 10))

        self.button_back = ctk.CTkButton(self.left_frame, text="Back to Login", command=self.show_login_screen, fg_color="#444444", text_color="white", corner_radius=20, width=200, font=("Helvetica Neue", 12))
        self.button_back.pack(pady=(10, 20))

    def create_account(self):
        email = self.entry_email.get()
        password = self.entry_password.get()

        if not email or not password:
            messagebox.showwarning("Warning", "Please fill in both email and password.")
            return

        if create_user(email, password):
            messagebox.showinfo("Success", "Account created! Please log in.")
            self.show_login_screen()
        else:
            messagebox.showerror("Error", "Email already exists.")

    def login(self):
        email = self.entry_email.get()
        password = self.entry_password.get()

        if authenticate_user(email, password):
            self.current_user_id = self.get_user_id(email)
            self.show_vault_screen()
        else:
            messagebox.showerror("Error", "Invalid email or password.")

    def get_user_id(self, email):
        conn = sqlite3.connect("vault.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            return None  # Return None if no user ID is found

    def show_vault_screen(self):
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        label_vault_title = ctk.CTkLabel(self.left_frame, text="Your Password Vault", font=("Helvetica Neue", 24, "bold"), text_color="white")
        label_vault_title.pack(pady=(30, 10))

        self.entry_name = ctk.CTkEntry(self.left_frame, placeholder_text="Service Name", width=300)
        self.entry_name.pack(pady=(10, 5))

        self.entry_username = ctk.CTkEntry(self.left_frame, placeholder_text="Username", width=300)
        self.entry_username.pack(pady=(10, 5))

        self.entry_password = ctk.CTkEntry(self.left_frame, placeholder_text="Password / API Key", width=300)
        self.entry_password.pack(pady=(10, 5))

        self.button_add = ctk.CTkButton(self.left_frame, text="Add Credential", command=self.add_credential, width=200)
        self.button_add.pack(pady=(20, 10))

        credentials_label = ctk.CTkLabel(self.left_frame, text="Saved Credentials", font=("Helvetica Neue", 16, "bold"), text_color="white")
        credentials_label.pack(pady=(20, 10))

        self.credentials_frame = ctk.CTkFrame(self.left_frame)
        self.credentials_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.display_credentials()

    def display_credentials(self):
        # Clear any existing widgets in the credentials frame
        for widget in self.credentials_frame.winfo_children():
            widget.destroy()

        # Fetch credentials for the logged-in user
        credentials = get_credentials(self.current_user_id, key)

        # Calculate the width of the buttons based on the frame width
        button_width = self.credentials_frame.winfo_width() - 40  # Adjust width to fit and center within frame

        # Display only the name of each credential, centered within the credentials frame
        for cred_id, name, username, password in credentials:
            credential_button = ctk.CTkButton(
                self.credentials_frame, 
                text=name, 
                command=lambda cid=cred_id: self.show_credential_details(cid),
                fg_color="gray30",  # Button color
                width=button_width,  # Set button width to dynamically calculated width
                corner_radius=10,  # Slight rounding for a modern look
                font=("Helvetica Neue", 14)  # Font style for the button
            )
            # Center the button horizontally within the credentials frame
            credential_button.pack(pady=5)
            credential_button.pack_configure(anchor="center")  # Center within the credentials frame

    def show_credential_details(self, cred_id):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        credential = get_decrypted_credential(cred_id, key)
        
        if credential:
            name, username, password = credential
            details_title = ctk.CTkLabel(self.right_frame, text="Credential Details", font=("Helvetica Neue", 20, "bold"))
            details_title.pack(pady=(30, 10))

            label_name = ctk.CTkLabel(self.right_frame, text=f"Service Name: {name}", font=("Helvetica Neue", 14))
            label_name.pack(pady=(10, 5))

            label_username = ctk.CTkLabel(self.right_frame, text=f"Username: {username}", font=("Helvetica Neue", 14))
            label_username.pack(pady=(10, 5))

            copy_button = ctk.CTkButton(self.right_frame, text="Copy Password", command=lambda: self.copy_to_clipboard(password), width=100)
            copy_button.pack(pady=(10, 5))

            label_password = ctk.CTkLabel(self.right_frame, text=f"Password/API Key: {password[:30]}...", font=("Helvetica Neue", 14))
            label_password.pack(pady=(10, 5))
            label_password.bind("<Enter>", lambda e, pw=password: self.show_tooltip(e, pw))
            label_password.bind("<Leave>", self.hide_tooltip)

    def add_credential(self):
        name = self.entry_name.get()
        username = self.entry_username.get()
        password = self.entry_password.get()

        if name and password:
            add_credential(self.current_user_id, name, username, password, key)
            self.display_credentials()
            messagebox.showinfo("Success", "Credential added successfully!")
            self.entry_name.delete(0, 'end')
            self.entry_username.delete(0, 'end')
            self.entry_password.delete(0, 'end')
        else:
            messagebox.showwarning("Warning", "Please fill in the required fields.")

    def copy_to_clipboard(self, text):
        pyperclip.copy(text)
        messagebox.showinfo("Copied", "Password copied to clipboard.")

    def show_tooltip(self, event, text):
        self.tooltip = ctk.CTkLabel(self.right_frame, text=text, font=("Helvetica Neue", 10), fg_color="white", bg_color="black")
        self.tooltip.place(x=event.x_root - self.right_frame.winfo_rootx(), y=event.y_root - self.right_frame.winfo_rooty())

    def hide_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

# Run the application
if __name__ == "__main__":
    app = PasswordVaultApp()
    app.mainloop()
