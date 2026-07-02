# Cortex-R52 bare-metal build for the YOLOv5_HW driver (Project 2, Task D).
# Same flow as Project 1's Makefile (freestanding gcc + custom linker script,
# built on the server), but with the 32-bit ARM toolchain because the R52 runs
# AArch32 -- aarch64-none-elf- targets AArch64 only and cannot emit R52 code.
#
# Output: cpu0/yolo_cpu0.elf -- point the bare_metal VP config's cpu0
# initial_image at it.

# -------------------------------
# Toolchain (CHANGE prefix if the server names it differently)
# -------------------------------
CROSS   = arm-none-eabi-
CC      = $(CROSS)gcc
OBJCOPY = $(CROSS)objcopy
OBJDUMP = $(CROSS)objdump

# -------------------------------
# Flags
# -------------------------------
CFLAGS  = -Wall -O0 -g -ffreestanding -nostdlib -nostartfiles
CFLAGS += -mcpu=cortex-r52 -marm
CFLAGS += -mfloat-abi=soft        # no FPU: f2i/f2pct use integer ops only
CFLAGS += -Icommon                # headers live in common/

LDFLAGS = -T common/linker_r52.ld -nostartfiles

# -------------------------------
# Files
# -------------------------------
SRCS   = cpu0/main.c cpu0/startup_r52.S cpu0/images.S
OBJ    = cpu0/main.o cpu0/startup_r52.o cpu0/images.o
TARGET = cpu0/yolo_cpu0

# -------------------------------
# Build
# -------------------------------
all: $(TARGET).elf

$(TARGET).elf: $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(LDFLAGS)

cpu0/%.o: cpu0/%.c
	$(CC) $(CFLAGS) -c $< -o $@

cpu0/%.o: cpu0/%.S
	$(CC) $(CFLAGS) -c $< -o $@

# -------------------------------
# Inspect
# -------------------------------
dump: $(TARGET).elf
	$(OBJDUMP) -d $(TARGET).elf > cpu0/dump.txt

clean:
	rm -f cpu0/*.o $(TARGET).elf cpu0/dump.txt
