from datetime import datetime, timedelta


class EventValidationService:

    DEFAULT_DURATION = 60

    def validate(self, event: dict) -> dict:
        """
        Validates extracted event data.

        Returns:
        {
            "success": True,
            "start": datetime,
            "end": datetime,
            "duration": int
        }

        or

        {
            "success": False,
            "error": "missing_datetime"
        }
        """

        start = self._parse_datetime(
            event.get("date"),
            event.get("start_time")
        )

        if not start:
            return {
                "success": False,
                "error": "missing_datetime"
            }

        duration = event.get("duration_minutes")

        if duration is None:
            duration = self.DEFAULT_DURATION

        if duration <= 0:
            return {
                "success": False,
                "error": "invalid_duration"
            }

        end = start + timedelta(minutes=duration)

        return {
            "success": True,
            "start": start,
            "end": end,
            "duration": duration
        }

    @staticmethod
    def _parse_datetime(date_str: str | None, time_str: str | None):
        if not date_str or not time_str:
            return None

        try:
            return datetime.fromisoformat(
                f"{date_str}T{time_str}:00"
            )
        except ValueError:
            return None