import streamlit as st
from pipeline.health_check import check_health
from pipeline.orchestrator import PipelineOrchestrator

def render(repository):
    st.header("Pipeline Monitor"); health=check_health(repository=repository)
    a,b,c=st.columns(3); a.metric("Database",health["database"]); b.metric("CafeF source",health["source"]); c.metric("Pipeline",health["last_pipeline_status"])
    st.json({k:str(v) for k,v in health.items()}); last=repository.latest_run()
    if last:
        st.dataframe({"Metric":["Last run","Dataset date","Downloaded","Inserted","Updated","Skipped","Duration"],"Value":[last.started_at,last.dataset_date,last.records_downloaded,last.records_inserted,last.records_updated,last.records_skipped,last.duration_seconds]})
    confirm=st.checkbox("I confirm that I want to run the pipeline")
    if st.button("Run Pipeline Now",disabled=not confirm):
        with st.status("Running pipeline…",expanded=True) as status:
            result=PipelineOrchestrator(repository=repository).run(); status.update(label=f"Pipeline {result['status']}",state="complete" if result["status"] in ["SUCCESS","NO_NEW_DATA"] else "error")
        st.cache_data.clear(); st.json(result)
