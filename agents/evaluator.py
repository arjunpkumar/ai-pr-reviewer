# # agents/evaluator.py
# from state import AgentState

# def run_evaluator(state: AgentState):
#     reports = state.get("reports", [])
    
#     # 1. Build the Markdown Table
#     table_header = "| Agent | Status | Severity | Findings |\n| :--- | :--- | :--- | :--- |\n"
#     table_rows = ""
    
#     any_fails = False
#     for report in reports:
#         status_emoji = "✅ PASS" if report["status"].upper() == "PASS" else "❌ FAIL"
#         if report["status"].upper() == "FAIL":
#             any_fails = True
            
#         table_rows += f"| {report['agent']} | {status_emoji} | {report['severity']} | {report['findings']} |\n"

#     # 2. Final Verdict
#     verdict_title = "## 🤖 AI Agent Review Summary\n\n"
#     verdict_status = "### 🚀 Verdict: Ready for Review" if not any_fails else "### 🛑 Verdict: Changes Requested"
    
#     final_summary = f"{verdict_title}{table_header}{table_rows}\n\n{verdict_status}"
    
#     return {
#         "final_summary": final_summary,
#         "deployment_ready": not any_fails
#     }