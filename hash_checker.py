import hashlib

def check_hash_2_files(file_path, expected_hash) -> bool:
    hasher = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest() == expected_hash