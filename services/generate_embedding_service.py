from models.input_schema import DocumentInput,PDFInput
from utils.generate_embedding_utils import get_embedding,split_text_into_chunks
from config import collection
from typing import Dict
import os
from fastapi import HTTPException
from pypdf import PdfReader

def generate_embedding(doc:DocumentInput)-> Dict[str,str]:
    vector = get_embedding(doc.text)
    collection.add(ids=[doc.id],
                   embeddings=[vector],
                   documents=[doc.text]
                   )
    return {"status":"success","message":f"document {doc.id} successfully embedded"}

def generate_embedding_by_pdf(inputPdf : PDFInput)-> Dict[str,str]:
    if not os.path.exists(inputPdf.filepath):
        raise HTTPException(status_code=404,detail="File path not found")
    try:
        reader = PdfReader(inputPdf.filepath)
        full_text=""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text+=page_text+"\n"

        if not full_text.strip():
            raise HTTPException(status_code=400,detail="PDF appears to be empty")
        
        chunks = split_text_into_chunks(full_text,1000,200)
        for idx,chunk in enumerate(chunks):
            vector=get_embedding(chunk)
            chunk_id = f"{os.path.basename(inputPdf.filepath)}_chunk_{idx}"
            collection.add(ids=[chunk_id],
                           embeddings=[vector],
                           documents=[chunk],
                           metadatas=[{"source":inputPdf.filepath,"chunk_index":idx}])
        return {
            "status": "success", 
            "message": f"Successfully processed '{os.path.basename(input_data.file_path)}' into {len(chunks)} chunks."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")