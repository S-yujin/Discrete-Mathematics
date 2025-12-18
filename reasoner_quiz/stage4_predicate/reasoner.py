from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
)


Term = object
Predicate = Tuple[str, ...]
Substitution = Dict[str, Term]


def is_variable(term: Term) -> bool:
    return isinstance(term, str) and term.startswith("?")


def substitute(expr: Term, subs: Substitution) -> Term:
    if isinstance(expr, str):
        return subs.get(expr, expr)
    if isinstance(expr, tuple):
        return tuple(substitute(part, subs) for part in expr)
    return expr


def occurs_check(var: str, value: Term, subs: Substitution) -> bool:
    if var == value:
        return True
    if isinstance(value, str) and is_variable(value) and value in subs:
        return occurs_check(var, subs[value], subs)
    if isinstance(value, tuple):
        return any(occurs_check(var, part, subs) for part in value)
    return False


def unify(x: Term, y: Term, subs: Optional[Substitution] = None) -> Optional[Substitution]:
    if subs is None:
        subs = {}
    x = substitute(x, subs)
    y = substitute(y, subs)
    if x == y:
        return subs
    if is_variable(x):
        return unify_var(x, y, subs)
    if is_variable(y):
        return unify_var(y, x, subs)
    if isinstance(x, tuple) and isinstance(y, tuple):
        if len(x) != len(y):
            return None
        for x_part, y_part in zip(x, y):
            subs = unify(x_part, y_part, subs)
            if subs is None:
                return None
        return subs
    return None


def unify_var(var: str, value: Term, subs: Substitution) -> Optional[Substitution]:
    if var in subs:
        return unify(subs[var], value, subs)
    if is_variable(value) and value in subs:
        return unify(var, subs[value], subs)
    if occurs_check(var, value, subs):
        return None
    new_subs = subs.copy()
    new_subs[var] = value
    return new_subs


def is_ground(fact: Predicate) -> bool:
    return all(not (isinstance(arg, str) and is_variable(arg)) for arg in fact)


def is_exists(expr: Term) -> bool:
    return isinstance(expr, tuple) and len(expr) == 3 and expr[0] == "EXISTS"


@dataclass
class Rule:
    variables: Tuple[str, ...]
    premises: Tuple[Predicate, ...]
    conclusion: Term


class KB:
    def __init__(
        self,
        facts: Optional[Iterable[Predicate]] = None,
        rules: Optional[Iterable[Term]] = None,
    ) -> None:
        self.facts: Set[Predicate] = set()
        self.rules: List[Rule] = []
        self._exist_counter = 0
        # === 수정: 초기 인자로 들어온 사실과 규칙을 등록함 ===
        if facts:
            for f in facts:
                self.add_fact(f)
        if rules:
            for r in rules:
                self.add_rule(r)

    def add_fact(self, fact: Predicate) -> bool:
        if fact in self.facts:
            return False
        self.facts.add(fact)
        return True

    def add_rule(self, rule: Term) -> None:
        parsed = rule if isinstance(rule, Rule) else self._parse_rule(rule)
        self.rules.append(parsed)

    def forward_chain(self, max_iterations: int = 50) -> None:
        for _ in range(max_iterations):
            added_any = False
            for rule in self.rules:
                for subs in self._satisfying_substitutions(rule.premises):
                    conclusion = rule.conclusion
                    
                    # === 수정 포인트: EXISTS 처리 로직 ===
                    if is_exists(conclusion):
                        # 이미 이 결론을 만족하는 사실이 하나라도 있는지 확인 (매우 중요)
                        # 예: (?x: mia)일 때 ("loves", "mia", ?y) 형태의 사실이 이미 있는지 query
                        pattern = substitute(conclusion[2], subs)
                        if self.query(pattern):
                            continue # 이미 있으면 새로운 스콜렘 상수를 만들지 않고 건너뜀
                        
                        new_fact = self._instantiate_exists(substitute(conclusion, subs))
                    else:
                        new_fact = substitute(conclusion, subs)
                    
                    if self.add_fact(new_fact):
                        added_any = True
            
            if not added_any:
                break

    def query(self, pattern: Predicate) -> List[Substitution]:
        results = []
        for fact in self.facts:
            subs = unify(pattern, fact)
            if subs is not None:
                results.append(subs)
        return results

    def _satisfying_substitutions(self, premises: Sequence[Predicate]) -> Iterator[Substitution]:
        def recursive_search(idx: int, current_subs: Substitution) -> Iterator[Substitution]:
            if idx == len(premises):
                yield current_subs
                return
            current_premise = substitute(premises[idx], current_subs)

            for fact in list(self.facts): 
                new_subs = unify(current_premise, fact, current_subs.copy())
                if new_subs is not None:
                    yield from recursive_search(idx + 1, new_subs)
        return recursive_search(0, {})

    def _instantiate_exists(self, expr: Term) -> Predicate:
        # === 수정: 변수가 리스트 ["?y"]로 들어오는 경우를 처리함 ===
        vars_to_replace = expr[1]
        if isinstance(vars_to_replace, str):
            vars_to_replace = [vars_to_replace]
            
        predicate_template = expr[2]
        subs = {}
        for var in vars_to_replace:
            # 테스트 케이스가 요구하는 "_sk" 접두사 사용
            skolem_constant = f"_sk{self._exist_counter}"
            self._exist_counter += 1
            subs[var] = skolem_constant
        return substitute(predicate_template, subs)

    def _parse_rule(self, expr: Term) -> Rule:
        if isinstance(expr, tuple) and expr[0] == "FORALL":
            variables = tuple(expr[1])
            content = expr[2]
            if isinstance(content, tuple) and content[0] == "IMPLIES":
                premises = self._normalize_premises(content[1])
                conclusion = content[2]
                return Rule(variables=variables, premises=premises, conclusion=conclusion)
        raise ValueError(f"Invalid rule format: {expr}")

    def _normalize_premises(self, raw: Term) -> Tuple[Predicate, ...]:
        if isinstance(raw, list):
            return tuple(raw)
        if isinstance(raw, tuple) and raw[0] == "AND":
            return (raw[1], raw[2])
        return (raw,)


__all__ = ["KB", "Rule", "unify", "substitute", "is_variable"]