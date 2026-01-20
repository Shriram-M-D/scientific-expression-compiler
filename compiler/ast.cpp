#include "ast.h"
#include <sstream>

std::string NumberNode::toString() const {
    return std::to_string(value);
}

std::string VariableNode::toString() const {
    return name;
}

std::string BinaryOpNode::toString() const {
    std::ostringstream oss;
    oss << "(" << left->toString() << " " << op << " " << right->toString() << ")";
    return oss.str();
}

std::string UnaryOpNode::toString() const {
    std::ostringstream oss;
    oss << op << "(" << operand->toString() << ")";
    return oss.str();
}

std::string FunctionCallNode::toString() const {
    std::ostringstream oss;
    oss << name << "(";
    for (size_t i = 0; i < arguments.size(); i++) {
        if (i > 0) oss << ", ";
        oss << arguments[i]->toString();
    }
    oss << ")";
    return oss.str();
}

std::string DiffNode::toString() const {
    std::ostringstream oss;
    oss << "diff(" << expression->toString() << ", " << variable << ", " << point << ")";
    return oss.str();
}

std::string IntegrateNode::toString() const {
    std::ostringstream oss;
    oss << "integrate(" << expression->toString() << ", " << variable 
        << ", " << lowerBound << ", " << upperBound << ")";
    return oss.str();
}

std::string FactorialNode::toString() const {
    std::ostringstream oss;
    oss << "(" << operand->toString() << ")!";
    return oss.str();
}

std::string NCrNode::toString() const {
    std::ostringstream oss;
    oss << "nCr(" << n->toString() << ", " << r->toString() << ")";
    return oss.str();
}

std::string NPrNode::toString() const {
    std::ostringstream oss;
    oss << "nPr(" << n->toString() << ", " << r->toString() << ")";
    return oss.str();
}
