# utils.py
import base64

def encode(string):
    sample_string = string
    sample_string_bytes = sample_string.encode("ascii")

    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")

    print(f"Encoded string: {base64_string}")
    return base64_string

def decode(string):
    base64_string = string
    base64_bytes = base64_string.encode("ascii")

    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")

    return sample_string
