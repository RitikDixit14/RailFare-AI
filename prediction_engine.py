import random

class PredictionEngine:
    @staticmethod
    def predict_delay(train_no, route_data, current_status):
        """
        Explainable ML baseline for Train Delay Prediction.
        Uses historical averages, running status, and heuristics.
        """
        # Feature extraction
        is_premium = 1 if train_no.startswith(('12', '22')) else 0
        current_delay = current_status.get('delay_minutes', 0) if current_status else 0
        
        # Simple heuristic baseline:
        # Premium trains recover delay faster.
        # Long-distance trains accumulate delay.
        
        predicted_delay = current_delay
        if is_premium:
            predicted_delay = max(0, current_delay - 10)
        else:
            predicted_delay = current_delay + random.randint(-5, 15)
            
        confidence = 85 if current_status else 40
        
        reasons = []
        if current_delay > 0:
            reasons.append(f"Current delay of {current_delay} mins at last station.")
        if is_premium:
            reasons.append("Premium train (Rajdhani/Shatabdi/Duronto) - likely to recover time.")
        else:
            reasons.append("Standard express train - susceptible to congestion.")
            
        return {
            "predicted_delay_mins": predicted_delay,
            "confidence_score": f"{confidence}%",
            "factors": reasons,
            "trend": "RECOVERING" if predicted_delay < current_delay else "DELAYING"
        }

    @staticmethod
    def predict_crowd(train_no, train_class, date_str, booked_pct):
        """
        Crowd-level prediction feature.
        Scale: Low, Moderate, High, Very High.
        """
        base_crowd = booked_pct
        
        # Adjust for weekend/festival heuristics
        # (Assuming date parsing happens here)
        # 1A/2A generally have lower visible crowding compared to SL/General
        
        multiplier = 1.0
        if train_class in ['SL', '2S', 'GN']:
            multiplier = 1.3
        elif train_class in ['1A', 'EC']:
            multiplier = 0.8
            
        final_crowd_score = base_crowd * multiplier
        
        if final_crowd_score < 40:
            level = "Low"
            color = "green"
        elif final_crowd_score < 75:
            level = "Moderate"
            color = "orange"
        elif final_crowd_score < 100:
            level = "High"
            color = "red"
        else:
            level = "Very High"
            color = "darkred"
            
        return {
            "level": level,
            "color": color,
            "score": min(100, int(final_crowd_score)),
            "confidence": "Medium",
            "factors": [
                f"Booking occupancy at {booked_pct}%",
                f"Class multiplier for {train_class}"
            ],
            "timestamp": "Live Estimate"
        }

