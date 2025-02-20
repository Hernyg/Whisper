import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import whisper

# Global variables
mp3_files = []      # List of selected MP3 file paths
model = None        # Whisper model (to be loaded)
output_folder = None  # User-selected output folder

def update_status(message):
    """Update the status label."""
    status_label.config(text=message) 
    root.update_idletasks()

def load_whisper_model():
    """Load the Whisper model and update the status."""
    global model
    update_status("Loading Whisper model (this may take a while)...")
    try:
        model = whisper.load_model("small")
        update_status("Model loaded. Ready to transcribe!")
    except Exception as e:
        update_status(f"Error loading model: {e}")

def upload_mp3():
    """Open a file dialog to select MP3 files."""
    global mp3_files
    files = filedialog.askopenfilenames(
        title="Select MP3 Files",
        filetypes=[("MP3 Files", "*.mp3")]
    )
    if files:
        mp3_files = list(files)
        listbox.delete(0, tk.END)
        for file in mp3_files:
            listbox.insert(tk.END, os.path.basename(file))
        update_status(f"{len(mp3_files)} file(s) selected.")

def select_output_location():
    """Open a dialog to select the output folder."""
    global output_folder
    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        output_folder = folder
        output_folder_label.config(text=f"Output Folder: {output_folder}")

def transcribe_files():
    """Transcribe each selected MP3 file and save the transcription as a text file."""
    if not mp3_files:
        messagebox.showwarning("No files", "Please upload at least one MP3 file.")
        return

    # Disable buttons during processing
    upload_button.config(state=tk.DISABLED)
    transcribe_button.config(state=tk.DISABLED)
    output_folder_button.config(state=tk.DISABLED)

    for file_path in mp3_files:
        filename = os.path.basename(file_path)
        update_status(f"Transcribing {filename}...")
        try:
            # Use Whisper to transcribe the file
            result = model.transcribe(file_path)
            transcript = result.get("text", "").strip()

            # Determine output file path based on selected output folder
            base_name, _ = os.path.splitext(filename)
            if output_folder:
                output_file = os.path.join(output_folder, base_name + ".txt")
            else:
                # If no folder selected, use same directory as the MP3 file
                base_path = os.path.dirname(file_path)
                output_file = os.path.join(base_path, base_name + ".txt")

            # Save the transcription to the output file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(transcript)

            update_status(f"Saved transcription for {filename} to {os.path.basename(output_file)}")
        except Exception as e:
            update_status(f"Error transcribing {filename}: {e}")

    update_status("All files processed.")

    # Re-enable buttons when done
    upload_button.config(state=tk.NORMAL)
    transcribe_button.config(state=tk.NORMAL)
    output_folder_button.config(state=tk.NORMAL)

def start_transcription():
    """Start the transcription process in a separate thread."""
    if model is None:
        messagebox.showwarning("Model not loaded", "Please wait until the model is loaded.")
        return
    threading.Thread(target=transcribe_files, daemon=True).start()

# ----------------- GUI Setup ----------------- #
root = tk.Tk()
root.title("Whisper MP3 Transcriber")
root.geometry("500x450")

# Button to upload MP3 files
upload_button = ttk.Button(root, text="Upload MP3(s)", command=upload_mp3)
upload_button.pack(pady=10)

# Listbox to display selected MP3 filenames
listbox = tk.Listbox(root, width=60, height=10)
listbox.pack(pady=5)

# Button and label for selecting output folder
output_folder_button = ttk.Button(root, text="Select Output Folder", command=select_output_location)
output_folder_button.pack(pady=5)

output_folder_label = ttk.Label(root, text="Output Folder: Not selected")
output_folder_label.pack(pady=5)

# Button to start transcription
transcribe_button = ttk.Button(root, text="Transcribe", command=start_transcription)
transcribe_button.pack(pady=10)

# Status label at the bottom of the window
status_label = ttk.Label(root, text="Initializing...", relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(fill=tk.X, pady=5, side=tk.BOTTOM)

# Load the Whisper model in a separate thread so the GUI remains responsive
threading.Thread(target=load_whisper_model, daemon=True).start()

root.mainloop()
