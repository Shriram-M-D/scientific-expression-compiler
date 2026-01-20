#include "lexer.h"
#include <cctype>
#include <cmath>
#include <stdexcept>

// Define constants if not available
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#ifndef M_E
#define M_E 2.71828182845904523536
#endif

Lexer::Lexer(const std::string& input) : input(input), position(0) {
    // Initialize function keywords
    functions["sin"] = TokenType::FUNCTION;
    functions["cos"] = TokenType::FUNCTION;
    functions["tan"] = TokenType::FUNCTION;
    functions["asin"] = TokenType::FUNCTION;
    functions["acos"] = TokenType::FUNCTION;
    functions["atan"] = TokenType::FUNCTION;
    functions["log"] = TokenType::FUNCTION;
    functions["ln"] = TokenType::FUNCTION;
    functions["exp"] = TokenType::FUNCTION;
    functions["sqrt"] = TokenType::FUNCTION;
    functions["cbrt"] = TokenType::FUNCTION;
    functions["abs"] = TokenType::FUNCTION;
    functions["diff"] = TokenType::FUNCTION;
    functions["integrate"] = TokenType::FUNCTION;
    
    // Combinatorics functions
    functions["nCr"] = TokenType::FUNCTION;
    functions["nPr"] = TokenType::FUNCTION;
    
    // Initialize constants
    constants["pi"] = M_PI;
    constants["e"] = M_E;
}

char Lexer::currentChar() {
    if (position >= input.length()) return '\0';
    return input[position];
}

char Lexer::peek(int offset) {
    size_t pos = position + offset;
    if (pos >= input.length()) return '\0';
    return input[pos];
}

void Lexer::advance() {
    position++;
}

void Lexer::skipWhitespace() {
    while (std::isspace(currentChar())) {
        advance();
    }
}

Token Lexer::readNumber() {
    std::string number;
    bool hasDecimal = false;
    
    while (std::isdigit(currentChar()) || currentChar() == '.') {
        if (currentChar() == '.') {
            if (hasDecimal) break;
            hasDecimal = true;
        }
        number += currentChar();
        advance();
    }
    
    double value = std::stod(number);
    return Token(TokenType::NUMBER, number, value);
}

Token Lexer::readIdentifier() {
    std::string identifier;
    
    while (std::isalnum(currentChar()) || currentChar() == '_') {
        identifier += currentChar();
        advance();
    }
    
    // Check if it's a function
    if (functions.find(identifier) != functions.end()) {
        return Token(TokenType::FUNCTION, identifier);
    }
    
    // Check if it's a constant
    if (constants.find(identifier) != constants.end()) {
        return Token(TokenType::CONSTANT, identifier, constants[identifier]);
    }
    
    // Otherwise, it's a variable
    return Token(TokenType::VARIABLE, identifier);
}

std::vector<Token> Lexer::tokenize() {
    std::vector<Token> tokens;
    
    while (position < input.length()) {
        skipWhitespace();
        
        if (position >= input.length()) break;
        
        char c = currentChar();
        
        // Numbers
        if (std::isdigit(c) || (c == '.' && std::isdigit(peek()))) {
            tokens.push_back(readNumber());
        }
        // Identifiers (functions, constants, variables)
        else if (std::isalpha(c) || c == '_') {
            tokens.push_back(readIdentifier());
        }
        // Operators and punctuation
        else {
            Token token;
            switch (c) {
                case '+':
                    token = Token(TokenType::PLUS, "+");
                    token.precedence = 1;
                    break;
                case '-':
                    token = Token(TokenType::MINUS, "-");
                    token.precedence = 1;
                    break;
                case '*':
                    token = Token(TokenType::MULTIPLY, "*");
                    token.precedence = 2;
                    break;
                case '/':
                    token = Token(TokenType::DIVIDE, "/");
                    token.precedence = 2;
                    break;
                case '%':
                    token = Token(TokenType::MODULO, "%");
                    token.precedence = 2;
                    break;
                case '^':
                    token = Token(TokenType::POWER, "^");
                    token.precedence = 3;
                    token.rightAssociative = true;
                    break;
                case '!':
                    token = Token(TokenType::FACTORIAL, "!");
                    token.precedence = 4;
                    break;
                case '(':
                    token = Token(TokenType::LPAREN, "(");
                    break;
                case ')':
                    token = Token(TokenType::RPAREN, ")");
                    break;
                case ',':
                    token = Token(TokenType::COMMA, ",");
                    break;
                default:
                    throw std::runtime_error("Invalid character: " + std::string(1, c));
            }
            tokens.push_back(token);
            advance();
        }
    }
    
    tokens.push_back(Token(TokenType::END, ""));
    return tokens;
}

std::string Lexer::tokenTypeToString(TokenType type) {
    switch (type) {
        case TokenType::NUMBER: return "NUMBER";
        case TokenType::PLUS: return "PLUS";
        case TokenType::MINUS: return "MINUS";
        case TokenType::MULTIPLY: return "MULTIPLY";
        case TokenType::DIVIDE: return "DIVIDE";
        case TokenType::MODULO: return "MODULO";
        case TokenType::POWER: return "POWER";
        case TokenType::FACTORIAL: return "FACTORIAL";
        case TokenType::LPAREN: return "LPAREN";
        case TokenType::RPAREN: return "RPAREN";
        case TokenType::COMMA: return "COMMA";
        case TokenType::FUNCTION: return "FUNCTION";
        case TokenType::CONSTANT: return "CONSTANT";
        case TokenType::VARIABLE: return "VARIABLE";
        case TokenType::END: return "END";
        default: return "INVALID";
    }
}
