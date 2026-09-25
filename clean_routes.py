import sys

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Let's find the first route and remove it
import re

# Match the old ImpactReportRequest class
old_model_regex = r'class ImpactReportRequest\(BaseModel\):\n\s+challenge_data: Dict\[str, Any\]\n\s+solution_data: Dict\[str, Any\]\n\s+feedback_list: List\[str\]'
code = re.sub(old_model_regex, "", code)

# Match the old route
old_route_regex = r'@app\.post\("/generate-impact-report"\)\ndef generate_impact_report_endpoint\(request: ImpactReportRequest\):\n\s+report = generate_impact_report\(request\.challenge_data, request\.solution_data, request\.feedback_list\)\n\s+if not isinstance\(report, str\) or not report\.strip\(\) or report\.startswith\(\("Error", "Failed", "Unexpected"\)\):\n\s+raise HTTPException\(status_code=500, detail="Failed to generate AI impact report"\)\n\s+return \{"markdown": report\}'
code = re.sub(old_route_regex, "", code)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Removed old route!")
