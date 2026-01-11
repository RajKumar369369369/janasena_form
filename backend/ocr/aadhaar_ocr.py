import cv2
import re
from datetime import datetime
from paddleocr import PaddleOCR

# ---------------- OCR INITIALIZATION ----------------
ocr = PaddleOCR(
    lang="en",
    use_angle_cls=True,
    use_textline_orientation=True,
    det=True,
    rec=True,
    cls=False,
    use_gpu=False
)

# ---------------- PREPROCESS IMAGE ----------------
def preprocess_image(img_path):
    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    return img

# ---------------- TEXT EXTRACTION ----------------
def extract_text(img_path):
    img = preprocess_image(img_path)
    result = ocr.ocr(img, cls=True)

    lines = []
    for block in result:
        for line in block:
            lines.append(line[1][0])

    return "\n".join(lines)

# ---------------- NAME EXTRACTION ----------------
def extract_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        if line.lower() == "to":
            if i + 2 < len(lines):
                return lines[i + 2]

    return ""

# ---------------- DATE REGEX ----------------
DATE_REGEX = re.compile(
    r'(0?[1-9]|[12][0-9]|3[01])\s*[/-]\s*'
    r'(0?[1-9]|1[0-2])\s*[/-]\s*'
    r'(19\d{2}|20\d{2})'
)

# ---------------- NORMALIZE OCR TEXT ----------------
def normalize_text(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text

# ---------------- FALLBACK CONTEXT-BASED DOB ----------------
def extract_dob_by_context(text):
    text = normalize_text(text)

    dob_candidates = []
    other_candidates = []

    for match in DATE_REGEX.finditer(text):
        date_str = match.group()
        start = match.start()
        context = text[max(0, start-25): start+25].lower()

        try:
            d, m, y = map(int, re.split(r'[/-]', date_str))
            age = datetime.now().year - y
            if not (0 <= age <= 120):
                continue
        except:
            continue

        # Strong priority: DOB keyword nearby
        if 'dob' in context or 'd.o.b' in context or 'a/dob' in context or 'birth' in context:
            dob_candidates.append(date_str)
        else:
            other_candidates.append(date_str)

    if dob_candidates:
        return dob_candidates[0]  # first date with DOB keyword
    elif other_candidates:
        return other_candidates[0]  # fallback
    else:
        return ""

def extract_aadhaar_number(text):
    # grouped
    match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text)
    if match:
        return match.group()

    # ungrouped fallback
    match = re.search(r'\b\d{12}\b', text)
    if match:
        num = match.group()
        return f"{num[:4]} {num[4:8]} {num[8:]}"
    
    return ""

# ---------------- FINAL DOB EXTRACTION ----------------

def extract_dob(text):
    text = normalize_text(text)

    dates = DATE_REGEX.findall(text)

    if not dates:
        return ""

    # take LAST date (2nd one)
    return "/".join(dates[-1])


def extract_gender(text):
    text = text.upper()

    if "FEMALE" in text:
        return "FEMALE"

    if "MALE" in text:
        return "MALE"

    return ""



# ---------------- FIELD EXTRACTION ----------------
def extract_fields(text):
    data = {
        "Name": "",
        "Adhaar_Number": "",
        "GENDER": "",
        "DOB": "",
        "Mobile": "",
        "Pincode": ""
    }
    data["Adhaar_Number"] = extract_aadhaar_number(text)
    data["Name"] = extract_name(text)
    data["GENDER"]= extract_gender(text)
    data["DOB"] = extract_dob(text)

    mobile_match = re.search(r'\b[6-9]\d{9}\b', text)
    if mobile_match:
        data["Mobile"] = mobile_match.group()

    pin_match = re.search(r'\b\d{6}\b', text)
    if pin_match:
        data["Pincode"] = pin_match.group()

    return data

# ocr/aadhaar_ocr.py

def run_aadhaar_ocr(image_path: str):
    text = extract_text(image_path)
    fields = extract_fields(text)

    # normalize Aadhaar (remove spaces)
    aadhaar = fields["Adhaar_Number"].replace(" ", "")

    return {
        "aadhaar_number": aadhaar,
        "full_name": fields["Name"],
        "gender": fields["GENDER"].capitalize(),
        "dob": fields["DOB"],
        "mobile_number": fields["Mobile"],
        "pincode": fields["Pincode"]
    }

def normalize_aadhaar(aadhaar_str: str) -> str:
    if not aadhaar_str:
        return ""
    # remove any non-digit chars
    return re.sub(r"\D", "", aadhaar_str)

def run_aadhaar_ocr(image_path: str) -> dict:
    """
    Run OCR on the saved image file path and return a dict matching AadhaarOCRResponse.
    This function *normalizes* the aadhaar (removes spaces) so DB lookups succeed.
    """
    text = extract_text(image_path)
    fields = extract_fields(text)

    raw_aadhaar = fields.get("Adhaar_Number", "")  # may be "1234 5678 9012"
    normalized = normalize_aadhaar(raw_aadhaar)    # becomes "123456789012"

    return {
        "aadhaar_number": normalized,
        "full_name": fields.get("Name", "") or "",
        "gender": (fields.get("GENDER", "") or "").capitalize(),
        "dob": fields.get("DOB", "") or "",
        "mobile_number": fields.get("Mobile", "") or "",
        "pincode": fields.get("Pincode", "") or ""
    }

# ---------------- MAIN ----------------
if __name__ == "__main__":
    aadhaar_image_path = r"D:\PycharmProjects\pythonProject\Narendra Mama\Adhaar\Adhaar\Adhaar_001.jpg"

    text = extract_text(aadhaar_image_path)

    print("\n========== EXTRACTED TEXT ==========\n")
    print(text)

    fields = extract_fields(text)

    print("\n========== EXTRACTED FIELDS ==========\n")
    for k, v in fields.items():
        print(f"{k}: {v}")
