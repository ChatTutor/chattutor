class JSONPaperParser:
    def __init__(
        self,
        capture={
            "authors": {
                "type": "array",
                "match": {
                    "key": ["authors", "writers"],
                },
            },
            "citations": {
                "type": "array",
                "match": {
                    "key": ["citations"],
                },
            },
            "cited_by": {
                "type": "single",
                "match": {
                    "key": ["cited_by"],
                },
            },
            "link": {
                "type": "single",
                "match": {"key": ["link", "paper_link"], "val": "@urllink"},
            },
            "result_id": {
                "type": "single",
                "match": {
                    "key": ["result_id"],
                },
            },
            "snippet": {
                "type": "single",
                "match": {
                    "key": ["snippet"],
                },
            },
            "title": {
                "type": "single",
                "match": {
                    "key": ["title"],
                },
            },
            "resources": {
                "type": "array",
                "match": {
                    "key": ["resources"],
                },
            },
        },
        list_ignore=True,
    ):
        self.capture = capture
        self.list_ignore = list_ignore

    def match_value(self, value, mode):
        if isinstance(value, dict):
            return False
        if isinstance(value, list):
            return False
        if mode == "@link" or mode == "@urllink":
            if value.startswith("http"):
                return True
            return False
        if mode.startswith("~"):
            left = mode[0:]
            return value.startswith(left)
        if mode.endswith("~"):
            left = mode[0:]
            return value.endswith(left)
        # TODO: handle regex

    def try_capture(self, key, value):
        for k, v in self.capture.items():
            matc = v["match"]["key"]
            if isinstance(matc, list):
                for opt in matc:
                    if opt == key:
                        if ("val" in v["match"] and self.match_value(value, v["match"]["val"])) or (
                            not "val" in v["match"]
                        ):
                            return k
            elif isinstance(matc, str):
                if matc == key:
                    if ("val" in v["match"] and self.match_value(value, v["match"]["val"])) or (
                        not "val" in v["match"]
                    ):
                        return k
        return False

    def parse(self, obj):
        queue = []
        output_json = {}
        set_keys = []
        queue.append(obj)
        while len(queue) > 0:
            top = queue[0]
            queue.pop(0)
            for key, value in top.items():
                if self.try_capture(key, value) is not False:
                    _k = self.try_capture(key, value)
                    if not _k in set_keys:
                        output_json[_k] = value
                        set_keys.append(_k)
                # if isinstance(value, list) and self.list_ignore:
                #     # dont' check
                #     a = 0
                elif isinstance(value, dict):
                    queue.append(value)
        return output_json
