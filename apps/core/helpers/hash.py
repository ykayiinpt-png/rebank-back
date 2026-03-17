import hmac
import hashlib
import binascii

def hmac_sha256_hash(key_string, message_string):
    """
    Generates an HMAC-SHA256 hash for a given message and secret key.
    Both key and message must be encoded to bytes before hashing.
    """
    key_bytes = key_string.encode('utf-8')
    message_bytes = message_string.encode('utf-8')
    hashed = hmac.new(key_bytes, message_bytes, hashlib.sha256)

    # Return the hex digest (a readable string)
    return hashed.hexdigest()