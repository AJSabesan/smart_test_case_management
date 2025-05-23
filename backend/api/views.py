from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pdfplumber
from django.core.files.uploadedfile import UploadedFile
import google.generativeai as genai
import os
import re
import tempfile
import shutil
from django.conf import settings

# Configure Gemini API (replace with your actual API key)
GEMINI_API_KEY = settings.GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

# Directory for temporary file storage
TEMP_UPLOAD_DIR = os.path.join(tempfile.gettempdir(), 'stcmt_uploads')

@csrf_exempt
def generate_test_cases(request):
    if request.method == 'POST':
        try:
            srs_text = ''
            temp_file_path = None

            # Create temporary directory if it doesn't exist
            if not os.path.exists(TEMP_UPLOAD_DIR):
                os.makedirs(TEMP_UPLOAD_DIR)

            # Check if a PDF file is uploaded
            if 'file' in request.FILES:
                pdf_file = request.FILES['file']
                if not pdf_file.name.endswith('.pdf'):
                    return JsonResponse({'error': 'Only PDF files are supported'}, status=400)

                # Save PDF temporarily to disk
                temp_file_path = os.path.join(TEMP_UPLOAD_DIR, pdf_file.name)
                with open(temp_file_path, 'wb') as f:
                    for chunk in pdf_file.chunks():
                        f.write(chunk)

                # Extract text from PDF using pdfplumber
                with pdfplumber.open(temp_file_path) as pdf:
                    for page in pdf.pages:
                        srs_text += page.extract_text() + '\n'
            else:
                # Fallback to JSON body for text input
                data = json.loads(request.body)
                srs_text = data.get('srs', '')

            # Clean up temporary file if it was saved
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

            if not srs_text.strip():
                return JsonResponse({'error': 'No SRS text provided or extracted'}, status=400)

            # Preprocess text: Extract sentences with functional requirements
            sentences = re.split(r'[.!?]', srs_text)
            filtered_srs = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and any(keyword in sentence.lower() for keyword in ['shall', 'must', 'create', 'update', 'delete', 'system']):
                    filtered_srs.append(sentence)
            processed_srs = '. '.join(filtered_srs)

            if not processed_srs:
                processed_srs = srs_text  # Fallback to full text if no requirements found

            # Craft prompt for Gemini
            prompt = f"""
You are a test case generation expert. Given the following Software Requirements Specification (SRS) text, generate detailed test cases. Each test case should include:
- Test Case ID (e.g., TC1, TC2)
- Description: What the test verifies
- Expected Result: The expected outcome

SRS Text:
{processed_srs}

Generate up to 10 test cases based on the functional requirements in the SRS. Use clear, concise language. If the input is too long, prioritize key functional requirements (e.g., sentences with 'shall' or 'must'). Return test cases in JSON format:
[
  {{"id": "TC1", "description": "...", "expected_result": "..."}},
  ...
]
"""

            # Call Gemini API (simulated for now)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)

            # Parse Gemini response (simulated with rule-based logic)
            test_cases = []
            for i, sentence in enumerate(filtered_srs[:10], 1):  # Limit to 10 test cases
                if sentence:
                    test_case = {
                        'id': f'TC{i}',
                        'description': f"Verify that {sentence}",
                        'expected_result': f"{sentence} succeeds as specified."
                    }
                    test_cases.append(test_case)

            # In a real implementation, parse response.text from Gemini
            # e.g., test_cases = json.loads(response.text)

            if not test_cases:
                test_cases.append({
                    'id': 'TC1',
                    'description': 'Verify basic functionality of the system based on SRS.',
                    'expected_result': 'System behaves as described in SRS.'
                })

            return JsonResponse({'test_cases': test_cases})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        finally:
            # Clean up temporary directory if empty
            if os.path.exists(TEMP_UPLOAD_DIR) and not os.listdir(TEMP_UPLOAD_DIR):
                shutil.rmtree(TEMP_UPLOAD_DIR)
    return JsonResponse({'error': 'Invalid request method'}, status=405)