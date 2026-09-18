import hashlib
import re
from pathlib import Path
import cv2
import numpy as np
import pytesseract
import fitz  # PyMuPDF
from web3 import Web3

# Explicit Windows path for the Tesseract binary
pytesseract.pytesseract.tesseract_cmd = r"E:\Animus\tesseract.exe"


def compute_sha256_hex(file_path):
    """Return the hex (without 0x) of SHA-256 of the file"""
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        raise Exception(f"Error computing hash: {e}")


def sha256_hex_to_bytes32(hexstr):
    """Convert hex string (64 chars or with 0x) to bytes32 for contract"""
    h = hexstr.lower()
    if h.startswith("0x"):
        h = h[2:]
    if len(h) != 64:
        raise ValueError("SHA256 hex string must be 64 hex chars")
    return Web3.to_bytes(hexstr="0x" + h)


def format_timestamp(timestamp):
    """Convert Unix timestamp to readable format"""
    if timestamp == 0:
        return "Not issued"
    import datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def validate_certificate_id(cert_id):
    """Validate certificate ID format"""
    if not cert_id or len(cert_id.strip()) == 0:
        return False, "Certificate ID cannot be empty"
    if len(cert_id) > 100:
        return False, "Certificate ID too long (max 100 characters)"
    if not re.match(r'^[a-zA-Z0-9_-]+$', cert_id):
        return False, "Certificate ID can only contain letters, numbers, hyphens, and underscores"
    return True, "Valid"


def get_file_info(file):
    """Get file information and validate"""
    if not file or not file.filename:
        return False, "No file selected"
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        return False, f"File type {file_ext} not allowed. Use: {', '.join(allowed_extensions)}"

    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    max_size = 10 * 1024 * 1024
    if size > max_size:
        return False, f"File too large ({size/1024/1024:.1f}MB). Max size: 10MB"
    return True, {"filename": file.filename, "size": size, "extension": file_ext}


def _convert_pdf_first_page_to_cv2(pdf_path):
    """Render page 1 of a PDF into an OpenCV BGR image"""
    doc = fitz.open(str(pdf_path))
    if len(doc) == 0:
        return None
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    if pix.n == 4:  # RGBA
        return cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
    elif pix.n == 3:  # RGB
        return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    return img_array


def analyze_certificate_ai(file_path):
    """
    AI Forensics:
    - Extracts textual data via Tesseract OCR
    - Inspects pixel sharpness/variance to detect artificial blurring or cut-and-paste edits
    - Scores overall document integrity
    """
    path_obj = Path(file_path)
    ext = path_obj.suffix.lower()

    ai_results = {
        "confidence_score": 100,
        "tampering_detected": False,
        "extracted_text": "",
        "flagged_fields": []
    }

    # 1. Load Image (Direct image or rendered PDF page)
    cv_img = None
    if ext in ['.jpg', '.jpeg', '.png']:
        cv_img = cv2.imread(str(file_path))
    elif ext == '.pdf':
        try:
            cv_img = _convert_pdf_first_page_to_cv2(file_path)
        except Exception as e:
            ai_results["flagged_fields"].append(f"PDF Rasterization notice: {e}")

    # 2. Computer Vision Anomaly Detection
    if cv_img is not None:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Low variance points to abnormal smoothing/smudging over credential areas
        if laplacian_var < 40.0:
            ai_results["tampering_detected"] = True
            ai_results["confidence_score"] -= 30
            ai_results["flagged_fields"].append("Abnormal pixel variance (potential digital alteration or blur).")

        # 3. Tesseract OCR Text Inspection
        try:
            extracted = pytesseract.image_to_string(gray).strip()
            ai_results["extracted_text"] = extracted

            expected_keywords = ["certificate", "degree", "diploma", "awarded", "university", "institute", "completion"]
            matches = [kw for kw in expected_keywords if kw in extracted.lower()]
            if len(matches) < 2:
                ai_results["confidence_score"] -= 20
                ai_results["flagged_fields"].append("Missing standard academic certificate vocabulary.")
        except Exception as e:
            ai_results["flagged_fields"].append(f"OCR scan warning: {e}")
    else:
        ai_results["confidence_score"] = 85
        ai_results["flagged_fields"].append("Document format limited forensic deep scan.")

    ai_results["confidence_score"] = max(0, min(100, ai_results["confidence_score"]))
    return ai_results