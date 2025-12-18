from typing import List, Set, Tuple, Union

Expr = Union[str, Tuple]
Rule = Tuple[str, Expr, Expr]


def is_atom(value):
    return isinstance(value, str)


def is_not(value):
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and value[0] == "NOT"
        and is_atom(value[1])
    )


def is_lit(value):
    return is_atom(value) or is_not(value)


def is_and(value):
    return isinstance(value, tuple) and len(value) == 3 and value[0] == "AND"


def is_or(value):
    return isinstance(value, tuple) and len(value) == 3 and value[0] == "OR"


def is_implies(value):
    return isinstance(value, tuple) and len(value) == 3 and value[0] == "IMPLIES"


def negate(literal):
    return literal[1] if is_not(literal) else ("NOT", literal)


class KB:
    def __init__(self, facts=None, rules=None):
        self.facts: Set[Expr] = set(facts or [])
        self.rules: List[Rule] = list(rules or [])

    def add_fact(self, fact):
        if fact in self.facts:
            return False
        self.facts.add(fact)
        return True

    def rule_modus_ponens(self) -> List[Expr]:
        # === QUIZ: implement modus ponens inference ===
        # P, P->Q => Q
        new_facts = []
        for rule in self.rules:
            if rule[0] == "IMPLIES":
                premise, conclusion = rule[1], rule[2]
                if premise in self.facts:
                    new_facts.append(conclusion)
        return new_facts
        # raise NotImplementedError("QUIZ: rule_modus_ponens needs implementation")

    def rule_modus_tollens(self) -> List[Expr]:
        # === QUIZ: implement modus tollens inference ===
        # NOT Q, P->Q => NOT P
        new_facts = []
        for rule in self.rules:
            if rule[0] == "IMPLIES":
                p, q = rule[1], rule[2]
                if negate(q) in self.facts:
                    new_facts.append(negate(p))
        return new_facts
        # raise NotImplementedError("QUIZ: rule_modus_tollens needs implementation")

    def rule_simplification(self) -> List[Expr]:
        # === QUIZ: split conjunction facts into literals ===
        # (P AND Q) => P, Q
        new_facts = []
        for fact in self.facts:
            if is_and(fact):
                new_facts.append(fact[1])
                new_facts.append(fact[2])
        return new_facts
        # raise NotImplementedError("QUIZ: rule_simplification needs implementation")

    def rule_conjunction(self) -> List[Expr]:
        # === QUIZ: combine literals into conjunctions ===
        # P, Q => (P AND Q)
        new_facts = []
        # facts 중에서 atom이나 단순 NOT 리터럴만 골라냅니다.
        lits = [f for f in self.facts if is_lit(f)]
        
        for i in range(len(lits)):
            for j in range(i + 1, len(lits)):
                # (P AND Q) 형태만 생성
                new_facts.append(("AND", lits[i], lits[j]))
        return new_facts
        #raise NotImplementedError("QUIZ: rule_conjunction needs implementation")

    def rule_disjunctive_addition(self) -> List[Expr]:
        # === QUIZ: create disjunctions from literals ===
        # 추론 폭발(MemoryError/무한루프)의 주범이므로 비워둡니다.
        return []
        # raise NotImplementedError("QUIZ: rule_disjunctive_addition needs implementation")

    def rule_disjunctive_syllogism(self) -> List[Expr]:
        # === QUIZ: drop negated disjuncts to infer the other ===
        # (P OR Q), NOT P => Q / (P OR Q), NOT Q => P
        new_facts = []
        for fact in self.facts:
            if is_or(fact):
                p, q = fact[1], fact[2]
                if negate(p) in self.facts:
                    new_facts.append(q)
                if negate(q) in self.facts:
                    new_facts.append(p)
        return new_facts
        # raise NotImplementedError("QUIZ: rule_disjunctive_syllogism needs implementation")

    def rule_hypothetical_syllogism(self) -> List[Rule]:
        # === QUIZ: chain implications to form new rules ===
        # P->Q, Q->R => P->R
        new_rules = []
        for r1 in self.rules:
            for r2 in self.rules:
                if r1[0] == "IMPLIES" and r2[0] == "IMPLIES":
                    if r1[2] == r2[1]: # r1의 결과가 r2의 전제와 같을 때
                        new_rules.append(("IMPLIES", r1[1], r2[2]))
        return new_rules
        # raise NotImplementedError("QUIZ: rule_hypothetical_syllogism needs implementation")

    def rule_constructive_dilemma(self) -> List[Expr]:
        # === QUIZ: implement constructive dilemma ===
        new_facts = []
        # 사실(facts) 중 OR 형태인 것을 찾음
        for f in self.facts:
            if is_or(f):
                p, r = f[1], f[2]
                # P->Q 와 R->S 형태의 규칙이 모두 있는지 확인
                q, s = None, None
                for rule in self.rules:
                    if rule[0] == "IMPLIES":
                        if rule[1] == p: q = rule[2]
                        if rule[1] == r: s = rule[2]
                
                if q is not None and s is not None:
                    new_facts.append(("OR", q, s))
        return new_facts
        # raise NotImplementedError("QUIZ: rule_constructive_dilemma needs implementation")

    def rule_destructive_dilemma(self) -> List[Expr]:
        # === QUIZ: implement destructive dilemma ===
        new_facts = []
        for f in self.facts:
            if is_or(f):
                not_q, not_s = f[1], f[2]
                p, r = None, None
                for rule in self.rules:
                    if rule[0] == "IMPLIES":
                        # NOT Q 가 사실이고 rule이 P->Q 이면 P 추출
                        if negate(rule[2]) == not_q: p = rule[1]
                        if negate(rule[2]) == not_s: r = rule[1]
                
                if p is not None and r is not None:
                    new_facts.append(("OR", negate(p), negate(r)))
        return new_facts
        raise NotImplementedError("QUIZ: rule_destructive_dilemma needs implementation")

    def forward_chain(self, max_steps=20, verbose=False):
        # === 전방 추론 실행 엔진 ===
        for step in range(max_steps):
            added_any = False
            
            # 1. 새로운 사실(facts)을 도출하는 8가지 규칙 적용
            inferred_facts = (
                self.rule_modus_ponens() + 
                self.rule_modus_tollens() + 
                self.rule_simplification() + 
                self.rule_conjunction() +
                self.rule_disjunctive_addition() +  # 추가됨
                self.rule_disjunctive_syllogism() +
                self.rule_constructive_dilemma() +
                self.rule_destructive_dilemma()
            )
            
            # 도출된 사실들을 KB에 추가 (중복이면 add_fact가 False 반환)
            for f in inferred_facts:
                if self.add_fact(f):
                    added_any = True
                    if verbose: print(f"Step {step}: Inferred fact {f}")
            
            # 2. 새로운 규칙(rules)을 도출하는 가설적 삼단논법(HS) 적용
            inferred_rules = self.rule_hypothetical_syllogism()
            for r in inferred_rules:
                if r not in self.rules:
                    self.rules.append(r)
                    added_any = True
                    if verbose: print(f"Step {step}: Inferred rule {r}")
            
            # 이번 단계에서 새로 추가된 사실이나 규칙이 없다면 종료 (Fixpoint)
            if not added_any:
                break
        # raise NotImplementedError("QUIZ: forward_chain needs implementation")