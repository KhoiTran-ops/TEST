"""Command line entry point."""
import argparse, json
from pipeline.health_check import check_health
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.scheduler import run_scheduled

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--mode",choices=["pipeline","scheduler","health-check"],default="pipeline"); args=parser.parse_args()
    if args.mode=="scheduler": run_scheduled()
    else: print(json.dumps(PipelineOrchestrator().run() if args.mode=="pipeline" else check_health(),default=str,indent=2))
if __name__=="__main__": main()
