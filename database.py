import json
import os
import uuid
from datetime import datetime

class Database:
    DB_FILE = "mock_db.json"
    
    @classmethod
    def _load(cls):
        if not os.path.exists(cls.DB_FILE):
            return {"complaints": [], "analytics": {}}
        with open(cls.DB_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return {"complaints": [], "analytics": {}}

    @classmethod
    def _save(cls, data):
        with open(cls.DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def submit_complaint(cls, category, description, ref_loc, severity):
        data = cls._load()
        complaint_id = f"IR-{str(uuid.uuid4())[:8].upper()}"
        
        new_complaint = {
            "id": complaint_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": category,
            "description": description,
            "location_ref": ref_loc,
            "severity": severity,
            "status": "Pending Verification"
        }
        
        data["complaints"].append(new_complaint)
        cls._save(data)
        
        return complaint_id

    @classmethod
    def get_all_complaints(cls):
        return cls._load()["complaints"]

