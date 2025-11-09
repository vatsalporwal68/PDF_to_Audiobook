import pyttsx3
import PyPDF2
from tkinter import Tk, Label, Button, filedialog, ttk, StringVar, OptionMenu
import pygame
import os

def select_pdf():
    """Open a dialog to select a PDF file."""
    pdf_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )
    if pdf_path:
        selected_file.set(f"Selected: {pdf_path.split('/')[-1]}")
        file_path.set(pdf_path)
        convert_button.config(state="normal")
    else:
        status.set("No file selected!")

def convert_pdf_to_audio():
    """Convert the selected PDF to an audiobook."""
    pdf_path = file_path.get()
    if not pdf_path:
        status.set("No PDF selected!")
        return

    try:
        status.set("Processing...")

        # Extract text from PDF
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if not text.strip():
            raise ValueError("No readable text found in the PDF.")

        # Initialize text-to-speech engine
        engine = pyttsx3.init()

        # Set voice
        voices = engine.getProperty('voices')
        selected_voice = voice_option.get()
        for voice in voices:
            if voice.name == selected_voice:
                engine.setProperty('voice', voice.id)
                break

        # Set speed
        speed = speed_option.get()
        engine.setProperty('rate', int(speed))

        # Save audiobook
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("Audio files", "*.mp3")],
        )
        if output_path:
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            audio_file.set(output_path)
            play_button.config(state="normal")
            status.set(f"Audiobook saved to: {output_path}")
        else:
            status.set("Save operation canceled.")

    except Exception as e:
        status.set(f"Error: {e}")

def play_audio():
    """Play the audiobook."""
    if not audio_file.get():
        status.set("No audiobook to play!")
        return
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    pygame.mixer.music.load(audio_file.get())
    pygame.mixer.music.play()
    play_button.config(state="disabled")
    pause_button.config(state="normal")
    status.set("Playing audio...")

def pause_audio():
    """Pause the audiobook."""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        play_button.config(state="normal")
        pause_button.config(state="disabled")
        status.set("Audio paused.")

def resume_audio():
    """Resume the audiobook."""
    if pygame.mixer.music.get_init():
        pygame.mixer.music.unpause()
        play_button.config(state="disabled")
        pause_button.config(state="normal")
        status.set("Resumed audio.")

def skip_forward():
    """Skip 10 seconds forward."""
    if pygame.mixer.music.get_init():
        pos = pygame.mixer.music.get_pos() / 1000 + 10  # Current position + 10 seconds
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=pos)
        status.set("Skipped forward 10 seconds.")

def skip_backward():
    """Skip 10 seconds backward."""
    if pygame.mixer.music.get_init():
        pos = max(0, pygame.mixer.music.get_pos() / 1000 - 10)  # Current position - 10 seconds
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=pos)
        status.set("Skipped backward 10 seconds.")

root = Tk()
root.title("PDF to Audiobook Converter")
root.geometry("500x500")

# Variables
file_path = StringVar()
audio_file = StringVar()
selected_file = StringVar()
status = StringVar(value="Status: Waiting for input...")
voice_option = StringVar()
speed_option = StringVar(value="150")

# UI Elements
Label(root, text="PDF to Audiobook Converter", font=("Arial", 16, "bold")).pack(pady=10)
Label(root, textvariable=selected_file, font=("Arial", 10)).pack()

Button(root, text="Select PDF", command=select_pdf).pack(pady=5)

Label(root, text="Voice Type:", font=("Arial", 12)).pack(pady=5)
voice_menu = OptionMenu(root, voice_option, *[voice.name for voice in pyttsx3.init().getProperty('voices')])
voice_menu.pack()

Label(root, text="Speed (Words per Minute):", font=("Arial", 12)).pack(pady=5)
speed_menu = ttk.Combobox(root, textvariable=speed_option, values=[100, 150, 200, 250, 300])
speed_menu.pack()

convert_button = Button(root, text="Convert to Audiobook", state="disabled", command=convert_pdf_to_audio)
convert_button.pack(pady=10)

play_button = Button(root, text="Play", state="disabled", command=play_audio)
play_button.pack(pady=5)

pause_button = Button(root, text="Pause", state="disabled", command=pause_audio)
pause_button.pack(pady=5)

skip_forward_button = Button(root, text="Skip Forward 10s", state="disabled", command=skip_forward)
skip_forward_button.pack(pady=5)

skip_backward_button = Button(root, text="Skip Backward 10s", state="disabled", command=skip_backward)
skip_backward_button.pack(pady=5)

Label(root, textvariable=status, font=("Arial", 10, "italic"), fg="blue").pack(pady=10)

# Initialize pygame
pygame.mixer.init()

root.mainloop()
