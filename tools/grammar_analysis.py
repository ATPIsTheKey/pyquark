quark_grammar_ll1 = {
    None: [['program']],
    'Expr': [['Let_Expr', 'Fun_Expr', 'Lambda_Expr', 'If_Then_Expr', 'Application_Expr', 'Logical_Expr']],
    'Let_Expr': [['LET', 'ID', 'EQUAL', 'Expr', 'IN', 'Expr']],
    'Fun_Expr': [['FUN', 'ID', 'WITH', 'Id_List', 'EQUAL', 'Expr_List', 'IN', 'Expr']],
    'If_Then_Expr': [['IF', 'Expr', 'THEN', 'Expr', 'THEN', 'Expr', 'ELSE', 'Expr']],
    'Lambda_Expr': [['LAMBDA', 'Id_List', 'PERIOD', 'Expr']],
    'Application_Expr': [['Expr', 'ON', 'Expr_List']],
    'Or_Expr': [['And_Expr', 'Or_Expr_Rhs']],
    'Or_Expr_Rhs': [['OR', 'And_Expr', 'Or_Expr_Rhs'], [None]],
    'And_Expr': [['Not_Expr', 'And_Expr_Rhs']],
    'And_Expr_Rhs': [['AND', 'NotExpr', 'And_Expr_Rhs'], [None]],
    'Not_Expr': [['NOT', 'Not_Expr'], ['Comp_Expr']],
    'Comp_Expr': [['Arith_Expr', 'Comp_Expr_Rhs']],
    'Comp_Expr_Rhs': [['COMP_BIN_OP', 'Arith_Expr', 'Comp_Expr_Rhs'], [None]],
    'Arith_Expr': [['Term_Expr', 'Arith_Expr_Rhs']],
    'Arith_Expr_Rhs': [['ARITH_BIN_OP', 'Term_Expr', 'Comp_Expr_Rhs'], [None]],
    'Term_Expr': [['Factor_Expr', 'Term_Expr_Rhs']],
    'Term_Expr_Rhs': [['TERM_BIN_OP', 'Factor_Expr', 'Term_Expr_Rhs'], [None]],
    'Factor_Expr': [['FACTOR_UN_OP', 'Factor_Expr'], ['Power_Expr']],
    'Power_Expr': [['Nil_Expr', 'Power_Expr_Rhs']],
    'Power_Expr_Rhs': [['DOUBLE_STAR', 'Nil_Expr', 'Power_Expr_Rhs'], [None]],
    'Nil_Expr': [['NIL', 'Nil_Expr'], ['List_Expr']],
    'List_Expr': [['List_Access_Expr', 'List_Expr_Rhs']],
    'List_Expr_Rhs': [['VERTICAL_BAR', 'List_Access_Expr', 'List_Expr_Rhs'], [None]],
    'List_Access_Expr': [['LIST_ACCESS_UN_OP', 'List_Access_Expr'], ['Atom_Expr']],
    'Atom_Expr': [['LEFT_PARENTHESIS', 'Expr_List', 'RIGHT_PARENTHESIS'], ['STRING'], ['NUMBER'], ['ID']],
    'Expr_List': [['Expr', 'Expr_List_Rhs']],
    'Expr_List_Rhs': [['COMMA', 'Expr', 'Expr_List_Rhs'], [None]],
    'ID_List': [['ID', 'ID_List_Rhs']],
    'ID_List_Rhs': [['COMMA', 'ID', 'ID_List_Rhs'], [None]]
}

quark_lexemes = {
    'ID', 'FACTOR_UN_OP', 'LIST_ACCESS_UN_OP', 'NIL', 'NOT', 'TERM_BIN_OP', 'COMMA', 'COMP_BIN_OP', 'AND', 'OR', 'IF',
    'ARITH_BIN_OP', 'THEN', 'ELSE', 'LET', 'WITH', 'IN', 'LAMBDA', 'FUN', 'ON', 'COMMA', 'PERIOD', 'LEFT_PARENTHESIS',
    'RIGHT_PARENTHESIS', 'LEFT_CURLY_BRACKET', 'RIGHT_CURLY_BRACKET', 'LEFT_BRACKET', 'RIGHT_BRACKET',  'NUMBER',
    'STRING', 'DOUBLE_STAR'
}


def format_grammar(grammar):
    for lhs, rhs in grammar:
        print("{} → {}".format(lhs or '⊤', " ".join(rhs)))


def format_item_set(grammar: dict, prefix: str, rule: str):
    fmt = rule
    ident = ' ' * len(rule)
    for alt in grammar[rule]:
        for i in range(len(alt)):
            fmt += f"→ [{' '.join(prod[:] + '•' + prod[:])}\n{ident}]"

    return fmt
