def to_hex(val):
    return f"{val & 0xFFFFFFFF:08X}"

def sc_fixed_to_uint32(float_val):
    # Convert float to Q16.16 fixed-point format
    fixed_int = int(float_val * 65536) & 0xFFFFFFFF
    return fixed_int

def uint32_to_sc_fixed(uint_val):
    # Interpret uint32 as Q16.16 fixed-point
    if uint_val & 0x80000000:
        return (uint_val - 0x100000000) / 65536.0
    else:
        return uint_val / 65536.0

def verify_fir_fixed_point():
    # Read input data from firData file
    try:
        with open('firData', 'r') as f:
            inputs = [int(line.strip()) for line in f if line.strip()]
    except:
        inputs = [65536 * i for i in range(1, 65)]

    taps_config = {'fir32': 32, 'fir48': 48}
    buffers = {name: [0] * taps for name, taps in taps_config.items()}

    print(f"{'#':<4} | {'Input (Hex)':<12} | {'y32 (Hex)':<12} | {'y48 (Hex)':<12}")
    print("-" * 52)

    for idx, x in enumerate(inputs, 1):
        outputs = {}

        for name, N in taps_config.items():
            # Coefficient: bi = 1/(N+1)
            coef_float = 1.0 / (N + 1)
            coef_fixed = sc_fixed_to_uint32(coef_float)
            coef_value = uint32_to_sc_fixed(coef_fixed)

            # Shift register
            buffer = buffers[name]
            for i in range(N - 1, 0, -1):
                buffer[i] = buffer[i - 1]
            buffer[0] = x

            # FIR computation
            acc = 0.0
            for i in range(N):
                data_value = uint32_to_sc_fixed(buffer[i])
                acc += data_value * coef_value

            y = sc_fixed_to_uint32(acc)
            outputs[name] = y

        print(f"{idx:<4} | {to_hex(x):<12} | {to_hex(outputs['fir32']):<12} | {to_hex(outputs['fir48']):<12}")

verify_fir_fixed_point()