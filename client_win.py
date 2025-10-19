import asyncio
import csv
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from telethon import TelegramClient, errors

CONFIG_FILE = "config.json"

# ---------------- Utility ----------------

def log_event(log_box, message):
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)
    log_box.update()

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

# ---------------- Telegram Functions ----------------

async def get_all_groups(client):
    """Fetch all groups (public + private) the user is a member of."""
    groups = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            groups.append(dialog.entity)
    return groups

async def send_messages(client, csv_file, delay, log_box):
    groups = await get_all_groups(client)
    log_event(log_box, f"Found {len(groups)} groups.")
    if not groups:
        log_event(log_box, "⚠️ No groups found.")
        return

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=1):
            message = row.get("message", "").strip()
            image_path = row.get("image", "").strip()

            if not message:
                continue

            for group in groups:
                try:
                    if image_path and os.path.exists(image_path):
                        await client.send_file(group.id, image_path, caption=message, parse_mode="markdown")
                        log_event(log_box, f"📤 Sent image + message to {group.title}")
                    else:
                        await client.send_message(group.id, message, parse_mode="markdown")
                        log_event(log_box, f"📩 Sent message to {group.title}")
                except errors.FloodWaitError as e:
                    log_event(log_box, f"⏸ Flood wait: waiting {e.seconds}s...")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    log_event(log_box, f"❌ Failed to send to {group.title}: {e}")

            # Delay between messages
            if delay > 0:
                for sec in range(delay, 0, -1):
                    log_box.delete("end-2l", tk.END)
                    log_event(log_box, f"⏳ Waiting {sec}s before next CSV line...")
                    await asyncio.sleep(1)

    log_event(log_box, "✅ All messages sent!")

# ---------------- GUI ----------------

class TelegramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Broadcaster (Tkinter Edition)")
        self.root.geometry("600x500")

        self.config = load_config()
        self.csv_file = None

        # Inputs
        tk.Label(root, text="API ID:").pack()
        self.api_id_entry = tk.Entry(root)
        self.api_id_entry.pack(fill="x")
        self.api_id_entry.insert(0, self.config.get("api_id", ""))

        tk.Label(root, text="API Hash:").pack()
        self.api_hash_entry = tk.Entry(root)
        self.api_hash_entry.pack(fill="x")
        self.api_hash_entry.insert(0, self.config.get("api_hash", ""))

        tk.Label(root, text="Phone Number (+CountryCode...):").pack()
        self.phone_entry = tk.Entry(root)
        self.phone_entry.pack(fill="x")
        self.phone_entry.insert(0, self.config.get("phone", ""))

        tk.Label(root, text="Delay between CSV lines (seconds):").pack()
        self.delay_entry = tk.Entry(root)
        self.delay_entry.pack(fill="x")
        self.delay_entry.insert(0, str(self.config.get("delay", 5)))

        tk.Button(root, text="Select CSV File", command=self.select_csv).pack(pady=5)
        tk.Button(root, text="Start", command=self.start).pack(pady=5)

        # Log box
        tk.Label(root, text="Logs:").pack()
        self.log_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
        self.log_box.pack(fill="both", expand=True)

    def select_csv(self):
        self.csv_file = filedialog.askopenfilename(
            title="Select CSV file", filetypes=[("CSV files", "*.csv")]
        )
        if self.csv_file:
            log_event(self.log_box, f"📁 Selected CSV: {self.csv_file}")

    def start(self):
        api_id = self.api_id_entry.get().strip()
        api_hash = self.api_hash_entry.get().strip()
        phone = self.phone_entry.get().strip()
        delay = int(self.delay_entry.get().strip())

        if not (api_id and api_hash and phone and self.csv_file):
            messagebox.showerror("Error", "Please fill in all fields and select a CSV file.")
            return

        self.config.update({"api_id": api_id, "api_hash": api_hash, "phone": phone, "delay": delay})
        save_config(self.config)

        asyncio.run(self.run_bot(api_id, api_hash, phone, delay, self.csv_file))

    async def run_bot(self, api_id, api_hash, phone, delay, csv_file):
        client = TelegramClient("session", api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code = simple_input_dialog("Enter Telegram code sent to your app or SMS:")
            await client.sign_in(phone, code)

        await send_messages(client, csv_file, delay, self.log_box)
        await client.disconnect()

# ---------------- Code Dialog ----------------

def simple_input_dialog(prompt):
    popup = tk.Tk()
    popup.title("Telegram Code")
    tk.Label(popup, text=prompt).pack()
    entry = tk.Entry(popup)
    entry.pack()
    result = []

    def submit():
        result.append(entry.get())
        popup.destroy()

    tk.Button(popup, text="Submit", command=submit).pack()
    popup.mainloop()
    return result[0] if result else ""

# ---------------- Main ----------------

if __name__ == "__main__":
    root = tk.Tk()
    app = TelegramApp(root)
    root.mainloop()
