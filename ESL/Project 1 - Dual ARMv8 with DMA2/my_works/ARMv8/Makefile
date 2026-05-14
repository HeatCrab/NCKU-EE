# -------------------------------
# Toolchain (CHANGE if needed)
# -------------------------------
CROSS   = aarch64-none-elf-
CC      = $(CROSS)gcc
AS      = $(CROSS)gcc
LD      = $(CROSS)ld
OBJCOPY = $(CROSS)objcopy

# -------------------------------
# Flags
# -------------------------------
CFLAGS  = -Wall -O0 -g -ffreestanding -nostdlib -nostartfiles
CFLAGS += -march=armv8-a
CFLAGS += -mgeneral-regs-only

#------  The flag specifically for a Cortex core, e.g. A35
#CFLAGS += -mcpu=cortex-a35
#------  The flag specifically for an architecture, e.g. ARMv8
#CFLAGS += -march=armv8-a

ASFLAGS = -c -march=armv8-a
#ASFLAGS = -c -mcpu=cortex-a35

LDFLAGS_CPU0 = -T common/linker.ld      -nostartfiles
LDFLAGS_CPU1 = -T common/linker_cpu1.ld -nostartfiles

# -------------------------------
# Files
# -------------------------------
SRCS0 = cpu0/main_cpu0.c cpu0/init.S
SRCS1 = cpu1/main_cpu1.c cpu1/init.S
OBJ0 = $(SRCS0:.c=.o)
OBJ1 = $(SRCS1:.c=.o)

TARGET0 = cpu0/DualARMv8_SW0
TARGET1 = cpu1/DualARMv8_SW1

# -------------------------------
# Build
# -------------------------------
all: $(TARGET0).elf $(TARGET1).elf

$(TARGET0).elf: $(OBJ0)
	$(CC) $(CFLAGS) -o $@ $(OBJ0) $(LDFLAGS_CPU0)

$(TARGET1).elf: $(OBJ1)
	$(CC) $(CFLAGS) -o $@ $(OBJ1) $(LDFLAGS_CPU1)

# Compile C
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Assemble
%.o: %.S
	$(AS) $(CFLAGS) -c $< -o $@

# -------------------------------
# Optional: binary output
# -------------------------------
$(TARGET0).bin: $(TARGET0).elf
	$(OBJCOPY) -O binary $< $@

# -------------------------------
# Clean
# -------------------------------
clean:
	rm -f cpu0/*.o cpu0/*.elf cpu0/*.bin
	rm -f cpu1/*.o cpu1/*.elf cpu1/*.bin

# -------------------------------
# Debug (optional)
# -------------------------------
dump:
	$(CROSS)objdump -d $(TARGET).elf > dump.txt
