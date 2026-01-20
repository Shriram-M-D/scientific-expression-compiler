# Makefile for Scientific Expression Compiler

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
TARGET = compiler
SOURCES = lexer.cpp parser.cpp ast.cpp evaluator.cpp calculus.cpp main.cpp
OBJECTS = $(SOURCES:.cpp=.o)

# Object file analysis targets
ANALYSIS_SOURCES = lexer.cpp parser.cpp ast.cpp evaluator.cpp calculus.cpp
OBJECT_O0 = compiler_O0.o
OBJECT_O2 = compiler_O2.o

# Detect OS for proper clean command
ifeq ($(OS),Windows_NT)
    RM = del /Q
    TARGET_EXT = .exe
    CLEAN_FILES = *.o $(TARGET).exe
else
    RM = rm -f
    TARGET_EXT =
    CLEAN_FILES = $(OBJECTS) $(TARGET)
endif

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
	-@rm -f *.o compiler.exe compiler compiler_O0.o compiler_O2.o 2>/dev/null || true

# Rebuild from scratch
rebuild: clean all

# Build object files for analysis (both optimization levels)
analyze-objects: $(OBJECT_O0) $(OBJECT_O2)
	@echo "Object files built for analysis:"
	@echo "  $(OBJECT_O0) (no optimization)"
	@echo "  $(OBJECT_O2) (optimized)"

# Build object file with -O0 (no optimization)
$(OBJECT_O0): $(ANALYSIS_SOURCES)
	$(CXX) -std=c++17 -Wall -Wextra -O0 -c $(ANALYSIS_SOURCES)
	ld -r -o $(OBJECT_O0) $(ANALYSIS_SOURCES:.cpp=.o)
	@rm -f $(ANALYSIS_SOURCES:.cpp=.o)

# Build object file with -O2 (optimization)
$(OBJECT_O2): $(ANALYSIS_SOURCES)
	$(CXX) -std=c++17 -Wall -Wextra -O2 -c $(ANALYSIS_SOURCES)
	ld -r -o $(OBJECT_O2) $(ANALYSIS_SOURCES:.cpp=.o)
	@rm -f $(ANALYSIS_SOURCES:.cpp=.o)

# Run the compiler with a test expression
test:
	./$(TARGET) "sin(pi/4) + cos(pi/4)"

# Help target
help:
	@echo "Available targets:"
	@echo "  all              - Build the compiler (default)"
	@echo "  clean            - Remove build artifacts"
	@echo "  rebuild          - Clean and build from scratch"
	@echo "  test             - Run a test expression"
	@echo "  analyze-objects  - Build object files for machine-level analysis"
	@echo "  help             - Show this help message"

.PHONY: all clean rebuild test analyze-objects help

.PHONY: all clean rebuild test help
