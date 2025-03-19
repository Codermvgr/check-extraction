import google.generativeai as genai # type: ignore
from dotenv import load_dotenv
import os
from PIL import Image
import fitz 

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("API key is missing. Please set the GEMINI_API_KEY in the .env file.")

def Model(image):
    genai.configure(api_key=api_key)

    # Choose a Gemini model.
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    prompt = """ You are given a scanned cheque, you need to give me the contents of the cheque in the JSON format like below. Strictly follow JSON format given below and dont add any metadata in the response:
    sample_output_json = {
                        "payee_name": "Deeepak Choudary",
                        "cheque_date" "05-04-2019",
                        "bank_account_number": "35583310826",
                        "bank_name": "State Bank of India",
                        "cheque_number": "2500229009",
                        "amount": "5225000",
                        "ifsc_code": "SBIN0007556"
                    }"""
    openedImage = Image.open(image)
    response = model.generate_content([prompt,  openedImage])
    print(response.text)
    return response.text.replace("\n","").replace("```json", "").replace("```", "")




 # PyMuPDF for PDF handling



# Fetch API key from environment variables
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("API key is missing. Please set the GEMINI_API_KEY in the .env file.")

# Configure Generative AI client
def configure_genai():
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"Failed to configure Generative AI client: {e}")

# Extract text from an image using Gemini API
def extract_text_from_image(image_path):
    """
    Extract information from a scanned cheque image using Gemini API.

    Args:
        image_path (str): Path to the cheque image.

    Returns:
        str: Extracted JSON content.
    """
    configure_genai()

    # Initialize Gemini model
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    
    # Define the prompt
    prompt = """
    You are given a scanned cheque. Extract its contents and provide them in JSON format as shown below:
    {
        "payee_name": "Deepak Choudary",
        "cheque_date": "05-04-2019",
        "bank_account_number": "35583310826",
        "bank_name": "State Bank of India",
        "cheque_number": "2500229009",
        "amount": "5225000",
        "ifsc_code": "SBIN0007556"
    }
    """

    # Open the image file
    try:
        with Image.open(image_path) as opened_image:
            response = model.generate_content([prompt, opened_image])
            return response.text.replace("\n", "").replace("```json", "").replace("```", "").strip()
    except Exception as e:
        raise RuntimeError(f"Failed to process the image: {e}")

# Extract text from a PDF using Gemini API
def extract_text_from_pdf(pdf_path):
    """
    Extract information from a PDF cheque using Gemini API.

    Args:
        pdf_path (str): Path to the cheque PDF.

    Returns:
        str: Extracted JSON content.
    """
    configure_genai()

    # Initialize Gemini model
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    # Define the prompt
    prompt = """
    You are given a cheque in PDF format. Extract its contents and provide them in JSON format as shown below:
    {
        "payee_name": "Deepak Choudary",
        "cheque_date": "05-04-2019",
        "bank_account_number": "35583310826",
        "bank_name": "State Bank of India",
        "cheque_number": "2500229009",
        "amount": "5225000",
        "ifsc_code": "SBIN0007556"
    }
    """

    try:
        # Open the PDF and extract text
        with fitz.open(pdf_path) as pdf:
            extracted_text = ""
            for page in pdf:
                extracted_text += page.get_text()

            # Pass extracted text to the model
            response = model.generate_content([prompt, extracted_text])
            return response.text.replace("\n", "").replace("```json", "").replace("```", "").strip()
    except Exception as e:
        raise RuntimeError(f"Failed to process the PDF: {e}")

# Combined function to handle both image and PDF
def extract_cheque_data(file_path):
    """
    Determine file type and extract cheque data accordingly.

    Args:
        file_path (str): Path to the cheque file (image or PDF).

    Returns:
        str: Extracted JSON content.
    """
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        return extract_text_from_image(file_path)
    elif file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload an image or PDF.")
