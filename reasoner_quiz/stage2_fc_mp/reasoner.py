from typing import List, Set, Tuple, Union

Expr = Union[str, Tuple[str, str]]
Rule = Tuple[str, Expr, Expr]


def is_atom(value):
    return isinstance(value, str)


def is_not(value):
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and value[0] == "NOT"
        and isinstance(value[1], str)
    )


def is_lit(value):
    return is_atom(value) or is_not(value)


def negate(literal):
    # === QUIZ: implement literal negation ===
    if is_atom(literal):
        return ("NOT", literal)
    elif is_not(literal):
        return literal[1]
    return None
    # raise NotImplementedError("QUIZ: negate needs implementation")


class KB:
    def __init__(self, facts=None, rules=None):
        self.facts: Set[Expr] = set(facts or [])
        self.rules: List[Rule] = list(rules or [])

    def add_fact(self, fact):
        # === QUIZ: enforce literal integrity before adding ===
        # 1. 리터럴 형식 검사
        if not is_lit(fact):
            return False
        
        # 2. 모순 검사
        opp = negate(fact)
        if opp in self.facts:
            raise ValueError(f"Contradictory fact: {fact} vs {opp}")
        
        # 3. 중복 검사 (이미 있으면 True를 반환하지 않고 종료)
        if fact in self.facts:
            return False
            
        # 4. 사실 추가 (이 부분이 실행되어야 함!)
        self.facts.add(fact)
        return True
        # raise NotImplementedError("QUIZ: add_fact needs implementation")

    def rule_modus_ponens(self) -> List[Expr]:
        # === QUIZ: derive new facts using modus ponens ===
        new_facts = []
        for rule in self.rules:
            # rule: ('IMPLIES', P, Q)
            if isinstance(rule, tuple) and rule[0] == "IMPLIES":
                premise, conclusion = rule[1], rule[2]
                # P가 사실이면 Q를 도출 후보에 추가
                if premise in self.facts:
                    new_facts.append(conclusion)
        return new_facts
        # raise NotImplementedError("QUIZ: rule_modus_ponens needs implementation")

    def forward_chain(self, max_steps=1000, verbose=False):
        # === QUIZ: drive forward chaining using inference rules ===
        for step in range(max_steps):
            added_any = False
            
            # 1. MP 규칙으로 도출 가능한 모든 사실을 가져옴
            inferred = self.rule_modus_ponens()
            
            # 2. 도출된 사실들을 하나씩 KB에 추가 시도
            for fact in inferred:
                # self.add_fact가 성공(새로운 사실 추가)하면 True를 반환함
                if self.add_fact(fact):
                    added_any = True
                    if verbose:
                        print(f"Step {step}: Inferred {fact}")
            
            # 3. 이번 턴에 새로 추가된 사실이 하나도 없다면 추론 종료
            if not added_any:
                break
        # raise NotImplementedError("QUIZ: forward_chain needs implementation")