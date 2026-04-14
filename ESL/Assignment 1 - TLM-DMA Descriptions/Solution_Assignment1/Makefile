SYSTEMC_DIR = ${SYSTEMC_HOME}
PROJECT     = dma
BUILDFLAGS  = -g3
CXX         = g++ -std=c++17
BUILDDIR    = build

INCFLAGS    = -I. -I${SYSTEMC_DIR}/include
LDFLAGS     = -L${SYSTEMC_DIR}/lib -Wl,-rpath,${SYSTEMC_DIR}/lib -lsystemc -lm
SRC_CPPHEAD = DMA CPU MEM
SRC_CPP     =
HEADERS     =
MAIN        = main.cpp
OBJECTS     = $(addprefix $(BUILDDIR)/,$(SRC_CPPHEAD:=.o) $(SRC_CPP:cpp=o))

EXE = $(PROJECT)

all: $(EXE)

$(BUILDDIR):
	mkdir -p $(BUILDDIR)

$(EXE): $(MAIN) $(OBJECTS) $(HEADERS)
	@echo "$@ building..."
	$(CXX) $(INCFLAGS) $(MAIN) $(OBJECTS) $(LDFLAGS) -o $@
	@echo ""
	@echo "$@ build done successfully..."
	@echo ""

$(BUILDDIR)/%.o: %.cpp %.h | $(BUILDDIR)
	@echo "Compiling $< ..."
	$(CXX) -c $< $(INCFLAGS) -o $@

clean:
	rm -f $(EXE)
	rm -rf $(BUILDDIR)
	rm -f *.vcd
