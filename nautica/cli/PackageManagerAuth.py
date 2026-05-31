import os
import getpass
import requests
from platformdirs import user_data_dir

from ..manager import Logger
from ..ext.StatusCodes import getMessage

API_URL = "http://localhost:8100/api/v1"

def prompt_login(attempt = 0) -> bool:
    if attempt > 3:
        Logger.critical("Login attempts exceeded the limit")
        return False
        
    path = os.path.join(user_data_dir("nautica", ensure_exists=True), ".auth")
    
    username = input("username> ")
    password = getpass.getpass("password> ")
    
    r = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password, "rememberMe": True})
    if not r.ok:
        data: dict | None = None
        try: data = r.json()
        except: pass
        
        Logger.error(f"Failed to log in: {data.get('error', getMessage(r.status_code)) if data else getMessage(r.status_code)}")
        return prompt_login(attempt + 1)
        
    with open(path, "w") as f:
        session = r.json().get("session")
        f.write(session)
        
    return True
    
    
def login() -> tuple[bool, str | None]:
    path = os.path.join(user_data_dir("nautica", ensure_exists=True), ".auth")
    with open(path, "r") as f:
        session = f.read().strip()
    
    r = requests.get(f"{API_URL}/auth/me", headers={"Authorization": session})
    if not r.ok:
        data: dict | None = None
        try: data = r.json()
        except: pass
        
        Logger.error(f"Failed to log in: {data.get('error', getMessage(r.status_code)) if data else getMessage(r.status_code)}")
        return False, None
    
    return True, session