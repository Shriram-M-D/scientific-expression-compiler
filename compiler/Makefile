# Makefile for Scientific Expression Compiler

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
TARGET = compiler
SOURCES = lexer.cpp parser.cpp ast.cpp evaluator.cpp calculus.cpp main.cpp
OBJECTS = $(SOURCES:.cpp=.o)

# Default target
all: $(TARGET)

# Link object files to create executable
$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJECTS)

# Compile source files to object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TARGET) $(TARGET).exe

# Rebuild from scratch
rebuild: clean all

# Run the compiler with a test expression
test:
	./$(TARGET) "sin(pi/4) + cos(pi/4)"

# Help target
help:
	@echo "Available targets:"
	@echo "  all      - Build the compiler (default)"
	@echo "  clean    - Remove build artifacts"
	@echo "  rebuild  - Clean and build from scratch"
	@echo "  test     - Run a test expression"
	@echo "  help     - Show this help message"

.PHONY: all clean rebuild test help
