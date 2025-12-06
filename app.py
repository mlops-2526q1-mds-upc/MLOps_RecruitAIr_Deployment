import os

import aws_cdk
from cdk.stack import RecruitAirEksStack, EksAlbStack

chart_path = "./recruitair"

if not os.path.exists(chart_path):
    raise FileNotFoundError(f"Could not find Helm chart at: {chart_path}")

app = aws_cdk.App()
# RecruitAirEksStack(app, "RecruitAirEksStack", chart_path)
EksAlbStack(app, "RecruitAirEksStack")
app.synth()