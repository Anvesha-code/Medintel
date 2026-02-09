from utils.session_state import get_uploaded_files

def get_document_options():
    files = get_uploaded_files()
    return ["All Documents"] + [f["file_name"] for f in files]
