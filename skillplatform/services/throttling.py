import time


class SimpleThrottle:
    def __init__(self, limit=10, window=60):
        self.limit = limit
        self.window = window

    def allow(self, request):
        now = time.time()

        key = "ai_requests"
        requests_log = request.session.get(key, [])

        requests_log = [t for t in requests_log if now - t < self.window]

        if len(requests_log) >= self.limit:
            request.session[key] = requests_log
            return False

        requests_log.append(now)
        request.session[key] = requests_log

        return True