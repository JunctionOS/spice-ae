#include <nan.h>
#include <stdint.h>

#if defined(_MSC_VER)
#include <intrin.h>
uint64_t rdtsc() { return __rdtsc(); }
#else
uint64_t rdtsc() {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}
#endif

NAN_METHOD(GetCycles) {
    uint64_t cycles = rdtsc();
    info.GetReturnValue().Set(Nan::New((double)cycles));
}

NAN_MODULE_INIT(Init) {
    Nan::Set(target, Nan::New("getCycles").ToLocalChecked(),
             Nan::GetFunction(Nan::New<v8::FunctionTemplate>(GetCycles)).ToLocalChecked());
}

NODE_MODULE(rdtsc, Init)
