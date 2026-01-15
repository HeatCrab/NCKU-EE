#include <SPICtrlTestHarness.h>
using namespace scml2::testing;
class FuncReq_SPI_target : public SPICtrlTestHarness {
// Register the test class and all test methods
SCML2_BEGIN_TESTS(FuncReq_SPI_target); SCML2_TEST(testInitiateTargetTransfer);
SCML2_END_TESTS();
FuncReq_SPI_target();
// initialize is...
virtual void initialize();
// Called before running each testcase
// Reset your model here.
virtual void setup();
// Called after running each testcase
virtual void teardown() {
}
// Called at the end of the complete testrun
virtual void shutdown() {
} void testInitiateTargetTransfer();
};
