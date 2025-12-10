import os
import pandas as pd
import json
import glob
import zipfile
import tempfile
from pathlib import Path
import openpyxl

def extract_text_from_excel(excel_file):
	"""Extract text from uploaded Excel file object"""
	try:
		# Reset file pointer if possible
		try:
			excel_file.seek(0)
		except Exception:
			pass
		
		# Read all sheets from the Excel file
		xl_data = pd.read_excel(excel_file, sheet_name=None, engine='openpyxl')
		
		text_content = ""
		for sheet_name, df in xl_data.items():
			text_content += f"\n=== SHEET: {sheet_name} ===\n"
			
			# Convert DataFrame to a readable text format
			# Include column headers
			if not df.empty:
				# Add column headers
				text_content += "COLUMNS: " + " | ".join(str(col) for col in df.columns) + "\n"
				
				# Add each row
				for index, row in df.iterrows():
					row_text = " | ".join(str(val) if pd.notna(val) else "" for val in row.values)
					text_content += f"ROW {index + 1}: {row_text}\n"
			else:
				text_content += "EMPTY SHEET\n"
		
		return text_content
	except Exception as e:
		raise Exception(f"Error reading Excel file: {str(e)}")

def extract_text_from_excel_path(excel_path):
	"""Extract text from Excel file using file path"""
	try:
		# Read all sheets from the Excel file
		xl_data = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
		
		text_content = ""
		for sheet_name, df in xl_data.items():
			text_content += f"\n=== SHEET: {sheet_name} ===\n"
			
			# Convert DataFrame to a readable text format
			# Include column headers
			if not df.empty:
				# Add column headers
				text_content += "COLUMNS: " + " | ".join(str(col) for col in df.columns) + "\n"
				
				# Add each row
				for index, row in df.iterrows():
					row_text = " | ".join(str(val) if pd.notna(val) else "" for val in row.values)
					text_content += f"ROW {index + 1}: {row_text}\n"
			else:
				text_content += "EMPTY SHEET\n"
		
		return text_content
	except Exception as e:
		raise Exception(f"Error reading Excel file {excel_path}: {str(e)}")

def process_excel_folder(folder_path, extract_with_gemini_func):
	"""
	Process all Excel files in a folder and create JSON output files
	
	"""
	# Create output directory
	output_dir = Path("json_output_excel")
	output_dir.mkdir(exist_ok=True)
	
	# Find all Excel files in the folder
	excel_files = glob.glob(os.path.join(folder_path, "*.xlsx")) + glob.glob(os.path.join(folder_path, "*.xls"))
	
	if not excel_files:
		return {
			'success': False,
			'results': [],
			'errors': [f"No Excel files found in folder: {folder_path}"],
			'total_files': 0,
			'files_found': []
		}
	
	# Process each Excel file
	results = []
	errors = []
	
	for i, excel_path in enumerate(excel_files):
		excel_name = Path(excel_path).stem  # Get filename without extension
		
		try:
			# Extract text from Excel
			text = extract_text_from_excel_path(excel_path)
			
			if text.strip():
				# Extract JSON data using Gemini
				json_data = extract_with_gemini_func(text, "Excel spreadsheet")
				
				# Save JSON file
				json_filename = f"{excel_name}.json"
				json_path = output_dir / json_filename
				
				try:
					with open(json_path, 'w', encoding='utf-8') as f:
						json.dump(json_data, f, indent=2, ensure_ascii=False)
					
					results.append({
						"file_name": excel_name + Path(excel_path).suffix,
						"json_file": json_filename,
						"status": "✅ Success"
					})
				except Exception as e:
					error_msg = f"Error saving JSON for {excel_name}: {str(e)}"
					errors.append(error_msg)
					results.append({
						"file_name": excel_name + Path(excel_path).suffix, 
						"json_file": json_filename,
						"status": f"❌ Error: {str(e)}"
					})
			else:
				results.append({
					"file_name": excel_name + Path(excel_path).suffix,
					"json_file": "N/A",
					"status": "❌ No data found"
				})
		except Exception as e:
			error_msg = f"Error processing {excel_name}: {str(e)}"
			errors.append(error_msg)
			results.append({
				"file_name": excel_name + Path(excel_path).suffix,
				"json_file": "N/A",
				"status": f"❌ Error: {str(e)}"
			})
	
	return {
		'success': len(errors) == 0,
		'results': results,
		'errors': errors,
		'total_files': len(excel_files),
		'files_found': excel_files
	}

def process_excel_zip_file(uploaded_zip, extract_with_gemini_func):
	"""
	Process all Excel files in an uploaded zip file and create JSON output files
	
	"""
	# Create output directory
	output_dir = Path("json_output_excel")
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
			
			# Find all Excel files in extracted content (including subdirectories)
			excel_files = []
			for root, dirs, files in os.walk(temp_dir):
				for file in files:
					if file.lower().endswith(('.xlsx', '.xls')):
						excel_files.append(os.path.join(root, file))
			
			if not excel_files:
				return {
					'success': False,
					'results': [],
					'errors': ["No Excel files found in the uploaded zip file."],
					'total_files': 0,
					'files_found': []
				}
			
			# Process each Excel file
			results = []
			errors = []
			file_names = [Path(f).name for f in excel_files]
			
			for i, excel_path in enumerate(excel_files):
				excel_name = Path(excel_path).stem  # Get filename without extension
				
				try:
					# Extract text from Excel
					text = extract_text_from_excel_path(excel_path)
					
					if text.strip():
						# Extract JSON data using Gemini
						json_data = extract_with_gemini_func(text, "Excel spreadsheet")
						
						# Save JSON file
						json_filename = f"{excel_name}.json"
						json_path = output_dir / json_filename
						
						try:
							with open(json_path, 'w', encoding='utf-8') as f:
								json.dump(json_data, f, indent=2, ensure_ascii=False)
							
							results.append({
								"file_name": excel_name + Path(excel_path).suffix,
								"json_file": json_filename,
								"status": "✅ Success"
							})
						except Exception as e:
							error_msg = f"Error saving JSON for {excel_name}: {str(e)}"
							errors.append(error_msg)
							results.append({
								"file_name": excel_name + Path(excel_path).suffix, 
								"json_file": json_filename,
								"status": f"❌ Error: {str(e)}"
							})
					else:
						results.append({
							"file_name": excel_name + Path(excel_path).suffix,
							"json_file": "N/A",
							"status": "❌ No data found"
						})
				except Exception as e:
					error_msg = f"Error processing {excel_name}: {str(e)}"
					errors.append(error_msg)
					results.append({
						"file_name": excel_name + Path(excel_path).suffix,
						"json_file": "N/A",
						"status": f"❌ Error: {str(e)}"
					})
			
			return {
				'success': len(errors) == 0,
				'results': results,
				'errors': errors,
				'total_files': len(excel_files),
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