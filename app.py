import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

def upload_and_process_pdf(file_path: str = "rulebook.pdf"):
    print(f"Uploading '{file_path}' directly to Gemini...")
    # Upload the PDF file directly to Google's file service
    uploaded_file = client.files.upload(file=file_path)
    print(f"File uploaded. Processing pages (URI: {uploaded_file.name})...")

    # Wait for Google to process the document
    while uploaded_file.state.name == "PROCESSING":
        time.sleep(3)
        uploaded_file = client.files.get(name=uploaded_file.name)

    if uploaded_file.state.name == "FAILED":
        raise ValueError("Failed to process the PDF document.")

    print("Rulebook successfully indexed and ready!\n")
    return uploaded_file

def ask_ref_bot(uploaded_file, scenario: str):
    prompt = f"""
You are an expert high school sports official and rules interpreter.
Adjudicate the following game scenario strictly based on the attached NFHS Basketball Rules Book PDF.

--- GAME SCENARIO ---
{scenario}

Provide a structured official ruling:
1. Ruling: Clear call (Violation, Common Foul, Technical Foul, Legal Play, etc.).
2. Applicable Rule & Citation: The exact Rule and Section numbers, and the specific text/article from the book.
3. Official Mechanic & Next Step: Exact whistle, arm signal, spot of throw-in, or free-throw administration.
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=[uploaded_file, prompt],
    )
    return response.text

if __name__ == "__main__":
    if not os.path.exists("rulebook.pdf"):
        print("Error: 'rulebook.pdf' not found in the root directory.")
        exit(1)

    pdf_doc = upload_and_process_pdf("rulebook.pdf")
    print("--- Sports Rulebook Assistant (Full Book) Ready ---")

    while True:
        scenario = input("\nDescribe scenario (or type 'quit' to exit): ")
        if scenario.lower() in ["quit", "exit"]:
            break
        print("\nSearching the scanned rulebook and analyzing call...\n")
        print(ask_ref_bot(pdf_doc, scenario))