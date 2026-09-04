from pathlib import Path
from analysis.indicators import calculate_indicators
from analysis.strategy import generate_signals
from pipeline.orchestrator import PipelineOrchestrator

class Source:
    def __init__(self,path,available=True): self.path,self.ok=path,available
    def available(self): return self.ok
    def download(self): return self.path
    def extract(self,path): return [path]

def test_indicators_and_signal_domain(prices):
    result=generate_signals(calculate_indicators(prices))
    assert {"sma20","sma50","ema20","rsi14","macd","atr14","volume_ma20"} <= set(result)
    assert set(result.signal) <= {"BUY","SELL","HOLD"}

def test_pipeline_second_run_is_no_new_data(repository,settings,prices,tmp_path):
    path=tmp_path/"source.csv"; prices.to_csv(path,index=False); runner=PipelineOrchestrator(repository,Source(path),settings)
    assert runner.run()["status"]=="SUCCESS"
    result=runner.run(); assert result["status"]=="NO_NEW_DATA" and result["records_inserted"]==0

def test_failure_is_audited_and_logged(repository,settings,tmp_path):
    result=PipelineOrchestrator(repository,Source(Path("missing"),False),settings).run()
    assert result["status"]=="FAILED" and "SOURCE_UNAVAILABLE" in result["error_message"]
    assert "Pipeline failed" in (tmp_path/"logs/pipeline.log").read_text()

def test_running_guard(repository,settings):
    repository.start_run("existing")
    result=PipelineOrchestrator(repository,Source(Path("unused")),settings).run()
    assert result["status"]=="ALREADY_RUNNING"
