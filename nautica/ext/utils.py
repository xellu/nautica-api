import random
import string
import hashlib

def randomStr(length: int=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def hashStr(text: str):
    return hashlib.sha256(text.encode()).hexdigest()

def hasUnicode(text: str):
    for char in text:
        if char not in string.ascii_letters+string.digits + "_":
            return True
    return False

