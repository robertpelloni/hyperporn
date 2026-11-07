#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "tvai.h"

int main(int argc, char **argv) {
    const char *modelDir = argv[1];
    const char *dataDir = argv[2];
    tvai_set_logging(1);
    tvai_set_logging_path("topaz_probe2.log");
    int ok = tvai_setup_model_manager((char *)modelDir, (char *)dataDir, 1);
    printf("setup=%d owns_app=%d\n", ok, tvai_owns_app());
    fflush(stdout);
    char list[8192] = {0};
    int r = tvai_model_list((char *)"prob-4", ModelTypeUpscaling, list, (int)sizeof(list));
    printf("model_list prob-4=%d list=%.200s\n", r, list);
    fflush(stdout);
    char vp[TVAI_PROCESSOR_NAME_SIZE] = {0};
    int vpr = tvai_vp_name((char *)"prob-4", 0, vp);
    printf("vp_name=%d name=%s\n", vpr, vp);
    fflush(stdout);

    VideoProcessorInfo info;
    memset(&info, 0, sizeof(info));
    info.basic.modelName = (char *)"prob-4";
    strncpy(info.basic.processorName, vp, sizeof(info.basic.processorName) - 1);
    info.basic.inputWidth = 320;
    info.basic.inputHeight = 180;
    info.basic.scale = 4;
    info.basic.pixelFormat = TVAIPixelFormatRGB8;
    info.basic.timebase = 1.0 / 60.0;
    info.basic.framerate = 60.0;
    info.basic.device.index = -1; /* CPU */
    info.basic.device.maxMemory = 1.0;
    info.basic.canDownloadModel = 1;
    info.outputWidth = 1280;
    info.outputHeight = 720;
    printf("creating processor...\n");
    fflush(stdout);
    void *proc = tvai_create(&info);
    printf("tvai_create=%p\n", proc);
    fflush(stdout);
    if (!proc) return 2;

    int npix = 320 * 180 * 3;
    unsigned char *buf = (unsigned char *)calloc(npix, 1);
    TVAIBuffer in;
    memset(&in, 0, sizeof(in));
    in.pBuffer = buf;
    in.lineSize = 320 * 3;
    in.pts = 0;
    in.frameNo = 0;
    in.duration = 1;
    printf("processing frame 0...\n");
    fflush(stdout);
    int pr = tvai_process(proc, &in);
    printf("tvai_process=%d outcount=%d\n", pr, tvai_output_count(proc));
    fflush(stdout);
    tvai_end_stream(proc);
    printf("draining output...\n");
    fflush(stdout);
    unsigned char *obuf = (unsigned char *)calloc(1280 * 720 * 3, 1);
    int got = 0;
    for (int i = 0; i < 120; i++) {
        int oc = tvai_output_count(proc);
        if (i % 10 == 0) { printf(" iter %d outcount=%d remaining=%u\n", i, oc, tvai_remaining_frames(proc)); fflush(stdout); }
        if (oc > 0) {
            TVAIBuffer out;
            memset(&out, 0, sizeof(out));
            out.pBuffer = obuf;
            out.lineSize = 1280 * 3;
            int orr = tvai_output_frame(proc, &out);
            printf("output_frame=%d frameNo=%ld pts=%lld\n", orr, out.frameNo, out.pts);
            fflush(stdout);
            got = 1;
            break;
        }
        tvai_wait(500);
    }
    printf("drained got=%d\n", got);
    tvai_destroy(proc);
    printf("done\n");
    return 0;
}
