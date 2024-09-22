import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.resume_parser import ResumeParser


def test_resume_parser():
    parser = ResumeParser()
    upload_dir = 'uploads'

    for filename in os.listdir(upload_dir):
        if filename.lower().endswith(('.pdf', '.docx')):
            file_path = os.path.join(upload_dir, filename)

            print(f"\nProcessing: {filename}")
            print("-" * 50)

            with open(file_path, 'rb') as file:
                resume_id, result = parser.parse_resume(file, filename)

            if resume_id is None:
                print(f"Failed to parse {filename}:")
                print(json.dumps(result, indent=2))
            else:
                print(f"Successfully parsed {filename} (ID: {resume_id}):")
                print(json.dumps(result, indent=2))

            print("\n")


if __name__ == "__main__":
    test_resume_parser()