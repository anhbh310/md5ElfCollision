#!/usr/bin/env python3
import math
import binascii

# Hàm công cụ
bin_to_words = lambda x: [x[4 * i:4 * (i + 1)] for i in range(len(x) // 4)]
words_to_bin = lambda x: b''.join(x)
word_to_int = lambda x: int.from_bytes(x, 'little')
int_to_word = lambda x: x.to_bytes(4, 'little')
bin_to_int = lambda x: list(map(word_to_int, bin_to_words(x)))
int_to_bin = lambda x: words_to_bin(map(int_to_word, x))
mod32bit = lambda x: x % 2 ** 32
rotleft = lambda x, n: (x << n) | (x >> (32 - n))

# Trạng thái ban đầu
IHV0_HEX = '0123456789abcdeffedcba9876543210'
IHV0 = bin_to_int(binascii.unhexlify(IHV0_HEX.encode()))

# Hằng số
BLOCK_SIZE = 64  # 512 bits (64 bytes)
ROUNDS = BLOCK_SIZE

# Hằng số tại mỗi bước
AC = [int(2 ** 32 * abs(math.sin(t + 1))) for t in range(ROUNDS)]

# Hằng số xoay bit
RC = [7, 12, 17, 22] * 4 + [5, 9, 14, 20] * 4 + [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4

# Hàm phi tuyến
F = lambda x, y, z: (x & y) ^ (~x & z)
G = lambda x, y, z: (z & x) ^ (~z & y)
H = lambda x, y, z: x ^ y ^ z
I = lambda x, y, z: y ^ (x | ~z)
Fx = [F] * 16 + [G] * 16 + [H] * 16 + [I] * 16

# Tách dữ liệu
M1 = lambda t: t
M2 = lambda t: (1 + 5 * t) % 16
M3 = lambda t: (5 + 3 * t) % 16
M4 = lambda t: (7 * t) % 16
Mx = [M1] * 16 + [M2] * 16 + [M3] * 16 + [M4] * 16
Wx = [mxi(i) for i, mxi in enumerate(Mx)]

# Vòng lặp xử lý chính
RoundQNext = lambda w, q, i: mod32bit(
    q[0] + rotleft(mod32bit(Fx[i](q[0], q[1], q[2]) + q[3] + AC[i] + w[Wx[i]]), RC[i]))
DoRounds = lambda w, q, i: DoRounds(w, [RoundQNext(w, q, i)] + q[:3], i + 1) if (i < ROUNDS) else q
MD5CompressionInt = lambda ihvs, b: [mod32bit(ihvsi + qi) for ihvsi, qi in zip(ihvs, DoRounds(bin_to_int(b), ihvs, 0))]
arrSh = lambda x: [x[1], x[2], x[3], x[0]]
arrUs = lambda x: [x[3], x[0], x[1], x[2]]
MD5Compression = lambda ihv, b: arrUs(MD5CompressionInt(arrSh(ihv), b))


class MD5:
    def __init__(self, data=None):
        self._ihv = IHV0
        self.bits = 0
        self.buf = b''
        if data:
            self.update(data)

    def update(self, data):
        self.bits += len(data) * 8
        self.buf += data
        while len(self.buf) >= BLOCK_SIZE:
            to_compress, self.buf = self.buf[:BLOCK_SIZE], self.buf[BLOCK_SIZE:]
            self._ihv = MD5Compression(self._ihv, to_compress)

    def ihv(self):
        return int_to_bin(self._ihv)
