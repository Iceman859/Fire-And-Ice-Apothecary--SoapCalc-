"""
Manages production batches and cure dates.
"""
import json
import os
from datetime import datetime, timedelta
import uuid

class BatchManager:
    """Manages production batches and cure dates"""
    
    def __init__(self, filepath="batches.json"):
        self.filepath = filepath
        self.batches = []
        self.load_batches()

    def load_batches(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.batches = json.load(f)
            except:
                self.batches = []

    def save_batches(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.batches, f, indent=4)
        except Exception as e:
            print(f"Error saving batches: {e}")

    def create_batch(self, recipe_data, notes=""):
        """Create a new batch entry from a recipe"""
        # Generate a simple Lot Number: YYYYMMDD-ShortUUID
        date_str = datetime.now().strftime("%Y%m%d")
        short_id = str(uuid.uuid4())[:4].upper()
        lot_number = f"{date_str}-{short_id}"
        
        batch = {
            "id": str(uuid.uuid4()),
            "lot_number": lot_number,
            "recipe_name": recipe_data.get("name", "Unknown"),
            "date_made": datetime.now().strftime("%Y-%m-%d"),
            # Default 4 week cure
            "cure_date": (datetime.now() + timedelta(weeks=4)).strftime("%Y-%m-%d"),
            "status": "Curing",
            "total_weight": recipe_data.get("properties", {}).get("total_batch_weight", 0),
            "recipe_snapshot": recipe_data,
            "notes": notes
        }
        self.batches.insert(0, batch) # Add to top
        self.save_batches()
        return batch

    def delete_batch(self, batch_id):
        self.batches = [b for b in self.batches if b["id"] != batch_id]
        self.save_batches()
        
    def update_status(self, batch_id, status):
        for b in self.batches:
            if b["id"] == batch_id:
                b["status"] = status
                self.save_batches()
                return

    def update_notes(self, batch_id, notes):
        """Update notes for a specific batch"""
        for b in self.batches:
            if b["id"] == batch_id:
                b["notes"] = notes
                self.save_batches()
                return