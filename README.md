# Infosys Internship - Bank Check Extraction

## Overview
This project is a **Bank Check Extraction** system developed during the Infosys Internship. It utilizes **OCR (Optical Character Recognition)** and **Machine Learning** to extract key details from bank checks. The application is deployed using **Streamlit**, providing an easy-to-use web interface.

### Live Demo
Check out the live version here: [Bank Check Extraction](https://bank-check-extraction.streamlit.app/)

## Features
- **OCR-Based Text Extraction:** Extracts text from bank checks with high accuracy.
- **Field Recognition:** Identifies and extracts essential fields such as account number, date, payee name, amount, and signature.
- **Automated Processing:** Reduces manual effort in check processing.
- **User-Friendly Interface:** Built using **Streamlit** for ease of use.
- **Supports Multiple Check Formats:** Works with different bank check layouts.

## Tech Stack
- **Frontend:** Streamlit (Python-based UI framework)
- **Backend:** Python, OpenCV, Tesseract OCR
- **Libraries Used:**
  - OpenCV (Image Processing)
  - Tesseract OCR (Text Extraction)
  - Pandas, NumPy (Data Handling)
- **Deployment:** Streamlit Cloud

## Installation
To run the project locally, follow these steps:

### Prerequisites
- Python (>=3.8)
- pip (Python Package Manager)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/bank-check-extraction.git
   cd bank-check-extraction
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
5. Open the application in your browser:
   ```
   http://localhost:8501/
   ```

## How It Works
1. Upload an image of a bank check.
2. The system processes the image and extracts relevant details.
3. Extracted details are displayed in a structured format.
4. Users can download the extracted information for further use.

## Demo Video
Watch the project in action:

[![Bank Check Extraction Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

## Contributing
Contributions are welcome! If you want to enhance this project:
1. Fork the repository.
2. Create a new branch (`feature-branch`).
3. Commit your changes and push to GitHub.
4. Submit a Pull Request (PR).

## License
This project is licensed under the MIT License.

## Contact
For any queries, reach out at: [gullipallinagabhushan@example.com] or visit the project repository: [GitHub Repo](https://github.com/Codermvgr/check-extraction)

Happy coding! 🚀


