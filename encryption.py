import os
import json
import hmac
import base64
import hashlib

# 文件头，用于识别格式
HEADER = b"CFGv1"
MAC_LEN = 32  # HMAC-SHA256 长度
BLOCK_SIZE = 32  # keystream 每块大小


def derive_key(key_str: str) -> bytes:
    """从字符串密钥生成 32 字节固定 key"""
    return hashlib.sha256(key_str.encode('utf-8')).digest()


def keystream(key: bytes, length: int, nonce: bytes = b"") -> bytes:
    """根据 key 生成伪随机字节流（用于 XOR 加密）"""
    out = bytearray()
    counter = 0
    while len(out) < length:
        ctr_bytes = counter.to_bytes(8, 'big')
        out.extend(hmac.new(key, ctr_bytes + nonce, hashlib.sha256).digest())
        counter += 1
    return bytes(out[:length])


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """异或两个字节串"""
    return bytes(x ^ y for x, y in zip(a, b))


def encrypt_file(input_file: dict, output_path: str, key_str: str):
    """加密文件"""
    input_file_bytes = json.dumps(input_file).encode("utf-8")

    key = derive_key(key_str)
    nonce = os.urandom(8)  # 随机 nonce（避免每次加密相同输出）
    ks = keystream(key, len(input_file_bytes), nonce)
    cipher = xor_bytes(input_file_bytes, ks)

    # 生成 MAC（完整性校验）
    mac_data = HEADER + nonce + cipher
    mac = hmac.new(key, mac_data, hashlib.sha256).digest()

    packaged = HEADER + nonce + mac + cipher
    tmp_file = output_path+".tmp"
    with open(tmp_file, "wb") as f:
        f.write(base64.b64encode(packaged))
    os.replace(tmp_file, output_path)


def decrypt_file(input_path: str, key_str: str) -> dict:
    """解密文件并返回配置字典；若被篡改则报错"""
    if os.path.exists(input_path):
        with open(input_path, 'rb') as f:
            b64data = f.read()
        data = base64.b64decode(b64data)
    else:
        raise NameError("指定文件不存在")

    if not data.startswith(HEADER):
        raise ValueError("文件格式错误")

    offset = len(HEADER)
    nonce = data[offset:offset + 8]
    mac = data[offset + 8:offset + 8 + MAC_LEN]
    cipher = data[offset + 8 + MAC_LEN:]

    key = derive_key(key_str)
    mac_data = HEADER + nonce + cipher
    expected_mac = hmac.new(key, mac_data, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected_mac):
        raise ValueError("文件被篡改或密钥错误")

    ks = keystream(key, len(cipher), nonce)
    plain = xor_bytes(cipher, ks)

    try:
        return json.loads(plain.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError("解密成功但内容非 JSON（可能密钥错误）")

if __name__ == "__main__":
    SECRET_KEY = "potato_love"

    config = {'ss_address':R'.\screenshot', 'ss_max_amount': 5, 'ss_quality': 1, 'ss_shotgap': 30*1000, 'if_quit_judge': -1, 'password_key': 'potato'}

    # 加密
    encrypt_file(config, "config.json", SECRET_KEY)

    # 解密
    config = decrypt_file("config.json", SECRET_KEY)

    print("解密后配置:", config)
