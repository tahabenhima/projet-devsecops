import re

class LogParserEngine:
    def __init__(self):
        self.patterns = {
            "secrets": [
                (r"(?i)(password|secret|key|token)\s*[:=]\s*['\"]?([a-zA-Z0-9@#$%^&+=]{8,})['\"]?", "Potential Secret"),
                (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
                (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token")
            ],
            "errors": [
                (r"(?i)(error|exception|fail|fatal)", "Error/Failure")
            ],
            "urls": [
                (r"https?://[^\s]+", "URL")
            ]
        }

    def parse(self, content: str) -> dict:
        results = {
            "secrets": [],
            "errors": [],
            "urls": []
        }

        for pattern, description in self.patterns["secrets"]:
            for match in re.finditer(pattern, content):
                results["secrets"].append({
                    "type": description,
                    "match": match.group(0), # In production, we should mask this!
                    "position": match.span()
                })

        for pattern, description in self.patterns["errors"]:
            for match in re.finditer(pattern, content):
                results["errors"].append({
                    "type": description,
                    "match": match.group(0),
                    "position": match.span()
                })

        for pattern, description in self.patterns["urls"]:
            for match in re.finditer(pattern, content):
                results["urls"].append({
                    "type": description,
                    "match": match.group(0),
                    "position": match.span()
                })

        return results
