import logging
import json
import uuid


class StructuredLogger:

    def __init__(self, name="agent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)

    def log(self, event_type, payload):

        log_entry = {
            "event": event_type,
            "payload": payload
        }

        self.logger.info(json.dumps(log_entry))


def generate_request_id():
    return str(uuid.uuid4())
