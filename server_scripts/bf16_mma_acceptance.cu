#include <cstdio>
#include <cuda_runtime.h>
#include <cstdlib>
// Identical kernel structure, identical instruction family, only the MMA dtype differs.
template<int MODE>
__global__ void chain(float* out, int iters){
    float a0=0,a1=0,a2=0,a3=0;
    const unsigned bf=0x3F803F80u;  // two bf16 1.0
    const unsigned hf=0x3C003C00u;  // two fp16 1.0
    unsigned v = MODE? hf : bf;
    for(int i=0;i<iters;i++){
        if(MODE==0)
          asm volatile("mma.sync.aligned.m16n8k16.row.col.f32.bf16.bf16.f32 {%0,%1,%2,%3},{%4,%4,%4,%4},{%4,%4},{%0,%1,%2,%3};\n"
            :"+f"(a0),"+f"(a1),"+f"(a2),"+f"(a3):"r"(v));
        else
          asm volatile("mma.sync.aligned.m16n8k16.row.col.f32.f16.f16.f32 {%0,%1,%2,%3},{%4,%4,%4,%4},{%4,%4},{%0,%1,%2,%3};\n"
            :"+f"(a0),"+f"(a1),"+f"(a2),"+f"(a3):"r"(v));
    }
    int t=blockIdx.x*blockDim.x+threadIdx.x;
    out[t*4+0]=a0;out[t*4+1]=a1;out[t*4+2]=a2;out[t*4+3]=a3;
}
template<int MODE> void run(const char* name,int reps){
    const int B=128,T=256,IT=20000; const long n=(long)B*T*4;
    float*d;cudaMalloc(&d,n*sizeof(float));float*h=(float*)malloc(n*sizeof(float));
    long totbad=0,totinf=0;
    for(int r=0;r<reps;r++){
        chain<MODE><<<B,T>>>(d,IT); cudaDeviceSynchronize();
        cudaMemcpy(h,d,n*sizeof(float),cudaMemcpyDeviceToHost);
        for(long i=0;i<n;i++){ if(h[i]!=16.0f*IT){totbad++; if(!isfinite(h[i]))totinf++;} }
    }
    double macs=(double)(B*T/32)*IT*2048.0*reps;
    printf("%-6s reps=%d  MACs=%.3e  bad=%ld  inf=%ld  rate/MAC=%.3g  %s\n",
        name,reps,macs,totbad,totinf,totbad/macs, totbad?"FAIL":"PASS");
    cudaFree(d);free(h);
}
int main(){
    int reps = 5;
    const char* e = getenv("REPS");
    if (e) { int v = atoi(e); if (v > 0) reps = v; }
    run<0>("bf16", reps);
    run<1>("fp16", reps);
    return 0;
}
