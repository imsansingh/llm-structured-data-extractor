
📄 Business Document Extractor using LLM (Gemini)
This project provides a Streamlit-based web application for extracting structured data from various business documents, specifically PDFs and Excel spreadsheets (.xlsx, .xls), using the power of the Gemini large language model.

It supports both single-file processing and bulk processing (via folder path or ZIP upload), saving the extracted information into clean JSON files.

✨ Features
🌐 Streamlit Web Interface: A user-friendly, interactive web application.

🧠 LLM-Powered Extraction: Uses Gemini-1.5 Flash for intelligent data extraction.

📄 PDF Processing: Extracts text from PDF files (using pdfplumber).

📊 Excel Processing: Extracts text from Excel files, including sheet names, column headers, and row data (using pandas and openpyxl).

📁 Bulk Processing: Handle multiple files via a folder path or an uploaded ZIP archive containing documents (supports subdirectories).

💾 Structured JSON Output: Extracts data into a standardized JSON schema.


🔒 Secure: Files are processed temporarily and not stored (as noted in the Streamlit app's footer ).

📦 Installation
To set up and run this project locally, follow these steps:

1. Prerequisites
Python (3.9+)

2. Clone the Repository
Bash
git clone <repository-url>
cd document_extractor
3. Set Up Virtual Environment (Recommended)
Bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate  # On Windows
4. Install Dependencies
Install the required libraries listed in requirements.txt:

Bash
pip install -r requirements.txt
The necessary dependencies are python-dotenv, streamlit, google-generativeai, pdfplumber, pandas, and openpyxl.

5. Configure API Key
Create a .env file in the root directory of the project and add your Google AI Studio API key (or set it as an environment variable):

.env

GOOGLE_API_KEY="YOUR_API_KEY_HERE"
The application is configured to use this key via dotenv.

▶️ How to Run the App
Execute the following command in your terminal from the project root directory:

Bash
streamlit run document_extractor_app.py
The app will launch in your web browser, typically at http://localhost:8501.


🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request for improvements, bug fixes, or new features.
