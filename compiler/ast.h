#ifndef AST_H
#define AST_H

#include <string>
#include <vector>
#include <memory>
#include "lexer.h"

// AST Node Types
enum class ASTNodeType {
    NUMBER,
    VARIABLE,
    BINARY_OP,
    UNARY_OP,
    FUNCTION_CALL,
    DIFF_NODE,
    INTEGRATE_NODE
};

// Base AST Node
class ASTNode {
public:
    ASTNodeType type;
    virtual ~ASTNode() = default;
    virtual std::string toString() const = 0;
    
protected:
    ASTNode(ASTNodeType t) : type(t) {}
};

// Number Node
class NumberNode : public ASTNode {
public:
    double value;
    
    NumberNode(double v) : ASTNode(ASTNodeType::NUMBER), value(v) {}
    std::string toString() const override;
};

// Variable Node
class VariableNode : public ASTNode {
public:
    std::string name;
    
    VariableNode(const std::string& n) : ASTNode(ASTNodeType::VARIABLE), name(n) {}
    std::string toString() const override;
};

// Binary Operation Node
class BinaryOpNode : public ASTNode {
public:
    std::string op;
    std::shared_ptr<ASTNode> left;
    std::shared_ptr<ASTNode> right;
    
    BinaryOpNode(const std::string& operation, 
                 std::shared_ptr<ASTNode> l, 
                 std::shared_ptr<ASTNode> r)
        : ASTNode(ASTNodeType::BINARY_OP), op(operation), left(l), right(r) {}
    std::string toString() const override;
};

// Unary Operation Node
class UnaryOpNode : public ASTNode {
public:
    std::string op;
    std::shared_ptr<ASTNode> operand;
    
    UnaryOpNode(const std::string& operation, std::shared_ptr<ASTNode> oper)
        : ASTNode(ASTNodeType::UNARY_OP), op(operation), operand(oper) {}
    std::string toString() const override;
};

// Function Call Node
class FunctionCallNode : public ASTNode {
public:
    std::string name;
    std::vector<std::shared_ptr<ASTNode>> arguments;
    
    FunctionCallNode(const std::string& n) 
        : ASTNode(ASTNodeType::FUNCTION_CALL), name(n) {}
    std::string toString() const override;
};

// Differentiation Node
class DiffNode : public ASTNode {
public:
    std::shared_ptr<ASTNode> expression;
    std::string variable;
    double point;
    
    DiffNode(std::shared_ptr<ASTNode> expr, const std::string& var, double pt)
        : ASTNode(ASTNodeType::DIFF_NODE), expression(expr), variable(var), point(pt) {}
    std::string toString() const override;
};

// Integration Node
class IntegrateNode : public ASTNode {
public:
    std::shared_ptr<ASTNode> expression;
    std::string variable;
    double lowerBound;
    double upperBound;
    
    IntegrateNode(std::shared_ptr<ASTNode> expr, const std::string& var, 
                  double lower, double upper)
        : ASTNode(ASTNodeType::INTEGRATE_NODE), expression(expr), 
          variable(var), lowerBound(lower), upperBound(upper) {}
    std::string toString() const override;
};

#endif // AST_H
