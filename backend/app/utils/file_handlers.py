import io
import os
from typing import Optional
from typing import BinaryIO
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

def extract_text_from_file(file_content:bytes, file_name:str)->Optional[str]:

    name,ext = os.path.splitext(file_name)
    ext = ext.lower()

    file_like = io.BytesIO(file_content)

    if ext == '.pdf':
        return extract_pdf_text(file_like)
    elif ext == '.txt':
        return extract_txt_text(file_like)
    elif ext == '.docx':
        return extract_docx_text(file_like)
    else:
        return ValueError(f"unsported file extentiton {ext}")

def extract_pdf_text(file_like) ->str:

    if PdfReader is None:
        raise ImportError(
            "pdf reader is not installed"
        )

    try:
        reader =PdfReader(file_like)
        take_parts =[]

        for page_num,page in enumerate(reader.pages,1):
            text =  page.extract_text()

            if text and text.strip():
                take_parts.append(text)
            else:
                print(f"Warning ! {page_num} has no extracted text")

        return "\n\n ".join(take_parts)
    except Exception as e:
        raise ValueError("failed to read the .pdf {str(e)}")

def extract_docx_text(file_like) ->str:

    if Document is None:
        raise ImportError(
            "docx reader is not installed"
        )

    try:
        doc = Document(file_like)
        take_parts =[]

        for paragraph in doc.paragraphs:
            text =  paragraph.text.strip()

            if text :
                take_parts.append(text)
            else:
                print(f"Warning ! docx has no extracted text")

        return "\n\n ".join(take_parts)
    except Exception as e:
        raise ValueError("failed to read the .pdf {str(e)}")

def extract_txt_text(file_like:BinaryIO) ->str:


    try:
        file_like.seek(0)
        return file_like.read().decode('utf-8')
    except UnicodeDecodeError:
        try:
            file_like.seek(0)
            return file_like.read().decode('latin-1')
        except UnicodeDecodeError:
            raise ValueError("couldnt read the txt file ..please ensure it is utf-8 or latin-1 format")



        