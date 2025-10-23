#
#  Makefile for Assignment 3
#
#  by Alan Su
#  alansuphd@mail.ncku.edu.tw
#

CC = g++
PCFLAG = -O1 -Wall -c
POFLAG = -O1 -Wall
HDR = Node.h List.h
SRC = ${HDR:.h=.cpp} main.cpp
OBJ = ${HDR:.h=.o} main.o
TARGET = list

all: $(TARGET)
Node.o: Node.h Node.cpp
	$(CC) $(PCFLAG) $(@:.o=.cpp)
List.o: List.h List.cpp
	$(CC) $(PCFLAG) $(@:.o=.cpp)
main.o: main.cpp
	$(CC) $(PCFLAG) $(@:.o=.cpp)
$(TARGET): $(OBJ)
	$(CC) $(POFLAG) $(LIB) $(OBJ) -o $@

clean:
	rm $(OBJ)
	rm $(TARGET)
