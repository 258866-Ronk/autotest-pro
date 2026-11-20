"""Domain models. Plain dataclasses, no magic."""
from dataclasses import dataclass, field
from typing import Any, List, Dict


@dataclass
class RequestConfig:
    method: str = "GET"
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    body: Any = None


@dataclass
class Assertion:
    type: str = "status_code"      # status_code | json_path | body_contains | response_time
    path: str = ""                 # json_path only, e.g. $.data.token
    op: str = "eq"                 # eq/ne/gt/gte/lt/lte/contains/not_null
    expected: Any = None


@dataclass
class TestCase:
    name: str
    description: str = ""
    request: RequestConfig = field(default_factory=RequestConfig)
    assertions: List[Assertion] = field(default_factory=list)
    extract: Dict[str, str] = field(default_factory=dict)   # var_name -> json_path
    variables: Dict[str, Any] = field(default_factory=dict)
    data_source: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class AssertionResult:
    type: str
    path: str
    op: str
    expected: Any
    actual: Any
    passed: bool
    message: str = ""


@dataclass
class CaseResult:
    name: str
    passed: bool
    status_code: int
    response_time_ms: int
    assertions: List[AssertionResult] = field(default_factory=list)
    error: str = ""


@dataclass
class RunSummary:
    run_id: str
    environment: str
    base_url: str
    started_at: str
    duration_ms: int
    total: int
    passed: int
    failed: int
    pass_rate: float
    results: List[CaseResult] = field(default_factory=list)
