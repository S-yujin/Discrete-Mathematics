from typing import Set, Tuple, Union

Expr = Union[str, Tuple[str, str]]


def is_atom(value):
    return isinstance(value, str)


def is_not(value):
    # === QUIZ: implement NOT predicate detection ===
    return isinstance(value, tuple) and len(value) == 2 and value[0] == 'NOT'
    # raise NotImplementedError("QUIZ: is_not needs implementation")


def is_lit(value):
    # === QUIZ: determine if a value is a literal (atom or NOT(atom)) ===
    return is_atom(value) or is_not(value) 
    # raise NotImplementedError("QUIZ: is_lit needs implementation")


def negate(literal):
    # === QUIZ: return the logical negation of a literal ===
    if is_atom(literal):
        return ("NOT", literal)
    elif is_not(literal):
        return literal[1]
    return None
    raise NotImplementedError("QUIZ: negate needs implementation")


class KB:
    def __init__(self):
        self.facts: Set[Expr] = set()

    def add_fact(self, fact: Expr) -> bool:
        # === QUIZ: validate and insert a literal fact into the KB ===
        if not is_lit(fact): 
            return False
        
        if negate(fact) in self.facts:
            raise ValueError(f"Contradictory fact: {fact} vs {negate(fact)}") # 모순 검사
        if fact in self.facts:
            return False # 이미 존재하는 사실
        self.facts.add(fact)
        return True
    # raise NotImplementedError("QUIZ: add_fact needs implementation")