import pyttsx3
from PyPDF4 import PdfFileReader
import speech_recognition as sr
import threading
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import ttk
import re

window = Tk()
window.title("AudiobookAI")
window.geometry('600x600')
v = IntVar()
v.set(0)
stop_flag = threading.Event()

def clear_text(textbox):
    textbox.delete(1.0, END)

def stop_speech():
    stop_flag.set()

def text_to_speech(text):
    speaker = pyttsx3.init()
    rate = speaker.getProperty('rate')
    speaker.setProperty('rate', rate - 50)
    voices = speaker.getProperty('voices')
    speaker.setProperty('voice', voices[v.get()].id)
    
    text_parts = re.split(r'([.!?])', text)
    for part in text_parts:
        if stop_flag.is_set():
            break
        if part.strip():  
            speaker.say(part)
            speaker.runAndWait()
    speaker.stop()

def process_pdf():
    file_location = askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_location:
        book = open(file_location, 'rb')
        pdfReader = PdfFileReader(book, strict=False)
        total_pages = pdfReader.numPages
        plabel.config(text="Total pages: " + str(total_pages))
        p1 = int(first_page_entry.get())
        p2 = int(last_page_entry.get())
        extracted_text = ""
        for x in range(p1-1, p2):
            page = pdfReader.getPage(x)
            text = page.extractText()
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'(\w)([.,!?])', r'\1\2', text)
            extracted_text += text
            textboxp.delete(1.0, END)
            textboxp.insert(1.0, extracted_text)
        output_text.delete(1.0, END)
        output_text.insert(INSERT, extracted_text)
        stop_flag.clear()
        threading.Thread(target=text_to_speech, args=(extracted_text,)).start()  

def convert_audio_to_text():
    sound = askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3")])
    if sound:
        r = sr.Recognizer()
        with sr.AudioFile(sound) as source:
            r.adjust_for_ambient_noise(source)
            print("Converting Audio To Text ...")
            audio = r.listen(source)
        try:
            result = r.recognize_google(audio)
            print("Converted Audio Is:\n", result)
            output_text.delete(1.0, END)
            output_text.insert(INSERT, result)
        except Exception as e:
            print("Error:", e)

tab_control = ttk.Notebook(window)
tab1 = Frame(tab_control)
tab2 = Frame(tab_control)
tab3 = Frame(tab_control)
tab4 = Frame(tab_control)

tab_control.add(tab1, text='Text')
tab_control.add(tab2, text='PDF')
tab_control.add(tab3, text='Settings')
tab_control.add(tab4, text='Audio to Text')

label_text = Label(tab1, text="Enter text to convert to speech:", font=("Arial", 14))
label_text.grid(row=0, column=0, padx=10, pady=10)

textbox = Text(tab1, height=10, width=60)
textbox.grid(row=1, column=0, padx=10, pady=10)

convert_button = Button(tab1, text="Convert to Speech", command=lambda: threading.Thread(target=text_to_speech, args=(textbox.get(1.0, END),)).start())
convert_button.grid(row=2, column=0, padx=10, pady=10)

clear_button = Button(tab1, text="Clear", command=lambda: clear_text(textbox))
clear_button.grid(row=3, column=0, padx=10, pady=10)

label_pdf = Label(tab2, text="Select a PDF file to process:", font=("Arial", 14))
label_pdf.grid(row=0, column=0, padx=10, pady=10)

open_pdf_button = Button(tab2, text="Open PDF", command=process_pdf)
open_pdf_button.grid(row=1, column=0, padx=10, pady=10)

first_page_label = Label(tab2, text="First Page:")
first_page_label.grid(row=2, column=0, padx=10, pady=10)
first_page_entry = Entry(tab2, width=10)
first_page_entry.grid(row=2, column=1, padx=10, pady=10)

last_page_label = Label(tab2, text="Last Page:")
last_page_label.grid(row=2, column=2, padx=10, pady=10)
last_page_entry = Entry(tab2, width=10)
last_page_entry.grid(row=2, column=3, padx=10, pady=10)

convert_pdf_button = Button(tab2, text="Convert PDF to Speech", command=process_pdf)
convert_pdf_button.grid(row=2, column=4, padx=10, pady=10)

stop_button = Button(tab2, text="Stop", command=stop_speech)
stop_button.grid(row=3, column=0, padx=10, pady=10)

plabel = Label(tab2, text="", font=("Arial", 12))
plabel.grid(row=4, column=0, columnspan=5)

textboxp = Text(tab2, height=10, width=60)
textboxp.grid(row=5, column=0, columnspan=5, padx=10, pady=10)

label_settings = Label(tab3, text="Adjust Voice and Rate Settings:", font=("Arial", 14))
label_settings.grid(row=0, column=0, padx=10, pady=10)

range_label = Label(tab3, text="Rate:")
range_label.grid(row=1, column=0, padx=10, pady=5)

range1 = Scale(tab3, from_=-200, to=200, orient=HORIZONTAL)
range1.grid(row=1, column=1, padx=10, pady=5)

voice_label = Label(tab3, text="Voice:")
voice_label.grid(row=2, column=0, padx=10, pady=5)

voice_male = Radiobutton(tab3, text="Male", variable=v, value=0)
voice_male.grid(row=2, column=1, padx=10, pady=5)

voice_female = Radiobutton(tab3, text="Female", variable=v, value=1)
voice_female.grid(row=2, column=2, padx=10, pady=5)

label_audio = Label(tab4, text="Select an audio file for conversion:", font=("Arial", 14))
label_audio.grid(row=0, column=0, padx=10, pady=10)

convert_audio_button = Button(tab4, text="Convert to Text", command=convert_audio_to_text)
convert_audio_button.grid(row=1, column=0, padx=10, pady=10)

output_text = Text(window, height=10, width=60)
output_text.pack(pady=10)

tab_control.pack(expand=1, fill='both')
window.mainloop()
