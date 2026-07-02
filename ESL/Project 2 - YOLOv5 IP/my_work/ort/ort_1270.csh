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
