import os
import json
import getpass
import requests
from starlette.datastructures import URL
from platformdirs import user_data_dir
from ..manager import Logger
from ..ext.StatusCodes import getMessage

DEFAULT_REPO = "http://localhost:8100/api/v1"
REGISTRIES = os.path.join(user_data_dir("nautica", ensure_exists=True), "registries.json")
AUTH_PATH = os.path.join(user_data_dir("nautica", ensure_exists=True), ".auth")


def _load_regs() -> dict:
    try:
        with open(REGISTRIES, "r") as f:
            return json.loads(f.read())
    except Exception:
        Logger.error("Failed to load registries, using default")
        return {"active": DEFAULT_REPO, "all": [DEFAULT_REPO]}


def _save_regs(data: dict) -> bool:
    try:
        with open(REGISTRIES, "w") as f:
            f.write(json.dumps(data))
        return True
    except Exception:
        Logger.error("Failed to save registries")
        return False


def _ensure_regs_exist():
    if not os.path.exists(REGISTRIES):
        _save_regs({"active": DEFAULT_REPO, "all": [DEFAULT_REPO]})


def get_reg_url() -> str:
    _ensure_regs_exist()
    return _load_regs().get("active", DEFAULT_REPO)


def set_reg_url(url: str) -> bool:
    _ensure_regs_exist()

    try:
        r = requests.get(f"{url}/ping")
        if not r.ok:
            raise ConnectionError()
    except Exception:
        Logger.error("Unable to change registry: URL unreachable")
        return False

    data = _load_regs()
    if data.get("all") is None:
        data["all"] = []
    if url not in data["all"]:
        data["all"].append(url)
    data["active"] = url

    return _save_regs(data)


def get_all_regs() -> list[str]:
    _ensure_regs_exist()
    data = _load_regs()
    return [URL(url).hostname for url in data.get("all", [DEFAULT_REPO])]


def _parse_error(r: requests.Response) -> str:
    try:
        data = r.json()
        return data.get("error", getMessage(r.status_code))
    except Exception:
        return getMessage(r.status_code)


def prompt_login(attempt: int = 0) -> bool:
    if attempt >= 3:
        Logger.critical("Login attempts exceeded the limit")
        return False

    username = input("username> ")
    password = getpass.getpass("password> ")

    r = requests.post(
        f"{get_reg_url()}/auth/login",
        json={"username": username, "password": password, "rememberMe": True},
    )

    if not r.ok:
        Logger.error(f"Failed to log in: {_parse_error(r)}")
        return prompt_login(attempt + 1)

    with open(AUTH_PATH, "w") as f:
        f.write(r.json().get("session"))

    return True


def login() -> tuple[bool, str | None]:
    try:
        with open(AUTH_PATH, "r") as f:
            session = f.read().strip()
    except FileNotFoundError:
        Logger.error("No auth file found, please log in first")
        return False, None

    r = requests.get(f"{get_reg_url()}/auth/me", headers={"Authorization": session})

    if not r.ok:
        Logger.error(f"Failed to log in: {_parse_error(r)}")
        return False, None

    return True, session