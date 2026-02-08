STORE_NAME_PREFIX = "fileSearchStores/"


def normalize_store_name(name: str) -> str:
    """Store 이름에 'fileSearchStores/' prefix가 없으면 자동으로 붙인다."""
    if not name.startswith(STORE_NAME_PREFIX):
        return f"{STORE_NAME_PREFIX}{name}"
    return name
