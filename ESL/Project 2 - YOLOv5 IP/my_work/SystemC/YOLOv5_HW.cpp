#include "YOLOv5_HW.h"

#include <cstring>
#include <iostream>

void YOLOv5_HW::bus_read(sc_uint<32> address, unsigned char* buffer,
                         unsigned int length) {
  trans.set_command(tlm::TLM_READ_COMMAND);
  trans.set_address(address);
  trans.set_data_ptr(buffer);
  trans.set_data_length(length);
  // SharedmemoryMap aborts a transaction whose streaming_width is left at the
  // generic-payload default of 0 ("streaming width is set to zero"); set it to
  // the data length for a normal, non-streaming transfer.
  trans.set_streaming_width(length);
  trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
  Msocket->b_transport(trans, delay);
}

void YOLOv5_HW::bus_write(sc_uint<32> address, const unsigned char* buffer,
                          unsigned int length) {
  trans.set_command(tlm::TLM_WRITE_COMMAND);
  trans.set_address(address);
  // The payload data pointer is non-const; the master only reads from `buffer`.
  trans.set_data_ptr(const_cast<unsigned char*>(buffer));
  trans.set_data_length(length);
  trans.set_streaming_width(length);
  trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
  Msocket->b_transport(trans, delay);
}

void YOLOv5_HW::b_transport(tlm::tlm_generic_payload& payload,
                            sc_time& r_delay) {
  wait(r_delay);

  tlm::tlm_command cmd = payload.get_command();
  unsigned char* data = payload.get_data_ptr();
  unsigned int len = payload.get_data_length();
  sc_dt::uint64 addr = payload.get_address();

  payload.set_response_status(tlm::TLM_OK_RESPONSE);

  // NOTE: Virtualizer's SharedmemoryMap already strips BASE before delivering
  // the transaction here, so `addr` is a register-relative offset (0x0..0x8).
  // DMA2 proved that re-subtracting BASE forces every access into the address
  // -error branch, so it is deliberately not done.
  if (cmd == tlm::TLM_WRITE_COMMAND) {
    // sc_uint<32> is not POD (it has a vtable), so the raw payload bytes are
    // packed into a plain uint32 first and then assigned, never memcpy'd into
    // the register object, the second DMA2 fix.
    unsigned int wval = 0;
    std::memcpy(&wval, data, len);
    switch (addr) {
      case kRegSrc:
        SRC = wval;
        std::cout << "YOLOv5_HW WRITE SRC = 0x" << std::hex << SRC << std::dec
                  << std::endl;
        break;
      case kRegDst:
        DST = wval;
        std::cout << "YOLOv5_HW WRITE DST = 0x" << std::hex << DST << std::dec
                  << std::endl;
        break;
      case kRegStart:
        START = wval;
        std::cout << "YOLOv5_HW WRITE START = " << START << std::endl;
        break;
      default:
        payload.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
        std::cout << "YOLOv5_HW WRITE wrong address 0x" << std::hex << addr
                  << std::dec << std::endl;
    }
  } else if (cmd == tlm::TLM_READ_COMMAND) {
    unsigned int rval = 0;
    switch (addr) {
      case kRegSrc:
        rval = SRC;
        std::cout << "YOLOv5_HW READ SRC = 0x" << std::hex << SRC << std::dec
                  << std::endl;
        break;
      case kRegDst:
        rval = DST;
        std::cout << "YOLOv5_HW READ DST = 0x" << std::hex << DST << std::dec
                  << std::endl;
        break;
      case kRegStart:
        rval = START;
        std::cout << "YOLOv5_HW READ START = " << START << std::endl;
        break;
      default:
        payload.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
        break;
    }
    std::memcpy(data, &rval, len);
  }
}

void YOLOv5_HW::detect_process() {
  // Reset behavior
  SRC = 0;
  DST = 0;
  START = 0;
  done = false;
  intr = false;
  // active-HIGH: the R52 GIC samples SPIs as active-HIGH level-sensitive (it has
  // no active-LOW option for SPIs), so idle/de-asserted is LOW, asserted is HIGH.
  INT.write(false);  // de-asserted (LOW)

  while (true) {
    wait();

    if (START == 0x1) {
      if (done) {
        continue;  // already serviced this request; wait for START to clear
      }

      // 1. Read the 16-byte container header to learn the image geometry, the
      //    reason no SIZE register is needed.
      unsigned char header[YOLOv5Detector::kHeaderBytes];
      bus_read(SRC, header, YOLOv5Detector::kHeaderBytes);

      uint32_t magic = 0, width = 0, height = 0, channels = 0;
      std::memcpy(&magic, header + 0, 4);
      std::memcpy(&width, header + 4, 4);
      std::memcpy(&height, header + 8, 4);
      std::memcpy(&channels, header + 12, 4);
      if (magic != YOLOv5Detector::kImageMagic) {
        std::cout << "YOLOv5_HW: bad image magic at SRC 0x" << std::hex << SRC
                  << std::dec << std::endl;
        done = true;
        continue;
      }
      const unsigned int total =
          YOLOv5Detector::kHeaderBytes + width * height * channels;
      std::cout << "YOLOv5_HW: image " << width << "x" << height << " ("
                << total << " bytes)" << std::endl;

      // 2. Read the whole container, then preprocess + detect on the host C++
      //    path. detect() runs in zero simulation time (a behavioral model).
      std::vector<unsigned char> blob(total);
      bus_read(SRC, blob.data(), total);

      std::vector<float> tensor = detector.preprocess(blob.data(), total);
      std::vector<Detection> dets = detector.detect(tensor.data());
      if (dets.size() > kMaxDetections) {
        dets.resize(kMaxDetections);
      }
      std::cout << "YOLOv5_HW: " << dets.size() << " detections" << std::endl;

      // 3. Serialize [count][records...] and write it to DST in RAM1.
      const unsigned int count = static_cast<unsigned int>(dets.size());
      std::vector<unsigned char> result(4 + count * kRecordBytes);
      std::memcpy(result.data(), &count, 4);
      for (unsigned int i = 0; i < count; ++i) {
        unsigned char* rec = result.data() + 4 + i * kRecordBytes;
        int32_t class_id = dets[i].class_id;
        std::memcpy(rec + 0, &class_id, 4);
        std::memcpy(rec + 4, &dets[i].score, 4);
        std::memcpy(rec + 8, &dets[i].x, 4);
        std::memcpy(rec + 12, &dets[i].y, 4);
        std::memcpy(rec + 16, &dets[i].w, 4);
        std::memcpy(rec + 20, &dets[i].h, 4);
      }
      bus_write(DST, result.data(), static_cast<unsigned int>(result.size()));

      // 4. Signal completion on the interrupt pin.
      if (!intr) {
        INT.write(true);  // asserted (HIGH) — fires the R52 GIC SPI (INTID 32)
        intr = true;
        std::cout << "YOLOv5_HW: INT asserted" << std::endl;
      }
      done = true;
    } else {
      // START cleared: re-arm and drop the interrupt.
      done = false;
      if (intr) {
        INT.write(false);  // de-asserted (LOW)
        intr = false;
        std::cout << "YOLOv5_HW: INT cleared" << std::endl;
      }
    }
  }
}
