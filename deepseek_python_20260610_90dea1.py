from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# تخزين مؤقت في الذاكرة (للتجربة)
sessions_db = {}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    chat_id: str = Form(...),
    user_id: str = Form(...),
    file_name: str = Form(...)
):
    session_id = str(uuid.uuid4())[:8]
    
    # تخزين معلومات الجلسة
    sessions_db[session_id] = {
        "chat_id": chat_id,
        "user_id": user_id,
        "file_name": file_name,
        "status": "processing",
        "created_at": datetime.now().isoformat()
    }
    
    # هنا هتضيف تحليل الملف (Gemini)
    # مؤقتًا هرجع رابط تجريبي
    
    dashboard_url = f"https://your-streamlit-app.streamlit.app/?id={session_id}"
    
    return {
        "dashboard_url": dashboard_url,
        "session_id": session_id,
        "status": "success"
    }

@app.get("/status/{session_id}")
def get_status(session_id: str):
    return sessions_db.get(session_id, {"status": "not_found"})

# للتشغيل المحلي
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)