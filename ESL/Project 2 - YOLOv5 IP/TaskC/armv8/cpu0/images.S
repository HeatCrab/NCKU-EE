// Test image containers baked into the ELF (Project 2, Task D). The per-CPU
// image loader can only load into RAM0, not the bus-attached RAM1, so the three
// container_*.bin files are embedded here (they land in RAM0 .rodata) and the
// CPU copies them into RAM1 at startup -- which is also exactly the rubric's
// "CPU0 passes the images" data flow. Sizes are exported as words so main.c can
// drive the copy without hardcoding lengths.
//
// .incbin paths are resolved from the build directory; testdata/ is synced next
// to the Makefile on the build host.

    .section .rodata.images, "a"
    .balign 4

    .global img0_data
img0_data:
    .incbin "testdata/container_002071.bin"
img0_end:

    .balign 4
    .global img1_data
img1_data:
    .incbin "testdata/container_003379.bin"
img1_end:

    .balign 4
    .global img2_data
img2_data:
    .incbin "testdata/container_005872.bin"
img2_end:

    .section .rodata
    .balign 4
    .global img0_size
img0_size:  .word img0_end - img0_data
    .global img1_size
img1_size:  .word img1_end - img1_data
    .global img2_size
img2_size:  .word img2_end - img2_data
