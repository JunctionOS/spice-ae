#include "rdtsc.h"

#ifdef _MSC_VER
#include <intrin.h>
#else
#include <x86intrin.h>
#endif

JNIEXPORT jlong JNICALL Java_timing_Rdtsc_get_1rdtsc
  (JNIEnv *, jobject) {
      return __rdtsc();
}
