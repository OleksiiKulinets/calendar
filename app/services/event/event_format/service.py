class EventFormatService:

    CONFERENCE_DOMAINS = (
        "zoom.us",
        "meet.google.com",
        "teams.microsoft.com",
        "webex.com"
    )

    def detect(self, event: dict) -> str:

        urls = event.get("urls") or []
        location = event.get("location_raw")

        conference_urls = [
            u for u in urls
            if any(d in u for d in self.CONFERENCE_DOMAINS)
        ]

        maps_urls = [
            u for u in urls
            if "google.com/maps" in u or "maps.app" in u
        ]

        registration_urls = [
            u for u in urls
            if "register" in u or "signup" in u
        ]

        has_conference = len(conference_urls) > 0
        has_location = bool(location and location.strip())

        is_online = has_conference or event.get("event_format") == "online"
        is_offline = has_location or len(maps_urls) > 0

        if is_online and is_offline:
            return "hybrid"

        if is_online:
            return "online"

        if is_offline:
            return "offline"

        return "offline"