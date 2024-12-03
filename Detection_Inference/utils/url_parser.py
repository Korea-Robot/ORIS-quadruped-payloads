import re

# def parse_url(url: str):
#     # Assuming URL structure includes company and robot names for parsing
#     # Example: rtsp://companyName/robotName/cameraType
#     match = re.match(r".*//([^/]+)/([^/]+)/([^/]+)", url)
#     if match:
#         return match.group(1), match.group(2), match.group(3)
#     return None, None, None

def parse_url(url: str):
    # Assuming URL structure includes company and robot names for parsing
    # Example: rtsp://companyName/robotName/cameraType
    match = re.match(r".*\/([\S]+)\/([\S]+)\/([\S]+)", url)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None
