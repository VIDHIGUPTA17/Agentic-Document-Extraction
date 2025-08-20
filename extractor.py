# High-level extraction pipeline: routing -> OCR -> LLM-assisted extraction -> postprocess & QA
import io
from typing import List, Dict, Any, Optional
from ocr import pdf_to_images, image_to_plain_text, image_to_tsv
from router_client import call_openrouter
from schema import ExtractionResult, FieldExtract
from utils import parse_amount, parse_date, compute_overall_confidence, totals_match
import re
import json

# simple routing heuristics
def detect_doc_type(text: str) -> str:
    text_l = text.lower()
    if 'invoice' in text_l or 'invoice no' in text_l:
        return 'invoice'
    if 'prescription' in text_l or 'rx' in text_l or 'patient' in text_l:
        return 'prescription'
    if 'total' in text_l and ('bill' in text_l or 'amount' in text_l):
        return 'medical_bill' if 'patient' in text_l or 'consultation' in text_l else 'bill'
    # fallback
    return 'unknown'

def simple_field_extract(text: str, requested_fields: Optional[List[str]] = None) -> List[Dict[str,Any]]:
    # very naive regex-based extraction for quick results without LLM
    fields = []
    if requested_fields is None:
        requested_fields = ['InvoiceNo','InvoiceDate','Vendor','TotalAmount','PatientName','DoctorName','PrescriptionItems']
    for name in requested_fields:
        v = None
        conf = 0.5
        if name.lower().startswith('invoice'):
            m = re.search(r'(invoice\s*(no\.?|number)[:\s]*([A-Z0-9-]+))', text, re.IGNORECASE)
            if m: v = m.group(3)
        if name.lower().endswith('date'):
            v = parse_date(text)
        if name.lower().startswith('total'):
            amt = parse_amount(text)
            if amt is not None:
                v = str(amt); conf = 0.7
        if name.lower().startswith('patient') or name.lower().startswith('doctor'):
            m = re.search(r'(patient|doctor|dr\.?):?\s*([A-Z][a-z]+\s*[A-Za-z]*)', text, re.IGNORECASE)
            if m: v = m.group(2)
        if name.lower().endswith('items') or 'prescription' in name.lower():
            # try to grep lines that look like medication entries
            items = []
            for line in text.splitlines():
                if re.search(r'\d+\s*(mg|ml|tab|tablet|capsule)', line, re.IGNORECASE):
                    items.append(line.strip())
            if items:
                v = json.dumps(items)
                conf = 0.6
        fields.append({'name': name, 'value': v, 'confidence': conf})
    return fields

def llm_extract(text: str, doc_type: str, requested_fields: Optional[List[str]] = None) -> List[Dict[str,Any]]:
    # Call LLM (OpenRouter) with a prompt asking for structured JSON following a schema.
    # The prompt is kept conservative to improve parse reliability.
    system = {"role":"system","content":"You are a reliable extractor that responds only with JSON matching the requested schema."}
    user_prompt = {
        "role":"user",
        "content": f"Extract the following fields from the document text and return JSON array of objects with keys name,value,confidence (0-1). Fields: {requested_fields or 'auto'}. Document type: {doc_type}. Document text:\n\n{text[:4000]}"
    }
    try:
        resp = call_openrouter([system, user_prompt], model='gpt-4o-mini', max_tokens=800)
        # Expecting the model to return JSON in resp['choices'][0]['message']['content'] or similar
        content = None
        if 'choices' in resp and len(resp['choices'])>0:
            content = resp['choices'][0]['message']['content']
        elif 'output' in resp:
            content = resp['output']
        if content:
            # try to find a JSON substring
            j = None
            try:
                j = json.loads(content)
            except Exception:
                # try to extract between code fences
                import re
                m = re.search(r'\{.*\}', content, re.S)
                if m:
                    try:
                        j = json.loads(m.group(0))
                    except:
                        j = None
            if isinstance(j, list):
                return j
            if isinstance(j, dict) and 'fields' in j:
                return j['fields']
    except Exception as e:
        # LLM failed; fall back to simple extraction
        print('LLM extraction failed:', e)
    return simple_field_extract(text, requested_fields=requested_fields)

def extract_from_bytes(file_bytes: bytes, filename: str = 'document.pdf', requested_fields: Optional[List[str]] = None) -> Dict[str,Any]:
    images = []
    if filename.lower().endswith('.pdf'):
        images = pdf_to_images(file_bytes)
    else:
        from PIL import Image
        images = [Image.open(io.BytesIO(file_bytes)).convert('RGB')]
    # gather text
    full_text = ''
    for page in images:
        full_text += image_to_plain_text(page) + '\n\n'
    doc_type = detect_doc_type(full_text)
    # try LLM extraction first (if key present), else simple
    fields = llm_extract(full_text, doc_type, requested_fields=requested_fields)
    # postprocess: ensure fields are normalized and attach minimal source info
    processed = []
    for f in fields:
        name = f.get('name')
        value = f.get('value')
        confidence = float(f.get('confidence',0) or 0)
        processed.append({'name': name, 'value': value, 'confidence': max(0.0,min(1.0,confidence)), 'source': {'page':1}})
    overall = compute_overall_confidence(processed)
    # QA: if invoice/bill, check totals
    qa = {'passed_rules':[], 'failed_rules':[], 'notes':''}
    if any(x['name'] and x['name'].lower().startswith('total') for x in processed):
        total_field = next((x for x in processed if x['name'] and x['name'].lower().startswith('total')), None)
        items = [x for x in processed if x['name'] and ('item' in x['name'].lower() or 'line' in x['name'].lower())]
        total_val = None
        try:
            total_val = float(total_field['value']) if total_field and total_field['value'] else None
        except:
            total_val = None
        ok, s = totals_match(items, total_val or 0.0)
        if ok:
            qa['passed_rules'].append('totals_match')
        else:
            qa['failed_rules'].append('totals_match')
            qa['notes'] += f' Line items sum {s} vs total {total_val}.'
    return {'doc_type': doc_type, 'fields': processed, 'overall_confidence': overall, 'qa': qa}
