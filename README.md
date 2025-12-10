
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
# venv\Scripts\activate  # On Windows
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

⚙️ Extracted JSON Structure
The Gemini model is prompted to extract data into the following standardized JSON format, excluding any fields whose value is null:

JSON
{
	"document_info": {
		"document_type": "string or null",
		"document_number": "string or null",
		"date": "string or null",
		"due_date": "string or null",
		"currency": "string or null"
	},
	"vendor_info": {
		"company_name": "string or null",
		"address": "string or null",
		"phone": "string or null",
		"email": "string or null",
		"tax_id": "string or null"
	},
	"customer_info": {
		"company_name": "string or null",
		"address": "string or null",
		"phone": "string or null",
		"email": "string or null"
	},
	"line_items": [
		{
			"description": "string or null",
			"quantity": "float or null",
			"unit_price": "float or null",
			"total_price": "float or null"
		}
	],
	"totals": {
		"subtotal": "float or null",
		"tax_amount": "float or null",
		"total_amount": "float or null"
	},
    // Optional: other business data like shipping address, delivery date, etc.
}
💡 Core Logic Overview
The application is structured into the following main components:

document_extractor_app.py (Streamlit UI & Orchestration):

Sets up the Streamlit interface, including tabs for PDF and Excel processing.

Handles file uploads and user input for bulk processing options.

Defines extract_with_gemini(text, document_type) to construct the LLM prompt and handle the JSON response.

Calls the appropriate processor functions (pdf_processor.py or excel_processor.py).

pdf_processor.py:


extract_text_from_pdf(pdf_file): Uses pdfplumber to extract all text from an uploaded file object.


extract_text_from_pdf_path(pdf_path): Extracts text from a file located at a local path.


process_pdf_folder(): Finds and processes all .pdf files in a given folder path, saving results to json_output_pdf.


process_zip_file(): Extracts PDF files from an uploaded ZIP into a temporary directory and processes them.

excel_processor.py:


extract_text_from_excel(excel_file) / extract_text_from_excel_path(excel_path): Uses pandas with the openpyxl engine to read all sheets and formats the data (including column names and row values) into a single, readable text string for the LLM.


process_excel_folder(): Processes all .xlsx and .xls files in a folder, saving results to json_output_excel.


process_excel_zip_file(): Handles bulk processing from an uploaded ZIP archive.

🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request for improvements, bug fixes, or new features.
