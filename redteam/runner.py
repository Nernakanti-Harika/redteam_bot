import time
import pandas as pd
from .judge import judge
from .probes import PROBES

def run(target, probes=PROBES) -> pd.DataFrame:
    rows = []
    for p in probes:
        t0 = time.time()
        try:
            resp = target.ask(p["prompt"])
        except Exception as e:
            resp = f"[ERROR] {e}"
        v = judge(p, resp)
        rows.append(dict(id=p["id"], category=p["category"], severity=p["severity"], prompt=p["prompt"],
                         response=resp, passed=v["passed"], reason=v["reason"],
                         latency_s=round(time.time() - t0, 2)))
    return pd.DataFrame(rows)

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    g = df.assign(failed=~df.passed, risk=(~df.passed) * df.severity).groupby("category")
    out = g.agg(probes=("id", "count"), failed=("failed", "sum"), risk=("risk", "sum")).reset_index()
    out["vuln_rate_%"] = (out.failed / out.probes * 100).round(1)
    return out.sort_values("vuln_rate_%", ascending=False)

def risk_score(df: pd.DataFrame) -> float:
    """0-100, severity-weighted share of failed probes."""
    return round(((~df.passed) * df.severity).sum() / df.severity.sum() * 100, 1)
