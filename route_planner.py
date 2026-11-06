import requests
from datetime import datetime

# ==============================================================================
# ConfirmTkt Headers (same config as the rest of the project)
# ==============================================================================

def _get_ct_headers():
    return {
        "Accept": "*/*",
        "ApiKey": "ct-web!2$",
        "ClientId": "ct-web",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }


class RoutePlanner:

    @staticmethod
    def get_alternative_trains(source, dest, date, current_train_no):
        """
        Fetches real alternative trains from ConfirmTkt API for the same
        source → destination route on the given date, excluding the current train.

        Args:
            source (str):           Source station code (e.g. "NDLS")
            dest (str):             Destination station code (e.g. "BCT")
            date (str):             Journey date — accepts DD-MM-YYYY or YYYY-MM-DD
            current_train_no (str): Train number to exclude from alternatives

        Returns:
            list[dict] | []: List of alternative train dicts, or empty list on failure.
        """
        # ── Normalise date to DD-MM-YYYY (ConfirmTkt format) ──────────────────
        try:
            date_str = str(date)
            if "-" in date_str and len(date_str) == 10:
                parts = date_str.split("-")
                if len(parts[0]) == 4:          # YYYY-MM-DD → DD-MM-YYYY
                    date_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
                # else already DD-MM-YYYY
        except Exception:
            pass  # fallback: keep whatever was passed

        url = (
            f"https://cttrainsapi.confirmtkt.com/api/v1/trains/search"
            f"?sourceStationCode={source}"
            f"&destinationStationCode={dest}"
            f"&addAvailabilityCache=true"
            f"&excludeMultiTicketAlternates=true"
            f"&sortBy=DEFAULT"
            f"&dateOfJourney={date_str}"
            f"&enableNearby=false"
            f"&enableTG=true"
            f"&showPredictionGlobal=true"
        )

        try:
            resp = requests.get(url, headers=_get_ct_headers(), timeout=10)
            if resp.status_code != 200:
                return []

            raw = resp.json()
            # ConfirmTkt wraps result in data.trainList (confirmed from existing project code)
            train_list = (
                (raw.get("data") or {}).get("trainList")
                or raw.get("trainList")
                or []
            )

        except Exception:
            return []

        alternatives = []
        for t in train_list:
            t_no = str(t.get("trainNumber", ""))

            # Skip the current train the user already selected
            if t_no == str(current_train_no):
                continue

            # ── Map ConfirmTkt fields ──────────────────────────────────────────
            t_name     = t.get("trainName", "Unknown Train")
            departure  = t.get("departureTime") or t.get("fromTime") or "--:--"
            arrival    = t.get("arrivalTime")   or t.get("toTime")   or "--:--"
            duration   = t.get("duration", "")

            running_days = t.get("runningDays", "")
            # Use the exact same key confirmed in working parts of the project
            avail_cache  = t.get("availabilityCache") or t.get("avaialbleCache") or {}
            classes      = list(avail_cache.keys())

            # ── Pick a simple "why recommend" reason ──────────────────────────
            # Check if any class has available seats
            has_avail = False
            avail_summary = ""
            for cls_code, cls_data in avail_cache.items():
                if isinstance(cls_data, dict):
                    status = str(cls_data.get("availability", "")).upper()
                    if "AVAIL" in status or "AVL" in status:
                        has_avail = True
                        avail_summary = f"Seats available in {cls_code}"
                        break
                    elif "RAC" in status and not avail_summary:
                        avail_summary = f"RAC seats in {cls_code}"

            if not avail_summary:
                avail_summary = "Check availability for other classes"

            reason = avail_summary if has_avail else "Alternative route — check classes"

            # ── Reliability tag based on train number prefix ──────────────────
            if t_no.startswith(("12", "22", "20", "02")):
                reliability = "High"
            elif t_no.startswith(("18", "19", "15", "16")):
                reliability = "Medium"
            else:
                reliability = "Standard"

            alternatives.append({
                "train_no":    t_no,
                "train_name":  t_name,
                "departure":   departure,
                "arrival":     arrival,
                "duration":    duration,
                "running_days": running_days,
                "classes":     classes,
                "avail_cache": avail_cache,
                "reason":      reason,
                "reliability": reliability,
                "has_availability": has_avail,
                "source_api":  "ConfirmTkt",
            })

        # Sort: trains with confirmed available seats first
        alternatives.sort(key=lambda x: (0 if x["has_availability"] else 1))

        return alternatives[:5]  # Return up to 5 real alternatives


    @staticmethod
    def get_station_congestion(station_code):
        """
        Returns station congestion info.
        NOTE: No publicly authorized live-congestion API is available.
        Returns a time-aware heuristic estimate and clearly labels it as an estimate.
        """
        now = datetime.now()
        hour = now.hour

        # Time-based congestion heuristic (clearly labeled as estimate)
        if 6 <= hour < 10:
            current_status = "High Congestion"
        elif 10 <= hour < 17:
            current_status = "Moderate Congestion"
        elif 17 <= hour < 21:
            current_status = "Very High Congestion"
        else:
            current_status = "Low Congestion"

        return {
            "station": station_code,
            "current_status": current_status,
            "data_type": "time-based estimate",   # Honest label
            "peak_periods": ["06:00 - 10:00", "17:00 - 21:00"],
            "suggested_buffer": "Arrive 45 mins early during peak hours",
            "last_updated": now.strftime("%I:%M %p"),
            "note": "Live congestion data is not available from any authorized public API. This is a time-of-day estimate only.",
            "hourly_forecast": {
                "06:00": "High",
                "08:00": "Very High",
                "10:00": "Moderate",
                "12:00": "Low",
                "14:00": "Low",
                "16:00": "Moderate",
                "18:00": "Very High",
                "20:00": "High",
                "22:00": "Low"
            }
        }
