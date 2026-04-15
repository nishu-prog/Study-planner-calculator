import os
import json
import logging
from flask import Flask, render_template, request, jsonify
from datetime import datetime

# Application Configuration
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StudyPilotEngine")

class StudyAlgorithm:
    """
    Advanced Logic: Weighted Priority Index (WPI)
    Calculates urgency by squaring difficulty and applying 
    a square-root time decay to prevent data skewing.
    """
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.processed_list = []

    def run(self):
        current_time = datetime.now()
        
        for entry in self.raw_data:
            try:
                # 1. Temporal Analysis
                exam_day = datetime.strptime(entry['deadline'], '%Y-%m-%d')
                days_remaining = (exam_day - current_time).days
                
                # Minimum 1-day buffer for "due today" items
                safe_days = max(days_remaining, 1)
                
                # 2. Mathematical Urgency Scoring
                # Formula: (Complexity^2.4 * 20) / (Days^0.6)
                diff_factor = int(entry['level']) ** 2.4
                time_factor = safe_days ** 0.6
                score = round((diff_factor * 20) / time_factor, 2)
                
                # 3. Effort Allocation Breakdown
                # Translates priority score into suggested daily hours
                total_effort_hours = round(score / 5, 1)
                daily_split = round(total_effort_hours / safe_days, 1)

                self.processed_list.append({
                    "id": os.urandom(3).hex(),
                    "title": entry['label'].upper(),
                    "score": score,
                    "deadline": f"{safe_days} Days",
                    "load": f"{daily_split}h/day",
                    "intensity": "CRITICAL" if score > 250 else "HIGH" if score > 120 else "NORMAL",
                    "theme": "bg-red-500/20 text-red-400" if score > 250 else "bg-amber-500/20 text-amber-400" if score > 120 else "bg-emerald-500/20 text-emerald-400"
                })
            except Exception as e:
                logger.error(f"Logic Error for {entry.get('label')}: {e}")
                continue

        # Sort results: Highest WPI at the top
        return sorted(self.processed_list, key=lambda x: x['score'], reverse=True)

# --- Server Routes ---

@app.route('/')
def home():
    """Main Dashboard View"""
    return render_template('dashboard.html', current_year=datetime.now().year)

@app.route('/api/v1/optimize', methods=['POST'])
def optimize_api():
    """Endpoint for asynchronous priority calculation."""
    user_payload = request.json
    tasks = user_payload.get('tasks', [])
    
    if not tasks:
        return jsonify({"success": False, "msg": "Empty Queue"}), 400

    engine = StudyAlgorithm(tasks)
    final_data = engine.run()
    
    # Statistical Summary
    avg_wpi = sum(t['score'] for t in final_data) / len(final_data) if final_data else 0
    
    return jsonify({
        "success": True,
        "payload": final_data,
        "summary": {
            "total_count": len(final_data),
            "global_urgency": round(avg_wpi, 2)
        }
    })

if __name__ == '__main__':
    # Local Test Environment
    app.run(host='0.0.0.0', port=5000, debug=False)
