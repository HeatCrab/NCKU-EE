def to_hex(val):
    return f"{val & 0xFFFFFFFF:08X}"

def verify_fir32():
    # Read input data from firData file
    try:
        with open('firData', 'r') as f:
            inputs = [int(line.strip()) for line in f if line.strip()]
    except:
        inputs = list(range(1, 65))

    # 32-order FIR with b = 0x000007C1
    N = 32
    coef_int = 0x000007C1  # Fixed as per Term Project spec
    buffer = [0] * (N + 1)  # 33 elements for N+1 terms

    print(f"{'#':<4} | {'Input (Hex)':<12} | {'y (Hex)':<12}")
    print("-" * 36)

    for idx, x in enumerate(inputs, 1):
        # Shift register (size N+1)
        for i in range(N, 0, -1):
            buffer[i] = buffer[i - 1]
        buffer[0] = x

        # FIR computation: N+1 multiplications
        # sum = x * b + mid[0]*b + mid[1]*b + ... + mid[N-1]*b
        # Note: In teacher's code, mid[0] gets current x (non-blocking)
        # so mid[j].read() reads PREVIOUS cycle's value
        
        # For golden model, we simulate the non-blocking behavior:
        # x.read() * b  (current input)
        # mid[0..N-1].read() * b  (previous cycle values, which is buffer[1..N])
        
        acc = (x * coef_int) & 0xFFFFFFFF  # Current input
        for i in range(1, N + 1):
            term = (buffer[i] * coef_int) & 0xFFFFFFFF
            acc = (acc + term) & 0xFFFFFFFF

        print(f"{idx:<4} | {to_hex(x):<12} | {to_hex(acc):<12}")

verify_fir32()