"""CLI entry point."""
import os, sys, time, uuid, argparse
from datetime import datetime, timezone
from .models import RunSummary
from .parser import load_cases, load_environment, expand_data
from .variable import VariableContext
from .http_client import HttpClient
from .mock_server import MockAPI
from .runner import run
from .report import write_all


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="autotest", description="AutoTest Pro CLI")
    p.add_argument("--root", default=None, help="project root (contains testcases/)")
    p.add_argument("--env", default="environments/default.yaml")
    p.add_argument("--out", default="reports")
    p.add_argument("--mode", choices=["sequential", "parallel"], default="sequential")
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--port", type=int, default=0, help="mock server port, 0 = random")
    p.add_argument("--base-url", default=None, help="override base url, disables mock")
    p.add_argument("--no-mock", action="store_true")
    p.add_argument("--report-json", default=None, help="explicit report.json output path")
    return p.parse_args(argv)


def execute(args, root=None):
    root = root or os.getcwd()
    tc_dir = args.root or os.path.join(root, "testcases")
    env_path = args.env if os.path.isabs(args.env) else os.path.join(root, args.env)
    env = load_environment(env_path) if os.path.exists(env_path) else {}

    mock = None
    base_url = args.base_url or env.get("baseUrl", "")
    if not args.no_mock and not base_url:
        mock = MockAPI(args.port)
        mock.start()
        base_url = mock.base_url
    client = HttpClient(base_url, timeout=env.get("timeout", 5))

    cases = expand_data(load_cases(tc_dir), tc_dir)
    initial = dict(env.get("variables") or {})
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    t0 = time.perf_counter()
    results = run(cases, client, VariableContext(initial), args.mode, args.threads)
    duration = int((time.perf_counter() - t0) * 1000)

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    summary = RunSummary(
        run_id="RUN-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6].upper(),
        environment=os.path.basename(env_path), base_url=base_url, started_at=started,
        duration_ms=duration, total=total, passed=passed, failed=total - passed,
        pass_rate=round(passed * 100.0 / total, 1) if total else 0.0, results=results,
    )
    out_dir = args.out if os.path.isabs(args.out) else os.path.join(root, args.out)
    write_all(summary, out_dir)
    if args.report_json:
        from .report import write_json
        dest = args.report_json
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        write_json(summary, dest)

    if mock:
        mock.close()

    print("=" * 56)
    print("Run %s | %s" % (summary.run_id, summary.environment))
    print("Total=%d Passed=%d Failed=%d PassRate=%.1f%% Duration=%dms"
          % (total, passed, total - passed, summary.pass_rate, duration))
    for r in results:
        print("  [%s] %s (%dms)" % ("PASS" if r.passed else "FAIL", r.name, r.response_time_ms))
    print("=" * 56)
    return 0 if summary.failed == 0 else 1


def main(argv=None):
    return execute(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
