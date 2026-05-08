#include <cstring>
#include <jni.h>
#include <cinttypes>
#include <android/log.h>
#include <string>
#include "jni.h"

using namespace std;

#define LOGI(...) \
  ((void)__android_log_print(ANDROID_LOG_INFO, "lake-ctf::", __VA_ARGS__))

char* aaa;
char* bbb;

extern "C" JNIEXPORT jlong JNICALL
Java_com_lake_ctf_MainActivity_Init(JNIEnv *env, jobject thiz){
    aaa = (char*)calloc(0x50,1);
    strcpy(aaa, "REPLACE1");
    bbb = (char*)calloc(0x50,1);
    strcpy(bbb, "REPLACE2");
    return 0;
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_lake_ctf_MainActivity_Test(JNIEnv *env, jobject thiz, jstring in){
    char* a = "com/lake/ctf/Check";
    char* b = "Check";
    char buf[0x100];
    memset(buf, 0, 0x100);
    char* out = strcat(buf, a);
    strcat(out, aaa);
    char buf2[0x100];
    memset(buf2, 0, 0x100);
    char* out2 = strcat(buf2, b);
    strcat(out2, bbb);

    jclass cls = env->FindClass(buf);
    jmethodID mid = env->GetStaticMethodID(cls,buf2,"(Ljava/lang/String;)Z");
    return env->CallStaticBooleanMethod(cls, mid, in);
}

void do_nop(JNIEnv *env, jobject thiz, jstring clazz_arg, jstring method_arg){
    const char* clazzz = env->GetStringUTFChars(clazz_arg, 0);
    const char* methodd = env->GetStringUTFChars(method_arg, 0);
    strcpy(reinterpret_cast<char *const>(aaa), clazzz);
    strcpy(reinterpret_cast<char *const>(bbb), methodd);
}

JNIEXPORT jint JNI_OnLoad(JavaVM* vm, void* reserved) {
    JNIEnv *env;
    if (vm->GetEnv(reinterpret_cast<void **>(&env), JNI_VERSION_1_6) != JNI_OK) {
        return JNI_ERR;
    }
    void* buf[7];
    const char* name = "nop";
    const char* sig = "(Ljava/lang/String;Ljava/lang/String;)V";
    buf[2] = (void*)&do_nop;
    buf[0] = (void*)name;
    buf[1] = (void*)sig;
    REPLACE3 
    //jclass c = env->FindClass("com/lake/ctf/Check123");
    //env->RegisterNatives(c, (const JNINativeMethod *)&buf, 1);
    return JNI_VERSION_1_6;
}
