from __future__ import annotations

import re
import sys
import pandas as pd
from pathlib import Path
from typing import List, Sequence, Tuple

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "stage4_predicate"))

from reasoner import KB  # type: ignore

Fact = Tuple[str, ...]
Rule = Tuple

DEFAULT_FACTS = """parent(alice,bob)
parent(bob,carol)
parent(carol,dana)"""

DEFAULT_RULES = """forall x,y: parent(x,y) -> ancestor(x,y)
forall x,y,z: parent(x,y) & ancestor(y,z) -> ancestor(x,z)
forall x,y: ancestor(x,y) -> connected(x,y)"""

DEFAULT_QUERY = "ancestor(?who, dana)"


class ParseError(Exception):
    """Raised when the text-based KB format cannot be parsed."""


def parse_fact(line: str) -> Fact:
    # === QUIZ: parse a textual fact into predicate tuple ===
    line = line.strip().lower()
    if not line: return None
    # 'parent(alice,bob)' 에서 이름과 인자들을 추출
    match = re.match(r"(\w+)\((.*)\)", line)
    if not match:
        raise ParseError(f"Invalid fact format: {line}")
    pred_name, args_str = match.groups()
    args = tuple(arg.strip() for arg in args_str.split(","))
    return (pred_name, *args)
    # raise NotImplementedError("QUIZ: parse_fact needs implementation")


def parse_predicate(token: str, variables: Sequence[str]) -> Fact:
    # === QUIZ: parse predicate tokens, normalizing variables and constants ===
    token = token.strip().lower()
    match = re.match(r"(\w+)\((.*)\)", token)
    if not match: return (token,) # 단일 상수의 경우
    
    pred_name, args_str = match.groups()
    args = []
    for arg in args_str.split(","):
        arg = arg.strip()
        # 변수 리스트에 있으면 ?를 붙여 변수로 인식하게 함
        if arg in variables:
            args.append(f"?{arg}")
        else:
            args.append(arg)
    return (pred_name, *args)
    # raise NotImplementedError("QUIZ: parse_predicate needs implementation")


def parse_rule(line: str) -> Rule:
    # === QUIZ: translate surface rule syntax into Stage 4 format ===
    line = line.strip().lower()
    if "forall" not in line or "->" not in line:
        raise ParseError("Rule must contain 'forall' and '->'")
    
    # forall과 본문 분리
    header, body = line.split(":", 1)
    vars_str = header.replace("forall", "").strip()
    variables = [v.strip() for v in vars_str.split(",")]
    
    # 전제와 결론 분리
    premise_str, conclusion_str = body.split("->", 1)
    
    # 전제(AND로 연결된 경우 처리) 및 결론 파싱
    premises = [parse_predicate(p, variables) for p in premise_str.split("&")]
    conclusion = parse_predicate(conclusion_str, variables)
    
    return ("FORALL", variables, ("IMPLIES", premises, conclusion))
    # raise NotImplementedError("QUIZ: parse_rule needs implementation")


def parse_facts_block(text: str) -> List[Fact]:
    # === QUIZ: split multi-line facts and parse each line ===
    facts = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            facts.append(parse_fact(line))
    return facts
    # raise NotImplementedError("QUIZ: parse_facts_block needs implementation")


def parse_rules_block(text: str) -> List[Rule]:
    # === QUIZ: parse a block of rule lines ===
    rules = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            rules.append(parse_rule(line))
    return rules
    # raise NotImplementedError("QUIZ: parse_rules_block needs implementation")


def parse_query(text: str) -> Fact:
    # === QUIZ: parse a query string into predicate form ===
    # 쿼리는 변수 정의가 따로 없으므로 ?가 붙은 단어를 변수로 간주하여 파싱
    text = text.strip().lower()
    match = re.match(r"(\w+)\((.*)\)", text)
    if not match:
        raise ParseError(f"Invalid query format: {text}")
    
    pred_name, args_str = match.groups()
    args = []
    for arg in args_str.split(","):
        arg = arg.strip()
        # 이미 ?로 시작하면 변수로, 아니면 상수로 처리
        args.append(arg if arg.startswith("?") else arg)
    return (pred_name, *args)
    # raise NotImplementedError("QUIZ: parse_query needs implementation")


def main() -> None:
    # === QUIZ: build Streamlit UI that wires parsing to the KB ===
    st.set_page_config(page_title="Predicate Logic Reasoner", layout="wide")
    
    # 상단 헤더 섹션
    st.title("Predicate Logic Reasoner")
    st.info("지식 베이스(KB)를 구축하고 전방 추론(Forward Chaining)을 통해 새로운 사실을 도출합니다.")
    
    # 1. 입력 섹션: 사실과 규칙을 좌우로 배치
    st.subheader("Step 1: 지식 베이스(KB) 정의")
    input_col1, input_col2 = st.columns(2)
    with input_col1:
        facts_text = st.text_area("Facts (알려진 사실들)", DEFAULT_FACTS, height=150)
    with input_col2:
        rules_text = st.text_area("Rules (추론 규칙들)", DEFAULT_RULES, height=150)
    
    # 2. 질의 및 실행 섹션
    st.subheader("Step 2: 추론 실행 및 질의")
    query_col1, query_col2 = st.columns([3, 1])
    with query_col1:
        query_text = st.text_input("도출하고자 하는 목표 (Query):", DEFAULT_QUERY)
    with query_col2:
        st.write("") # 간격 맞춤용
        run_inference = st.button("추론 실행", use_container_width=True)

    if run_inference:
        kb = KB()
        try:
            # 데이터 파싱 및 로딩
            facts = parse_facts_block(facts_text)
            rules = parse_rules_block(rules_text)
            for f in facts: kb.add_fact(f)
            for r in rules: kb.add_rule(r)

            # 추론 엔진 가동
            with st.status("전방 추론 수행 중...", expanded=True) as status:
                kb.forward_chain()
                status.update(label="추론 완료!", state="complete", expanded=False)
            
            # 3. 결과 출력 섹션
            st.divider()
            res_col1, res_col2 = st.columns([1, 1.2])
            
            with res_col1:
                st.subheader("추론된 모든 사실")
                # 내부 튜플을 문자열로 변환하여 리스트로 출력
                processed_facts = [f"{f[0]}({', '.join(f[1:])})" for f in kb.facts]
                st.write(processed_facts) # 깔끔한 텍스트 리스트 형태

            with res_col2:
                st.subheader("질의 결과")
                query_pred = parse_query(query_text)
                results = kb.query(query_pred)
                
                if results:
                    # 결과를 표(Table)로 보여주면 변수 매칭을 확인하기 훨씬 편합니다.
                    st.dataframe(pd.DataFrame(results), use_container_width=True)
                    st.success(f"총 {len(results)}개의 일치하는 사실을 찾았습니다.")
                else:
                    st.warning("일치하는 결과가 없습니다.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
    # raise NotImplementedError("QUIZ: main needs implementation")


if __name__ == "__main__":
    main()