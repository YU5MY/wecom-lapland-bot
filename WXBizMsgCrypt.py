"""
企业微信回调消息加解密 SDK
参考：https://developer.work.weixin.qq.com/document/path/90968
"""
import base64
import hashlib
import random
import socket
import struct
import os
import xml.etree.ElementTree as ET
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding


class WXBizMsgCrypt:
    def __init__(self, sToken: str, sEncodingAESKey: str, sReceiveId: str):
        self.token = sToken
        self.aes_key = base64.b64decode(sEncodingAESKey + "=")
        self.receive_id = sReceiveId

    def VerifyURL(self, msg_signature: str, timestamp: str, nonce: str, echo_str: str):
        """验证URL有效性，返回(errcode, 解密后的echostr)"""
        signature = self._get_signature(timestamp, nonce, echo_str)
        if signature != msg_signature:
            return -1, None
        decrypted = self._decrypt(echo_str)
        return 0, decrypted

    def DecryptMsg(self, post_data: str, msg_signature: str, timestamp: str, nonce: str):
        """解密回调消息"""
        root = ET.fromstring(post_data)
        encrypt_node = root.find("Encrypt")
        if encrypt_node is None:
            return -1, None
        encrypt_text = encrypt_node.text

        signature = self._get_signature(timestamp, nonce, encrypt_text)
        if signature != msg_signature:
            return -2, None

        decrypted = self._decrypt(encrypt_text)
        return 0, decrypted

    def EncryptMsg(self, reply_msg: str, nonce: str, timestamp: str = None) -> tuple:
        """加密回复消息，返回(errcode, xml_str)"""
        import time
        if timestamp is None:
            timestamp = str(int(time.time()))

        raw = self._encrypt(reply_msg)
        signature = self._get_signature(timestamp, nonce, raw)

        xml = f"""<xml>
<Encrypt><![CDATA[{raw}]]></Encrypt>
<MsgSignature><![CDATA[{signature}]]></MsgSignature>
<TimeStamp>{timestamp}</TimeStamp>
<Nonce><![CDATA[{nonce}]]></Nonce>
</xml>"""
        return 0, xml

    # ──── 内部方法 ────

    def _get_signature(self, timestamp: str, nonce: str, msg: str) -> str:
        sort_list = sorted([self.token, timestamp, nonce, msg])
        content = "".join(sort_list)
        return hashlib.sha1(content.encode("utf-8")).hexdigest()

    def _decrypt(self, text: str) -> str:
        raw = base64.b64decode(text)
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.aes_key[:16]))
        decryptor = cipher.decryptor()
        padded = decryptor.update(raw) + decryptor.finalize()

        # 去除 PKCS7 填充
        unpadder = sym_padding.PKCS7(256).unpadder()
        plain = unpadder.update(padded) + unpadder.finalize()

        # 格式：[随机16字节][消息长度4字节][消息][receive_id]
        msg_len = struct.unpack(">I", plain[16:20])[0]
        msg = plain[20 : 20 + msg_len].decode("utf-8")
        receive_id = plain[20 + msg_len :].decode("utf-8")

        if receive_id != self.receive_id:
            raise ValueError(f"ReceiveId 不匹配: {receive_id} != {self.receive_id}")
        return msg

    def _encrypt(self, text: str) -> str:
        raw_msg = text.encode("utf-8")
        msg_len = struct.pack(">I", len(raw_msg))
        raw = os.urandom(16) + msg_len + raw_msg + self.receive_id.encode("utf-8")

        # PKCS7 填充
        padder = sym_padding.PKCS7(256).padder()
        padded = padder.update(raw) + padder.finalize()

        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.aes_key[:16]))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded) + encryptor.finalize()
        return base64.b64encode(encrypted).decode("utf-8")
