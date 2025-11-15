#  Makefile for Assignment 4

CC = g++
CXXFLAGS = -O1 -Wall -c
LDFLAGS = -O1 -Wall
HDR = Node.h List.h
SRC = main.cpp
OBJ = main.o
TARGET = list

all: $(TARGET)

main.o: main.cpp $(HDR)
	$(CC) $(CXXFLAGS) main.cpp

$(TARGET): $(OBJ)
	$(CC) $(LDFLAGS) $(OBJ) -o $@

clean:
	rm -f $(OBJ)
	rm -f $(TARGET)