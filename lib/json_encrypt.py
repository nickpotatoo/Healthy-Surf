import os
import json
import hmac
import base64
import hashlib

# 文件头，用于识别格式
HEADER = b"CFGv1"
MAC_LEN = 32  # HMAC-SHA256 长度
BLOCK_SIZE = 32  # keystream 每块大小
SECRET_KEY = "potato_love"


def _derive_key(key_str: str) -> bytes:
    """从字符串密钥生成 32 字节固定 key"""
    return hashlib.sha256(key_str.encode('utf-8')).digest()


def _keystream(key: bytes, length: int, nonce: bytes = b"") -> bytes:
    """根据 key 生成伪随机字节流（用于 XOR 加密）"""
    out = bytearray()
    counter = 0
    while len(out) < length:
        ctr_bytes = counter.to_bytes(8, 'big')
        out.extend(hmac.new(key, ctr_bytes + nonce, hashlib.sha256).digest())
        counter += 1
    return bytes(out[:length])


def _xor_bytes(a: bytes, b: bytes) -> bytes:
    """异或两个字节串"""
    return bytes(x ^ y for x, y in zip(a, b))


def encrypt_file(input_file: dict, output_path: str, key_str: str):
    """加密文件"""
    input_file_bytes = json.dumps(input_file).encode("utf-8")

    key = _derive_key(key_str)
    nonce = os.urandom(8)  # 随机 nonce（避免每次加密相同输出）
    ks = _keystream(key, len(input_file_bytes), nonce)
    cipher = _xor_bytes(input_file_bytes, ks)

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

    key = _derive_key(key_str)
    mac_data = HEADER + nonce + cipher
    expected_mac = hmac.new(key, mac_data, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected_mac):
        raise ValueError("文件被篡改或密钥错误")

    ks = _keystream(key, len(cipher), nonce)
    plain = _xor_bytes(cipher, ks)

    try:
        return json.loads(plain.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError("解密成功但内容非 JSON（可能密钥错误）")
    
def load_json(file_name:str, SECRET_KEY, if_backup:bool=True, default:dict=None, if_encryption:bool = True, path:str=".\\"):
    """加载"""
    if if_encryption and not SECRET_KEY:
        raise ValueError("解密需要密钥")
    if not os.path.exists(path):
        raise FileNotFoundError("path不存在")
    if if_backup:
        backup_path = os.getenv('LOCALAPPDATA')+"\\Healthy Surf"
        backup_file_name = file_name[:len(file_name)-5]+"_backup.json"
    
    try:
        if if_encryption:
            res_dict = decrypt_file(path+"\\"+file_name, SECRET_KEY)
        else:
            with open(path+"\\"+file_name, 'r') as file:
                content = file.read()
                res_dict = json.load(content)
        return res_dict
    except Exception as e:
        if if_backup:
            print("读取失败：", e, "尝试读取备份")
            try:
                if if_encryption:
                    res_dict = decrypt_file(backup_path+"\\"+backup_file_name, SECRET_KEY)
                else:
                    with open(path+"\\"+backup_file_name, 'r') as file:
                        content = file.read()
                        res_dict = json.load(content)
                return res_dict
            except Exception as e:
                if default:
                    print("读取备份失败：", e, "已初始化")
                    return default
                else:
                    raise e
        else:
            raise e

def write_json(save_file_name:str, save_file:dict, SECRET_KEY, if_backup:bool=True, if_encryption:bool=True, save_path:str = ".\\"):
    if if_encryption and not SECRET_KEY:
        raise ValueError("加密需要密钥")
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    if if_backup:
        backup_path = os.getenv('LOCALAPPDATA')+"\\Healthy Surf"
        backup_file_name = save_file_name[:len(save_file_name)-5]+"_backup.json"
        if not os.path.exists(backup_path):
            os.mkdir(backup_path)

    try:
        if if_encryption:
            encrypt_file(save_file, save_path+"\\"+save_file_name, SECRET_KEY)
        else:
            temp_file = save_path+"\\"+save_file_name+".tmp"
            with open(temp_file, 'w') as file:
                json.dump(config, file, indent=4)
            os.replace(temp_file, save_path+"\\"+save_file_name)
    except Exception as e:
        raise e
    
    if if_backup:
        try:
            if if_encryption:
                encrypt_file(save_file, backup_path+"\\"+backup_file_name, SECRET_KEY)
            else:
                temp_file = backup_path+"\\"+backup_file_name+".tmp"
                with open(temp_file, 'w') as file:
                    json.dump(config, file, indent=4)
                os.replace(temp_file, backup_path+"\\"+backup_file_name)
        except Exception as e:
            raise e



if __name__ == "__main__":
    config = load_json("config.json", SECRET_KEY)
    print(config)
    write_json("config.json", config, SECRET_KEY)