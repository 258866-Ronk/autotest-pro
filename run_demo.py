"""One-command demo. Usage: python run_demo.py [sequential|parallel]"""
import sys, os
from autotest.cli import execute, parse_args

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sequential"
    args = parse_args(["--mode", mode])
    sys.exit(execute(args, root=os.path.dirname(os.path.abspath(__file__))))
