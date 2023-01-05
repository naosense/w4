#!/usr/bin/env python
# -.- coding: utf-8 -.-
META_CHAR = ['(', ')', '!', '&', '|']
LEFT_PAREN = 'LEFT_PARA'
RIGHT_PAREN = 'RIGHT_PARA'
NOT_OP = 'NOT_OP'
AND_OP = 'AND_OP'
OR_OP = 'OR_OP'
LITERAL = 'LITERAL'


class Expression:
    def __init__(self, exp):
        self.exp = exp
        self.tokens = Expression.__lex(exp)
        self.prefix_tokens = Expression.__infix_to_prefix(self.tokens)
        self.tree = Expression.__treefy(iter(self.prefix_tokens))

    @staticmethod
    def __lex(exp):
        tokens = []
        p = 0
        while p < len(exp):
            c = exp[p]
            if c == '(':
                tokens.append(Token(LEFT_PAREN, '('))
            elif c == ')':
                tokens.append(Token(RIGHT_PAREN, ')'))
            elif c == '!':
                if exp[p + 1] != '=':
                    tokens.append(Token(NOT_OP, '!'))
            elif c == '&':
                tokens.append(Token(AND_OP, '&'))
            elif c == '|':
                tokens.append(Token(OR_OP, '|'))
            else:
                s = c
                p += 1
                while p < len(exp):
                    c = exp[p]
                    if c not in META_CHAR or p + 1 < len(exp) and exp[p + 1] == '=':
                        s += c
                        p += 1
                    else:
                        p -= 1
                        break
                if s.strip():
                    tokens.append(Token(LITERAL, s.strip()))
            p += 1

        return tokens

    @staticmethod
    def __infix_to_prefix(tokens):
        queue = []
        stack = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token.name == LITERAL:
                queue.insert(0, token)
            elif token.name in [NOT_OP, OR_OP, AND_OP, LEFT_PAREN]:
                stack.append(token)
            elif token.name == RIGHT_PAREN:
                while stack[len(stack) - 1].name != LEFT_PAREN:
                    queue.append(stack.pop())
                stack.pop()
                if len(stack) > 0 and stack[len(stack) - 1].name == NOT_OP:
                    queue.append(stack.pop())
            index += 1
        queue.reverse()
        return queue

    @staticmethod
    def __treefy(tokens_iter):
        token = next(tokens_iter)
        if token is None:
            return None
        if token.name == LITERAL:
            tree = LogicTree(value=token.value)
            return tree
        elif token.name == NOT_OP:
            left = Expression.__treefy(tokens_iter)
            return LogicTree(op=NOT_OP, left=left)
        elif token.name == AND_OP:
            left = Expression.__treefy(tokens_iter)
            right = Expression.__treefy(tokens_iter)
            return LogicTree(op=AND_OP, left=left, right=right)
        elif token.name == OR_OP:
            left = Expression.__treefy(tokens_iter)
            right = Expression.__treefy(tokens_iter)
            return LogicTree(op=OR_OP, left=left, right=right)
        else:
            return None

    def predicate(self, event_dict):
        return Expression.__predicate(self.tree, event_dict)

    @staticmethod
    def __predicate(node, event_dict):
        """
        :param: event_dict e.g. {'who':[], 'what':'', 'when':'', 'where':'', 'link':[]}
        :rtype: bool
        """
        if node.op is None:
            if '!=' in node.value:
                kv = node.value.split('!=')
                col_val = event_dict[kv[0].strip()]
                if isinstance(col_val, list):
                    for v in col_val:
                        if kv[1].strip() in v:
                            return False
                    return True
                else:
                    return not kv[1].strip() in col_val
            elif '=' in node.value:
                kv = node.value.split('=')
                col_val = event_dict[kv[0].strip()]
                if isinstance(col_val, list):
                    for v in col_val:
                        if kv[1].strip() in v:
                            return True
                    return False
                else:
                    return kv[1].strip() in col_val
        else:
            if node.op == NOT_OP:
                return not Expression.__predicate(node.left, event_dict)
            elif node.op == AND_OP:
                return Expression.__predicate(node.left, event_dict) and Expression.__predicate(node.right, event_dict)
            elif node.op == OR_OP:
                return Expression.__predicate(node.left, event_dict) or Expression.__predicate(node.right, event_dict)


class Token:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return '<' + self.name + ',' + self.value + '>'


class LogicTree:
    def __init__(self, op=None, left=None, right=None, value=None):
        self.op = op
        self.left = left
        self.right = right
        self.value = value

    def __str__(self):
        s = []
        LogicTree.__infix(s, self)
        return ' '.join(s)

    @staticmethod
    def __infix(s, node):
        if node.op is None:
            s.append(node.value)
        else:
            if node.op == NOT_OP:
                s.append('!(')
                LogicTree.__infix(s, node.left)
                s.append(')')
            elif node.op == AND_OP:
                s.append('(')
                LogicTree.__infix(s, node.left)
                s.append('&')
                LogicTree.__infix(s, node.right)
                s.append(')')
            elif node.op == OR_OP:
                s.append('(')
                LogicTree.__infix(s, node.left)
                s.append('|')
                LogicTree.__infix(s, node.right)
                s.append(')')

# if __name__ == '__main__':
#     e = Expression('(who=武松 | who!=西门庆)')
#     for t in e.tokens:
#         print(t, end=' ')
#     print('\n---')
#     for t in e.prefix_tokens:
#         print(t, end=' ')
#     print('\n---')
#     print(e.tree)
#     print(e.predicate(
#         {'what': 'bbb', 'ln': 6, 'timestamp': '#0716105853', 'who': ['@西门庆', '@潘金莲'], 'when': '-', 'link': [],
#          'where': '-'}))
