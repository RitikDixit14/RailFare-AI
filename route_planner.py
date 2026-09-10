class RoutePlanner:
    @staticmethod
    def get_alternative_trains(source, dest, date, current_train_no):
        alternatives = [
            {
                "train_no": "12953",
                "train_name": "AK TEJAS RAJ EX",
                "departure": "17:10",
                "arrival": "09:43",
                "duration": "16h 33m",
                "reason": "Arrives earlier based on schedule",
                "crowd_level": "Moderate",
                "reliability": "High"
            },
            {
                "train_no": "12903",
                "train_name": "GOLDEN TEMPLE M",
                "departure": "18:45",
                "arrival": "13:50",
                "duration": "19h 05m",
                "reason": "Lower estimated crowd level",
                "crowd_level": "Low",
                "reliability": "Medium"
            }
        ]
        return [t for t in alternatives if t["train_no"] != current_train_no]

    @staticmethod
    def get_station_congestion(station_code):
        import datetime
        now = datetime.datetime.now()
        
        return {
            "station": station_code,
            "current_status": "Moderate Congestion",
            "peak_periods": ["08:00 - 10:00", "18:00 - 20:00"],
            "suggested_buffer": "Arrive 45 mins early",
            "last_updated": now.strftime("%I:%M %p"),
            "hourly_forecast": {
                "06:00": "Low",
                "08:00": "High",
                "10:00": "Moderate",
                "12:00": "Low",
                "14:00": "Low",
                "16:00": "Moderate",
                "18:00": "Very High",
                "20:00": "High",
                "22:00": "Low"
            }
        }
