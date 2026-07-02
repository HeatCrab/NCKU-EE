#ifndef YOLOV5_HW_H
#define YOLOV5_HW_H

// YOLOv5_HW: the SystemC wrapper that turns YOLOv5Detector into a memory-mapped
// co-processor on the SoC bus, the way Project 1's DMA2 module exposed its
// transfer engine. The Cortex-R52 drives it through three control registers and
// is notified through an interrupt pin:
//
//   Control registers (target socket, 32-bit word accesses)
//     0x0  SRC    address in RAM1 of the input image container
//     0x4  DST    address in RAM1 to write the inference result
//     0x8  START  write 1 to launch detection; cleared to re-arm
//   (No SIZE register: the image container's header carries width/height, so
//    the module learns the byte count itself, exactly the teacher's spec.)
//
//   Pins
//     clk   processing clock (SC_CTHREAD trigger)
//     RST   active-LOW reset (matches the ARM/UART nRESET convention)
//     INT   active-HIGH interrupt out, wired to the R52 GIC SPI line 0
//           (INTID 32); asserted (driven HIGH) when a detection completes. The
//           R52 GIC samples SPIs as active-HIGH level-sensitive, with no
//           active-LOW option, so the pin is HIGH-asserted unlike DMA2's nIRQ.
//
// On START the module reads the container from SRC over its initiator socket,
// runs YOLOv5Detector::preprocess() + detect(), and writes the detections back
// to DST as a small record the R52 reads:
//
//   [0]  uint32  count
//   then `count` records of 24 bytes each:
//        int32 class_id, float score, float x, float y, float w, float h
//
// This is the Project 1 DMA2 module morphed to the spec's "like a DMA, minus
// SIZE" shape, carrying the three Virtualizer fixes proven there: no second
// base subtraction in b_transport, no memcpy into the non-POD sc_uint
// registers, and a streaming_width set on every master transaction.

#include <systemc.h>
#include <tlm.h>
#include <tlm_utils/simple_initiator_socket.h>
#include <tlm_utils/simple_target_socket.h>

#include <cstdint>
#include <vector>

#include "YOLOv5Detector.h"

class YOLOv5_HW : public sc_module {
 public:
  // TLM sockets
  tlm_utils::simple_initiator_socket<YOLOv5_HW> Msocket;  // bus master
  tlm_utils::simple_target_socket<YOLOv5_HW> Ssocket;     // control registers

  // Other I/O ports
  sc_in<bool> clk;    // Clock pin
  sc_out<bool> INT;   // Interrupt pin (active-HIGH)
  sc_in<bool> RST;    // Reset pin (active-LOW)

  sc_dt::uint64 BASE = 0x10000000;  // control-register base in the system bus

  // Control registers
  sc_uint<32> SRC;    // input image container address (RAM1)
  sc_uint<32> DST;    // result address (RAM1)
  sc_uint<32> START;  // START/CLEAR register

  // Register offsets within BASE
  static constexpr unsigned int kRegSrc = 0x0;
  static constexpr unsigned int kRegDst = 0x4;
  static constexpr unsigned int kRegStart = 0x8;

  // One serialized detection record is 24 bytes; cap the writeback so a corrupt
  // image can never make the module write an unbounded block into RAM1.
  static constexpr unsigned int kRecordBytes = 24;
  static constexpr unsigned int kMaxDetections = 256;

  YOLOv5Detector detector;  // owns the ONNX Runtime session

  // Scratch for the bus transactions; sized at run time from the header.
  tlm::tlm_generic_payload trans;
  sc_time delay = sc_time(10, SC_NS);  // per-transaction latency
  bool done, intr;

  void detect_process();
  void b_transport(tlm::tlm_generic_payload&, sc_time&);

  // A parametrized constructor (BASE) cannot use SC_CTOR, so the SC_CTHREAD
  // below needs SC_CURRENT_USER_MODULE supplied explicitly. This is also why
  // DMA2, which took a base_ argument, could not use a single SC_CTOR.
  SC_HAS_PROCESS(YOLOv5_HW);

  // The ONNX model path is hard-coded in the module the way the spec's Step 7
  // example hard-codes "best.onnx", so the constructor matches DMA2's proven
  // (name, base_) shape; passing it as a const char* parameter made Virtualizer
  // generate a covermodel constructor that did not compile.
  static constexpr const char* kModelPath =
      "/home/user1/esl26/esl2625/project2/my_work/model/best.onnx";

  YOLOv5_HW(sc_module_name name, sc_dt::uint64 base_)
      : Msocket("Msocket"),
        Ssocket("Ssocket"),
        BASE(base_),
        detector(kModelPath) {
    Ssocket.register_b_transport(this, &YOLOv5_HW::b_transport);
    SC_CTHREAD(detect_process, clk.pos());
    reset_signal_is(RST, false);  // active-LOW reset, as in DMA2
  }

 private:
  // Read `length` bytes from `address` over the master socket into `buffer`.
  void bus_read(sc_uint<32> address, unsigned char* buffer,
                unsigned int length);
  // Write `length` bytes from `buffer` to `address` over the master socket.
  void bus_write(sc_uint<32> address, const unsigned char* buffer,
                 unsigned int length);
};

#endif  // YOLOV5_HW_H
