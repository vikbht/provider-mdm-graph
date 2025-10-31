"""Provider MDM Engine implementing matching, merging, data quality, and graph operations."""
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from neo4j import GraphDatabase
from pydantic import BaseModel
from models import Provider, ProviderComplete, MatchResult, DataQualityResult
from config import MATCHING_CONFIG, DATA_QUALITY_RULES, GRAPH_CONSTRAINTS, GRAPH_INDEXES, Neo4jConnection
import re

class ProviderMDMEngine:
    def __init__(self, conn: Neo4jConnection):
        self.conn = conn

    # ---------------- Graph Setup ----------------
    def bootstrap_graph(self) -> None:
        for cypher in GRAPH_CONSTRAINTS + GRAPH_INDEXES:
            self.conn.execute_query(cypher)

    # ---------------- Ingestion ----------------
    def upsert_provider(self, p: Provider) -> Dict:
        cypher = """
        MERGE (pr:Provider {npi: $npi})
        ON CREATE SET pr += $props, pr.created_at = datetime(), pr.updated_at = datetime()
        ON MATCH SET  pr += $props, pr.updated_at = datetime()
        RETURN pr
        """
        props = p.model_dump(exclude_none=True)
        return self.conn.execute_query(cypher, {"npi": p.npi, "props": props})

    def upsert_location(self, loc: Dict) -> Dict:
        cypher = """
        MERGE (l:Location {location_id: $location_id})
        ON CREATE SET l += $props
        ON MATCH SET  l += $props
        RETURN l
        """
        return self.conn.execute_query(cypher, {"location_id": loc["location_id"], "props": loc})

    def link_provider_location(self, npi: str, location_id: str, rel: str = "PRACTICES_AT") -> None:
        cypher = """
        MATCH (p:Provider {npi:$npi}), (l:Location {location_id:$location_id})
        MERGE (p)-[r:%s]->(l)
        SET r.updated_at = datetime()
        """ % rel
        self.conn.execute_query(cypher, {"npi": npi, "location_id": location_id})

    # ---------------- Data Quality ----------------
    def check_data_quality(self, p: Provider) -> DataQualityResult:
        issues: List[str] = []
        for field, rule in DATA_QUALITY_RULES.items():
            val = getattr(p, field, None)
            if rule.get("required") and not val:
                issues.append(f"{field} is required")
                continue
            pattern = rule.get("pattern")
            if val and pattern and not re.match(pattern, str(val)):
                issues.append(f"{field} fails pattern check")
        score = max(0.0, 1.0 - (len(issues) * 0.1))
        return DataQualityResult(provider_npi=p.npi, is_valid=len(issues) == 0, issues=issues, quality_score=score)

    # ---------------- Matching ----------------
    def similarity(self, a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        a, b = a.lower().strip(), b.lower().strip()
        if a == b:
            return 1.0
        # simple token overlap similarity
        sa, sb = set(a.split()), set(b.split())
        if not sa or not sb:
            return 0.0
        return len(sa & sb) / len(sa | sb)

    def compute_match_score(self, p1: Provider, p2: Provider) -> Tuple[float, List[str]]:
        weights = MATCHING_CONFIG["weights"]
        attrs = []
        score = 0.0
        if p1.npi and p2.npi and p1.npi == p2.npi:
            score += weights.get("npi", 0)
            attrs.append("npi")
        name1 = f"{p1.first_name} {p1.last_name}".strip()
        name2 = f"{p2.first_name} {p2.last_name}".strip()
        s = self.similarity(name1, name2)
        score += s * weights.get("name", 0)
        if s > 0.9:
            attrs.append("name")
        if p1.license_number and p2.license_number and p1.license_number == p2.license_number:
            score += weights.get("license_number", 0)
            attrs.append("license_number")
        if p1.email and p2.email and p1.email.lower() == p2.email.lower():
            score += weights.get("email", 0)
            attrs.append("email")
        if p1.phone and p2.phone and re.sub(r"\D", "", p1.phone) == re.sub(r"\D", "", p2.phone):
            score += weights.get("phone", 0)
            attrs.append("phone")
        return score, attrs

    def match_providers(self, candidate: Provider) -> List[MatchResult]:
        q = """
        MATCH (p:Provider)
        RETURN p { .npi, .first_name, .last_name, .email, .phone, .license_number } AS p
        """
        records = self.conn.execute_query(q)
        results: List[MatchResult] = []
        for r in records:
            p = Provider(**{k: v for k, v in r["p"].items() if v is not None}, last_name=r["p"].get("last_name", ""), first_name=r["p"].get("first_name", ""))
            score, attrs = self.compute_match_score(candidate, p)
            thresholds = MATCHING_CONFIG["thresholds"]
            if score >= thresholds["exact_match"]:
                mtype, level, action = "exact", "high", "merge"
            elif score >= thresholds["high_confidence"]:
                mtype, level, action = "high", "high", "merge"
            elif score >= thresholds["medium_confidence"]:
                mtype, level, action = "medium", "medium", "review"
            elif score >= thresholds["low_confidence"]:
                mtype, level, action = "low", "low", "review"
            else:
                continue
            results.append(MatchResult(provider1_npi=candidate.npi, provider2_npi=p.npi, match_score=score, match_type=mtype, matching_attributes=attrs, confidence_level=level, recommended_action=action))
        return sorted(results, key=lambda x: x.match_score, reverse=True)

    # ---------------- Merge ----------------
    def merge_providers(self, source_npi: str, target_npi: str) -> None:
        cypher = """
        MATCH (s:Provider {npi:$source}), (t:Provider {npi:$target})
        CALL apoc.refactor.mergeNodes([s,t], {properties:"combine", mergeRels:true}) YIELD node
        SET node.is_golden_record = true, node.updated_at = datetime()
        """
        self.conn.execute_query(cypher, {"source": source_npi, "target": target_npi})

    # ---------------- Queries ----------------
    def get_provider(self, npi: str) -> Optional[Dict]:
        q = "MATCH (p:Provider {npi:$npi}) RETURN p"
        res = self.conn.execute_query(q, {"npi": npi})
        return res[0]["p"] if res else None

    def search_providers(self, text: str) -> List[Dict]:
        q = """
        MATCH (p:Provider)
        WHERE toLower(p.first_name) CONTAINS toLower($t)
           OR toLower(p.last_name) CONTAINS toLower($t)
           OR toLower(p.email) CONTAINS toLower($t)
        RETURN p LIMIT 50
        """
        return [r["p"] for r in self.conn.execute_query(q, {"t": text})]
