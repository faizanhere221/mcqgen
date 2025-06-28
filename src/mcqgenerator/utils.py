import os
import PyPDF2
import json
import traceback


def read_file(file):
    """
    Reads the content of a file and returns it as a string.
    Supports both text files and PDF files.
    """
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        except Exception as e:
            raise Exception("Error Reading the PDF File")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception("Unsupported file format. Please upload a .txt or .pdf file.")
    

def get_table_data(quiz_input):
    try:
        # If it's a string, clean it first
        if isinstance(quiz_input, str):
            # Remove any header like "### RESPONSE_JSON"
            quiz_input = quiz_input.strip()
            if quiz_input.startswith("### RESPONSE_JSON"):
                quiz_input = quiz_input.replace("### RESPONSE_JSON", "").strip()

            quiz_dict = json.loads(quiz_input)
        elif isinstance(quiz_input, dict):
            quiz_dict = quiz_input
        else:
            raise ValueError("Invalid quiz format. Must be dict or JSON string.")

        quiz_table_data = []

        # Extract MCQ, options, correct answer
        for key, value in quiz_dict.items():
            mcq = value.get("mcq", "")
            options = " || ".join(
                [f"{option}->{option_value}" for option, option_value in value.get("options", {}).items()]
            )
            correct = value.get("correct", "")

            quiz_table_data.append({
                "MCQ": mcq,
                "Choices": options,
                "Correct": correct
            })

        return quiz_table_data

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return None