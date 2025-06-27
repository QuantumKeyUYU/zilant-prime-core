#include <jni.h>
#include <stdint.h>
#include <string.h>

int zil_unpack_dir(const char *in, const char *out, const uint8_t *key32);

JNIEXPORT jint JNICALL
Java_com_example_zilant_ZilantJNI_unpackDir(JNIEnv *env, jobject thiz,
                                            jstring in, jstring out,
                                            jbyteArray key) {
    const char *cin = (*env)->GetStringUTFChars(env, in, NULL);
    const char *cout = (*env)->GetStringUTFChars(env, out, NULL);
    jbyte *ckey = (*env)->GetByteArrayElements(env, key, NULL);
    int res = zil_unpack_dir(cin, cout, (const uint8_t *)ckey);
    (*env)->ReleaseByteArrayElements(env, key, ckey, JNI_ABORT);
    (*env)->ReleaseStringUTFChars(env, in, cin);
    (*env)->ReleaseStringUTFChars(env, out, cout);
    return res;
}
