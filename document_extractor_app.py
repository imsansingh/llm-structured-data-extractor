from dotenv import load_dotenv 
load_dotenv()

import os
import streamlit as st
import google.generativeai as genai
import json

# Import our custom processors (now pure business logic)
import pdf_processor
import excel_processor

# 🔑 Configure Google Gemini strictly from environment variable
_genai_key = os.getenv("GOOGLE_API_KEY")
if not _genai_key:
	st.error("GOOGLE_API_KEY is not set. Add it to .env or environment variables.")
	raise SystemExit

genai.configure(api_key=_genai_key)

# ===== SHARED AI PROCESSING FUNCTION =====
def extract_with_gemini(text: str, document_type: str = "document"):
	model = genai.GenerativeModel("gemini-1.5-flash")
	prompt = f"""
	You are an AI assistant that extracts essential structured data from business documents.

	Extract the key information from the following {document_type} and return ONLY valid JSON.
	
	JSON Structure:
	{{
		"document_info": {{
			"document_type": "string or null",
			"document_number": "string or null",
			"date": "string or null",
			"due_date": "string or null",
			"currency": "string or null"
		}},
		"vendor_info": {{
			"company_name": "string or null",
			"address": "string or null",
			"phone": "string or null",
			"email": "string or null",
			"tax_id": "string or null"
		}},
		"customer_info": {{
			"company_name": "string or null",
			"address": "string or null",
			"phone": "string or null",
			"email": "string or null"
		}},
		"line_items": [
			{{
				"description": "string or null",
				"quantity": "float or null",
				"unit_price": "float or null",
				"total_price": "float or null"
			}}
		],
		"totals": {{
			"subtotal": "float or null",
			"tax_amount": "float or null",
			"total_amount": "float or null"
		}},
        Also extract if there is other data present in the excel related to the business like shipping address, delivery date etc. Only include this data in the json if it is present in the document.

	}}
	
	Don't include itmes in json whose value is null.
	
	{document_type.capitalize()} data to analyze:
	{text}
	"""
	response = model.generate_content(prompt)
	raw_text = response.text.strip()

	# Clean markdown fences like ```json ... ```
	if raw_text.startswith("```"):
		raw_text = raw_text.strip("`")
		# remove leading 'json' if present
		if raw_text.lower().startswith("json"):
			raw_text = raw_text[4:].strip()

	try:
		return json.loads(raw_text)
	except Exception as e:
		return {"error": f"Failed to parse JSON: {e}", "raw": raw_text}

# ===== UI HELPER FUNCTIONS =====
def handle_processing_result(result, file_type="files"):
	"""Handle the structured result from processors and display UI messages"""
	if not result['success']:
		# Display errors
		for error in result['errors']:
			st.error(error)
		return False
	
	# Display success message
	st.success(f"✅ Processed {result['total_files']} {file_type} successfully!")
	
	# Show file discovery info
	if result['total_files'] > 0:
		st.info(f"Found and processed {result['total_files']} {file_type}")
	
	# Display results table
	if result['results']:
		st.subheader("Processing Results:")
		st.table(result['results'])
		
		# Update output folder paths based on user changes
		if "pdf" in file_type.lower():
			st.info(f"JSON files saved in: {os.path.abspath('json_output_pdf')}")
		elif "excel" in file_type.lower():
			st.info(f"JSON files saved in: {os.path.abspath('json_output_excel')}")
		else:
			st.info(f"JSON files saved in: {os.path.abspath('json output')}")
	
	# Display any non-critical errors
	if result['errors']:
		st.warning("Some files had issues:")
		for error in result['errors']:
			st.warning(f"⚠️ {error}")
	
	return True

def process_with_progress(processor_func, *args, file_type="files"):
	"""Run a processor function with progress tracking"""
	# Create progress bar and status placeholders
	progress_bar = st.progress(0)
	status_text = st.empty()
	
	# Set initial status
	status_text.text(f"Starting {file_type} processing...")
	
	try:
		# Run the processor
		result = processor_func(*args)
		
		# Update progress to complete
		progress_bar.progress(1.0)
		status_text.text(f"Processing complete!")
		
		# Handle the result
		return handle_processing_result(result, file_type)
		
	except Exception as e:
		progress_bar.progress(1.0)
		status_text.text("")
		st.error(f"Error during processing: {str(e)}")
		return False

# ===== STREAMLIT UI =====
st.set_page_config(page_title="Document → JSON Extractor", layout="wide")

st.title("🗂️ Business Document Extractor using LLM (Gemini)")
st.markdown("**Supports:** PDF files, Excel spreadsheets (.xlsx, .xls)")

# Create main tabs for different document types
main_tab1, main_tab2 = st.tabs(["📄 PDF Processing", "📊 Excel Processing"])

# ===== PDF PROCESSING TAB =====
with main_tab1:
	st.header("PDF Document Processing")
	
	# Create sub-tabs for different processing modes
	pdf_tab1, pdf_tab2 = st.tabs(["Single File", "Bulk Processing"])
	
	with pdf_tab1:
		st.subheader("Single PDF File Processing")
		uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], key="pdf_single")

		if uploaded_file:
			with st.spinner("Reading PDF..."):
				try:
					text = pdf_processor.extract_text_from_pdf(uploaded_file)
				except Exception as e:
					st.error(f"Error reading PDF: {str(e)}")
					text = ""

			if text.strip():
				with st.spinner("Extracting with Gemini AI..."):
					records = extract_with_gemini(text, "PDF document")

					st.success("✅ Extracted JSON")
					st.json(records)
			else:
				st.error("No readable text found in PDF.")
		else:
			st.info("👆 Please upload a PDF file to extract data.")

	with pdf_tab2:
		st.subheader("Bulk PDF Processing")
		st.info("Process multiple PDF files and create JSON output files in a 'json_output_pdf' folder.")
		
		# Create two options for input
		option = st.radio(
			"Choose how to provide PDF files:",
			["📁 Enter Folder Path", "📦 Upload Zip File"],
			horizontal=True,
			key="pdf_bulk_option"
		)
		
		if option == "📁 Enter Folder Path":
			st.subheader("Option 1: Folder Path")
			folder_path = st.text_input("Enter folder path containing PDF files:", 
										placeholder="e.g., C:\\pdf extract2\\pdfs", 
										key="pdf_folder_path")
			
			if st.button("Process PDF Folder", key="process_pdf_folder"):
				if folder_path and os.path.exists(folder_path):
					with st.spinner("Processing all PDFs in folder..."):
						process_with_progress(
							pdf_processor.process_pdf_folder,
							folder_path, 
							extract_with_gemini,
							file_type="PDF files"
						)
				elif folder_path:
					st.error("Folder path does not exist. Please check the path.")
				else:
					st.warning("Please enter a folder path.")
		
		else:  # Upload Zip File option
			st.subheader("Option 2: Upload Zip File")
			st.info("📦 Upload a zip file containing PDF files. The zip can contain PDFs in subdirectories.")
			
			uploaded_zip = st.file_uploader("Choose a zip file", type=["zip"], key="pdf_zip_uploader")
			
			if st.button("Process Zip File", key="process_pdf_zip"):
				if uploaded_zip is not None:
					with st.spinner("Processing all PDFs from zip file..."):
						process_with_progress(
							pdf_processor.process_zip_file,
							uploaded_zip,
							extract_with_gemini,
							file_type="PDF files"
						)
				else:
					st.warning("Please upload a zip file.")

# ===== EXCEL PROCESSING TAB =====
with main_tab2:
	st.header("Excel Spreadsheet Processing")
	
	# Create sub-tabs for different processing modes
	excel_tab1, excel_tab2 = st.tabs(["Single File", "Bulk Processing"])
	
	with excel_tab1:
		st.subheader("Single Excel File Processing")
		uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"], key="excel_single")

		if uploaded_file:
			with st.spinner("Reading Excel file..."):
				try:
					text = excel_processor.extract_text_from_excel(uploaded_file)
				except Exception as e:
					st.error(f"Error reading Excel file: {str(e)}")
					text = ""

			if text.strip():
				with st.spinner("Extracting with Gemini AI..."):
					records = extract_with_gemini(text, "Excel spreadsheet")

					st.success("✅ Extracted JSON")
					st.json(records)
			else:
				st.error("No readable data found in Excel file.")
		else:
			st.info("👆 Please upload an Excel file to extract data.")

	with excel_tab2:
		st.subheader("Bulk Excel Processing")
		st.info("Process multiple Excel files and create JSON output files in a 'json_output_excel' folder.")
		
		# Create two options for input
		excel_option = st.radio(
			"Choose how to provide Excel files:",
			["📁 Enter Folder Path", "📦 Upload Zip File"],
			horizontal=True,
			key="excel_bulk_option"
		)
		
		if excel_option == "📁 Enter Folder Path":
			st.subheader("Option 1: Folder Path")
			folder_path = st.text_input("Enter folder path containing Excel files:", 
										placeholder="e.g., C:\\pdf extract2\\excel_files", 
										key="excel_folder_path")
			
			if st.button("Process Excel Folder", key="process_excel_folder"):
				if folder_path and os.path.exists(folder_path):
					with st.spinner("Processing all Excel files in folder..."):
						process_with_progress(
							excel_processor.process_excel_folder,
							folder_path,
							extract_with_gemini,
							file_type="Excel files"
						)
				elif folder_path:
					st.error("Folder path does not exist. Please check the path.")
				else:
					st.warning("Please enter a folder path.")
		
		else:  # Upload Zip File option
			st.subheader("Option 2: Upload Zip File")
			st.info("📦 Upload a zip file containing Excel files. The zip can contain Excel files in subdirectories.")
			
			uploaded_excel_zip = st.file_uploader("Choose a zip file", type=["zip"], key="excel_zip_uploader")
			
			if st.button("Process Zip File", key="process_excel_zip"):
				if uploaded_excel_zip is not None:
					with st.spinner("Processing all Excel files from zip file..."):
						process_with_progress(
							excel_processor.process_excel_zip_file,
							uploaded_excel_zip,
							extract_with_gemini,
							file_type="Excel files"
						)
				else:
					st.warning("Please upload a zip file.")