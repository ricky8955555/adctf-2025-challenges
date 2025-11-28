#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static const uint8_t ENCRYPTED_FLAG[] = {
    0x7c, 0x51, 0x12, 0x26, 0x9,  0xde, 0x4b, 0x19, 0xfd, 0x21, 0x34,
    0x62, 0xb,  0xfc, 0xc7, 0xe4, 0xe5, 0xb6, 0x4c, 0x26, 0x91, 0xc1,
    0xc7, 0xde, 0x18, 0x9e, 0xaf, 0x67, 0x17, 0xf8, 0x22, 0xd3, 0xd5,
    0x88, 0xba, 0xa5, 0x92, 0x47, 0x94, 0x52, 0x72, 0x7e, 0xe,  0x65,
    0x36, 0x70, 0xc7, 0x2f, 0xb1, 0x34, 0x12, 0x7b, 0x20, 0x9e, 0xd3,
    0x4e, 0xb6, 0x36, 0xea, 0x29, 0xf2, 0xb2, 0xea, 0xfe};

static void crypt_inplace(void* buf, size_t size, uint32_t key) {
    uint8_t* ptr;

    uint8_t i;
    uint8_t nbytes;

    uint8_t ch;

    uint32_t ckey;
    uint8_t  shift;

    ptr = buf;
    shift = 0;

    while (size) {
        ckey = key;

        nbytes = size > 4 ? 4 : size;
        for (i = 0; i < nbytes; i++) {
            ch = *ptr ^ (uint8_t)(ckey & 0xff);
            *(ptr++) = ch;
            ckey >>= 8;
        }

        size -= nbytes;

        shift = (shift + 5) % 32;
        key ^= ((key << shift) | (key >> (32 - shift))) | (1 << shift);
    }
}

static uint32_t djb2_hash(const void* buf, size_t size) {
    const uint8_t* ptr;

    uint32_t hash;

    ptr = buf;
    hash = 5381;

    while (size--) {
        hash = ((hash << 5) + hash) + *(ptr++);
    }

    return hash;
}

int main() {
    char     buf[80];
    size_t   len;
    uint32_t hash;

    puts("please input your flag:");

    fgets(buf, sizeof(buf) / sizeof(char), stdin);
    len = strcspn(buf, "\r\n");

    if (len != sizeof(ENCRYPTED_FLAG) / sizeof(uint8_t)) {
        puts("length mismatch.");
        return 1;
    }

    hash = djb2_hash(buf, len);
    crypt_inplace(buf, len, hash);

    if (memcmp(buf, ENCRYPTED_FLAG, len)) {
        puts("incorrect.");
        return 1;
    }

    puts("correct!");
    return 0;
}
