# ONNX Runtime 1.27.0 Environment Setup

## 1. Overview

This document describes how to set up the ONNX Runtime 1.27.0 C++ environment on the ESL server.

The installed ONNX Runtime package provides the required C/C++ header files and shared libraries for compiling and running host-side C++ programs that depend on ONNX Runtime.

---

## 2. Installation Path

ONNX Runtime 1.27.0 is installed at:

```tcsh
/home/user1/esl26/lib/onnxruntime-linux-x64-1.27.0
```

The environment setup script is located at:

```tcsh
/home/user1/esl26/lib/ort_1270.csh
```

The important files are:

```text
/home/user1/esl26/lib/onnxruntime-linux-x64-1.27.0/include/onnxruntime_cxx_api.h
/home/user1/esl26/lib/onnxruntime-linux-x64-1.27.0/lib/libonnxruntime.so
/home/user1/esl26/lib/onnxruntime-linux-x64-1.27.0/lib/libonnxruntime.so.1.27.0
```

---

## 3. Load the Environment

Before using ONNX Runtime, source the environment script:

```tcsh
source /home/user1/esl26/lib/ort_1270.csh
```

After sourcing the script, the following environment variables will be configured:

```tcsh
ORT_HOME
LD_LIBRARY_PATH
LIBRARY_PATH
CPLUS_INCLUDE_PATH
```

---

## 4. Environment Variables

### ORT_HOME

`ORT_HOME` points to the ONNX Runtime installation directory.

Expected value:

```tcsh
/home/user1/esl26/lib/onnxruntime-linux-x64-1.27.0
```

### LD_LIBRARY_PATH

`LD_LIBRARY_PATH` allows Linux to locate the ONNX Runtime shared library during execution.

The following path is added:

```tcsh
${ORT_HOME}/lib
```

### LIBRARY_PATH

`LIBRARY_PATH` helps the linker locate ONNX Runtime libraries during compilation.

The following path is added:

```tcsh
${ORT_HOME}/lib
```

### CPLUS_INCLUDE_PATH

`CPLUS_INCLUDE_PATH` helps the compiler locate ONNX Runtime C++ header files.

The following path is added:

```tcsh
${ORT_HOME}/include
```

---

## 5. Environment Script Content

The environment script should contain:

```tcsh
setenv ORT_HOME /home/user1/esl26/lib/onnxruntime-linux-x64-1.27.0

if ( $?LD_LIBRARY_PATH ) then
    setenv LD_LIBRARY_PATH ${ORT_HOME}/lib:${LD_LIBRARY_PATH}
else
    setenv LD_LIBRARY_PATH ${ORT_HOME}/lib
endif

if ( $?LIBRARY_PATH ) then
    setenv LIBRARY_PATH ${ORT_HOME}/lib:${LIBRARY_PATH}
else
    setenv LIBRARY_PATH ${ORT_HOME}/lib
endif

if ( $?CPLUS_INCLUDE_PATH ) then
    setenv CPLUS_INCLUDE_PATH ${ORT_HOME}/include:${CPLUS_INCLUDE_PATH}
else
    setenv CPLUS_INCLUDE_PATH ${ORT_HOME}/include
endif
```

---

## 6. Check the Environment

After sourcing the script, check whether the variables are set correctly:

```tcsh
echo $ORT_HOME
echo $LD_LIBRARY_PATH
echo $LIBRARY_PATH
echo $CPLUS_INCLUDE_PATH
```

The output should include:

```tcsh
/home/user1/esl26/lib/onnxruntime-linux-x64-1.27.0
```

The library and include paths should include:

```tcsh
/home/user1/esl26/lib/onnxruntime-linux-x64-1.27.0/lib
/home/user1/esl26/lib/onnxruntime-linux-x64-1.27.0/include
```

---

## 7. Compiler and Linker Flags

When compiling C++ code that uses ONNX Runtime, include the following flags:

```tcsh
-I${ORT_HOME}/include
-L${ORT_HOME}/lib
-lonnxruntime
-Wl,-rpath,${ORT_HOME}/lib
```

Example usage:

```tcsh
g++ source.cpp -o output \
    -I${ORT_HOME}/include \
    -L${ORT_HOME}/lib \
    -lonnxruntime \
    -Wl,-rpath,${ORT_HOME}/lib \
    -std=c++17
```

---

## 8. Makefile Example

For Makefile-based compilation, the following variables can be added:

```makefile
ORT_HOME = /home/user1/esl26/lib/onnxruntime-linux-x64-1.27.0

CXXFLAGS += -I$(ORT_HOME)/include
LDFLAGS  += -L$(ORT_HOME)/lib
LDFLAGS  += -lonnxruntime
LDFLAGS  += -Wl,-rpath,$(ORT_HOME)/lib
```

---

## 9. Optional: Auto-load on Login

To automatically load the ONNX Runtime environment whenever a new `tcsh` shell starts, add the following line to `~/.tcshrc`:

```tcsh
source /home/user1/esl26/lib/ort_1270.csh
```

This step is optional.

If the ONNX Runtime environment is only needed for specific work, it is recommended to source it manually instead of adding it permanently to `~/.tcshrc`.

---

## 10. Common Environment Issues

### Header file not found

Possible message:

```text
onnxruntime_cxx_api.h: No such file or directory
```

Check that the include path is available:

```tcsh
echo $CPLUS_INCLUDE_PATH
```

or add the include flag manually:

```tcsh
-I${ORT_HOME}/include
```

---

### Shared library not found

Possible message:

```text
libonnxruntime.so: cannot open shared object file
```

Check that the library path is available:

```tcsh
echo $LD_LIBRARY_PATH
```

or source the environment script again:

```tcsh
source /home/user1/esl26/lib/ort_1270.csh
```

---

### Linker cannot find ONNX Runtime

Possible message:

```text
cannot find -lonnxruntime
```

Check that the library path is available:

```tcsh
echo $LIBRARY_PATH
```

or add the library path manually:

```tcsh
-L${ORT_HOME}/lib -lonnxruntime
```

---

## 11. Summary

To use ONNX Runtime 1.27.0, run:

```tcsh
source /home/user1/esl26/lib/ort_1270.csh
```

Then compile with:

```tcsh
-I${ORT_HOME}/include
-L${ORT_HOME}/lib
-lonnxruntime
-Wl,-rpath,${ORT_HOME}/lib
```
