import os
import pdfplumber
import json
import glob
import zipfile
import tempfile
from pathlib import Path

def extract_text_from_pdf(pdf_file):
	"""Extract text from uploaded PDF file object"""
	text = ""
	try:
		pdf_file.seek(0)
	except Exception:
		pass
	with pdfplumber.open(pdf_file) as pdf:
		for page in pdf.pages:
			text += page.extract_text() or ""
	return text

def extract_text_from_pdf_path(pdf_path):
	"""Extract text from PDF file using file path"""
	text = ""
	try:
		with pdfplumber.open(pdf_path) as pdf:
			for page in pdf.pages:
				text += page.extract_text() or ""
		return text
	except Exception as e:
		raise Exception(f"Error reading PDF {pdf_path}: {str(e)}")

def process_pdf_folder(folder_path, extract_with_gemini_func):
	"""
	Process all PDFs in a folder and create JSON output files
	
	"""
	# Create output directory
	output_dir = Path("json_output_pdf")
	output_dir.mkdir(exist_ok=True)
	
	# Find all PDF files in the folder
	pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
	
	if not pdf_files:
		return {
			'success': False,
			'results': [],
			'errors': [f"No PDF files found in folder: {folder_path}"],
			'total_files': 0,
			'files_found': []
		}
	
	# Process each PDF
	results = []
	errors = []
	
	for i, pdf_path in enumerate(pdf_files):
		pdf_name = Path(pdf_path).stem  # Get filename without extension
		
		try:
			# Extract text from PDF
			text = extract_text_from_pdf_path(pdf_path)
			
			if text.strip():
				# Extract JSON data using Gemini
				json_data = extract_with_gemini_func(text, "PDF document")
				
				# Save JSON file
				json_filename = f"{pdf_name}.json"
				json_path = output_dir / json_filename
				
				try:
					with open(json_path, 'w', encoding='utf-8') as f:
						json.dump(json_data, f, indent=2, ensure_ascii=False)
					
					results.append({
						"file_name": pdf_name + ".pdf",
						"json_file": json_filename,
						"status": "✅ Success"
					})
				except Exception as e:
					error_msg = f"Error saving JSON for {pdf_name}.pdf: {str(e)}"
					errors.append(error_msg)
					results.append({
						"file_name": pdf_name + ".pdf", 
						"json_file": json_filename,
						"status": f"❌ Error: {str(e)}"
					})
			else:
				results.append({
					"file_name": pdf_name + ".pdf",
					"json_file": "N/A",
					"status": "❌ No text found"
				})
		except Exception as e:
			error_msg = f"Error processing {pdf_name}.pdf: {str(e)}"
			errors.append(error_msg)
			results.append({
				"file_name": pdf_name + ".pdf",
				"json_file": "N/A",
				"status": f"❌ Error: {str(e)}"
			})
	
	return {
		'success': len(errors) == 0,
		'results': results,
		'errors': errors,
		'total_files': len(pdf_files),
		'files_found': pdf_files
	}

def process_zip_file(uploaded_zip, extract_with_gemini_func):
	# Process all PDFs in an uploaded zip file and create JSON output files

	# Create output directory
	output_dir = Path("json_output_pdf")
	output_dir.mkdir(exist_ok=True)
	
	# Create temporary directory for extracting zip
	with tempfile.TemporaryDirectory() as temp_dir:
		try:
			# Save uploaded zip file to temp location
			temp_zip_path = os.path.join(temp_dir, "uploaded.zip")
			with open(temp_zip_path, "wb") as f:
				f.write(uploaded_zip.getvalue())
			
			# Extract zip file
			with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
				zip_ref.extractall(temp_dir)
			
			# Find all PDF files in extracted content (including subdirectories)
			pdf_files = []
			for root, dirs, files in os.walk(temp_dir):
				for file in files:
					if file.lower().endswith('.pdf'):
						pdf_files.append(os.path.join(root, file))
			
			if not pdf_files:
				return {
					'success': False,
					'results': [],
					'errors': ["No PDF files found in the uploaded zip file."],
					'total_files': 0,
					'files_found': []
				}
			
			# Process each PDF
			results = []
			errors = []
			file_names = [Path(f).name for f in pdf_files]
			
			for i, pdf_path in enumerate(pdf_files):
				pdf_name = Path(pdf_path).stem  # Get filename without extension
				
				try:
					# Extract text from PDF
					text = extract_text_from_pdf_path(pdf_path)
					
					if text.strip():
						# Extract JSON data using Gemini
						json_data = extract_with_gemini_func(text, "PDF document")
						
						# Save JSON file
						json_filename = f"{pdf_name}.json"
						json_path = output_dir / json_filename
						
						try:
							with open(json_path, 'w', encoding='utf-8') as f:
								json.dump(json_data, f, indent=2, ensure_ascii=False)
							
							results.append({
								"file_name": pdf_name + ".pdf",
								"json_file": json_filename,
								"status": "✅ Success"
							})
						except Exception as e:
							error_msg = f"Error saving JSON for {pdf_name}.pdf: {str(e)}"
							errors.append(error_msg)
							results.append({
								"file_name": pdf_name + ".pdf", 
								"json_file": json_filename,
								"status": f"❌ Error: {str(e)}"
							})
					else:
						results.append({
							"file_name": pdf_name + ".pdf",
							"json_file": "N/A",
							"status": "❌ No text found"
						})
				except Exception as e:
					error_msg = f"Error processing {pdf_name}.pdf: {str(e)}"
					errors.append(error_msg)
					results.append({
						"file_name": pdf_name + ".pdf",
						"json_file": "N/A",
						"status": f"❌ Error: {str(e)}"
					})
			
			return {
				'success': len(errors) == 0,
				'results': results,
				'errors': errors,
				'total_files': len(pdf_files),
				'files_found': file_names
			}
			
		except zipfile.BadZipFile:
			return {
				'success': False,
				'results': [],
				'errors': ["Invalid zip file. Please upload a valid zip archive."],
				'total_files': 0,
				'files_found': []
			}
		except Exception as e:
			return {
				'success': False,
				'results': [],
				'errors': [f"Error processing zip file: {str(e)}"],
				'total_files': 0,
				'files_found': []
			} 