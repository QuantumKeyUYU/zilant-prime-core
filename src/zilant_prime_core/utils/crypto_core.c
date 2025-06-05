#include <stdint.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>

static uint8_t sk0[32];
static uint8_t sk1[32];
static int sk0_set = 0;
static int sk1_set = 0;

int derive_sk0_from_fp(const uint8_t *fp_bytes, size_t fp_len, uint8_t *out_handle) {
    const char salt[] = "ZILANT_SK0_SALT__";
    const char info[] = "ZILANT_INFO_SK0_";
    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_id(EVP_PKEY_HKDF, NULL);
    if (!pctx) return 0;
    if (EVP_PKEY_derive_init(pctx) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    if (EVP_PKEY_CTX_set_hkdf_md(pctx, EVP_sha256()) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    if (EVP_PKEY_CTX_set1_hkdf_salt(pctx, salt, sizeof(salt)-1) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    if (EVP_PKEY_CTX_set1_hkdf_key(pctx, fp_bytes, fp_len) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    if (EVP_PKEY_CTX_add1_hkdf_info(pctx, info, sizeof(info)-1) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    size_t outlen = 32;
    if (EVP_PKEY_derive(pctx, sk0, &outlen) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    EVP_PKEY_CTX_free(pctx);
    sk0_set = 1;
    if (out_handle) *out_handle = 1;
    return 1;
}

int derive_sk1(int sk0_handle, const uint8_t *user_secret, size_t secret_len, uint8_t *out_handle) {
    if (sk0_handle != 1 || !sk0_set) return 0;
    unsigned int len = 32;
    uint8_t salt1[32];
    HMAC(EVP_sha256(), sk0, 32, user_secret, secret_len, salt1, &len);
    const char info[] = "ZILANT_INFO_SK1_";
    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_id(EVP_PKEY_HKDF, NULL);
    if (!pctx) return 0;
    if (EVP_PKEY_derive_init(pctx) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    if (EVP_PKEY_CTX_set_hkdf_md(pctx, EVP_sha256()) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    if (EVP_PKEY_CTX_set1_hkdf_salt(pctx, salt1, 32) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    if (EVP_PKEY_CTX_set1_hkdf_key(pctx, sk0, 32) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    if (EVP_PKEY_CTX_add1_hkdf_info(pctx, info, sizeof(info)-1) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    size_t outlen = 32;
    if (EVP_PKEY_derive(pctx, sk1, &outlen) <= 0) { EVP_PKEY_CTX_free(pctx); return 0; }
    EVP_PKEY_CTX_free(pctx);
    sk1_set = 1;
    if (out_handle) *out_handle = 1;
    return 1;
}

int get_sk_bytes(int sk_handle, uint8_t *out_buf) {
    if (sk_handle != 1 || !sk1_set) return 0;
    memcpy(out_buf, sk1, 32);
    return 1;
}

void release_sk(int sk_handle) {
    if (sk_handle == 1) {
        OPENSSL_cleanse(sk0, 32);
        OPENSSL_cleanse(sk1, 32);
        sk0_set = sk1_set = 0;
    }
}
