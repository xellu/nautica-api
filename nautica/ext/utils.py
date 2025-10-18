import random
import string
import hashlib
import os

def randomStr(length: int=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def hashStr(text: str):
    return hashlib.sha256(text.encode()).hexdigest()

def hasUnicode(text: str):
    for char in text:
        if char not in string.ascii_letters+string.digits + "_":
            return True
    return False

def walkPath(dir_path: str):
    tree = []
    
    for file in os.listdir(dir_path):
        path = os.path.join(dir_path, file)
        if os.path.isdir(path):
            tree += walkPath(path)
            continue
        
        tree.append(path)
        
    return tree