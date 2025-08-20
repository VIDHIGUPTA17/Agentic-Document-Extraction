import streamlit as st
from extractor import extract_from_bytes
import json
from io import BytesIO

st.set_page_config(page_title='Agentic Doc Extractor', layout='wide')

st.title('Agentic Document Extractor — Demo')

with st.sidebar:
    st.markdown('**Upload** PDF or image. Optionally provide a comma-separated list of fields to extract.')
    uploaded = st.file_uploader('Choose file', type=['pdf','png','jpg','jpeg','tiff'], accept_multiple_files=False)
    fields_text = st.text_input('Optional: fields (comma separated)', value='InvoiceNo,InvoiceDate,Vendor,TotalAmount,LineItems,PatientName,DoctorName,PrescriptionItems')
    run_btn = st.button('Extract')

if uploaded and run_btn:
    file_bytes = uploaded.read()
    requested = [f.strip() for f in fields_text.split(',')] if fields_text.strip() else None
    with st.spinner('Running OCR and extraction...'):
        result = extract_from_bytes(file_bytes, filename=uploaded.name, requested_fields=requested)
    st.success('Extraction finished.')
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader('JSON Output')
        st.json(result)
        st.download_button('Download JSON', data=json.dumps(result, indent=2), file_name='extraction.json', mime='application/json')
    with col2:
        st.subheader('Confidence')
        for f in result['fields']:
            st.write(f"{f['name']}: {f.get('value')}")
            st.progress(int(f.get('confidence',0)*100))
        st.write('Overall confidence:')
        st.progress(int(result.get('overall_confidence',0)*100))
        st.write('QA:')
        st.write(result.get('qa', {}))
