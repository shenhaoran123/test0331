#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"
#pragma GCC diagnostic ignored "-Wcast-qual"
#define __NV_CUBIN_HANDLE_STORAGE__ static
#if !defined(__CUDA_INCLUDE_COMPILER_INTERNAL_HEADERS__)
#define __CUDA_INCLUDE_COMPILER_INTERNAL_HEADERS__
#endif
#include "crt/host_runtime.h"
#include "2mm.fatbin.c"
extern void __device_stub__Z11mm2_kernel1PfS_S_(DATA_TYPE *, DATA_TYPE *, DATA_TYPE *);
extern void __device_stub__Z11mm2_kernel2PfS_S_(DATA_TYPE *, DATA_TYPE *, DATA_TYPE *);
static void __nv_cudaEntityRegisterCallback(void **);
static void __sti____cudaRegisterAll(void) __attribute__((__constructor__));
void __device_stub__Z11mm2_kernel1PfS_S_(DATA_TYPE *__par0, DATA_TYPE *__par1, DATA_TYPE *__par2){__cudaLaunchPrologue(3);__cudaSetupArgSimple(__par0, 0UL);__cudaSetupArgSimple(__par1, 8UL);__cudaSetupArgSimple(__par2, 16UL);__cudaLaunch(((char *)((void ( *)(DATA_TYPE *, DATA_TYPE *, DATA_TYPE *))mm2_kernel1)));}
# 150 "2mm.cu"
void mm2_kernel1( DATA_TYPE *__cuda_0,DATA_TYPE *__cuda_1,DATA_TYPE *__cuda_2)
# 151 "2mm.cu"
{__device_stub__Z11mm2_kernel1PfS_S_( __cuda_0,__cuda_1,__cuda_2);
# 167 "2mm.cu"
}
# 1 "2mm.cudafe1.stub.c"
void __device_stub__Z11mm2_kernel2PfS_S_( DATA_TYPE *__par0,  DATA_TYPE *__par1,  DATA_TYPE *__par2) {  __cudaLaunchPrologue(3); __cudaSetupArgSimple(__par0, 0UL); __cudaSetupArgSimple(__par1, 8UL); __cudaSetupArgSimple(__par2, 16UL); __cudaLaunch(((char *)((void ( *)(DATA_TYPE *, DATA_TYPE *, DATA_TYPE *))mm2_kernel2))); }
# 170 "2mm.cu"
void mm2_kernel2( DATA_TYPE *__cuda_0,DATA_TYPE *__cuda_1,DATA_TYPE *__cuda_2)
# 171 "2mm.cu"
{__device_stub__Z11mm2_kernel2PfS_S_( __cuda_0,__cuda_1,__cuda_2);
# 183 "2mm.cu"
}
# 1 "2mm.cudafe1.stub.c"
static void __nv_cudaEntityRegisterCallback( void **__T3) {  __nv_dummy_param_ref(__T3); __nv_save_fatbinhandle_for_managed_rt(__T3); __cudaRegisterEntry(__T3, ((void ( *)(DATA_TYPE *, DATA_TYPE *, DATA_TYPE *))mm2_kernel2), _Z11mm2_kernel2PfS_S_, (-1)); __cudaRegisterEntry(__T3, ((void ( *)(DATA_TYPE *, DATA_TYPE *, DATA_TYPE *))mm2_kernel1), _Z11mm2_kernel1PfS_S_, (-1)); }
static void __sti____cudaRegisterAll(void) {  __cudaRegisterBinary(__nv_cudaEntityRegisterCallback);  }

#pragma GCC diagnostic pop
