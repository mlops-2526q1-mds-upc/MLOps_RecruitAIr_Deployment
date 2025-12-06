import json
import os

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_iam as iam,
)
from constructs import Construct

from aws_cdk.lambda_layer_kubectl_v33 import KubectlV33Layer


class EksAlbStack(Stack):
    def __init__(self, scope: Construct, id: str, *, env=None, **kwargs):
        super().__init__(scope, id, env=env, **kwargs)

        # 1) VPC
        vpc = ec2.Vpc(self, "EKS-VPC", max_azs=3)

        # 2) Create the EKS Cluster
        kubectl_layer = KubectlV33Layer(self, "kubectl")
        cluster = eks.Cluster(
            self,
            "RecruitAirCluster",
            vpc=vpc,
            version=eks.KubernetesVersion.V1_33,
            default_capacity=0,
            cluster_name="recruitair-cluster",
            kubectl_layer=kubectl_layer,
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
        )

        # Add managed nodegroup
        cluster.add_nodegroup_capacity("ng-1",
            desired_size=1,
            instance_types=[ec2.InstanceType("t3.micro")],
            ami_type=eks.NodegroupAmiType.AL2023_X86_64_STANDARD,
        )

        # 3) Create IAM policy for AWS Load Balancer Controller
        policy_file = os.path.join(os.path.dirname(__file__), "iam_policy.json")
        if not os.path.exists(policy_file):
            raise RuntimeError("Please download AWS Load Balancer Controller policy JSON into iam_policy.json.")

        with open(policy_file, "r") as f:
            policy_doc = json.load(f)

        cluster.aws_auth.add_user_mapping(
            user=iam.User.from_user_arn(self, "Me", "arn:aws:iam::424851482325:user/alfonso.brown"),
            groups=["system:masters"]
        )

        # 4) Create Kubernetes service account for the Load Balancer Controller (IRSA)
        sa = cluster.add_service_account(
            "aws-load-balancer-controller-sa",
            name="aws-load-balancer-controller",
            namespace="kube-system"
        )

        # Attach inline policy to the service account role
        sa_role = iam.Role.from_role_arn(self, "sa-role", sa.role.role_arn)  # reference to created role
        # Create a managed policy from the policy JSON and attach it to the role
        lb_policy = iam.Policy(self, "alb-policy",
            document=iam.PolicyDocument.from_json(policy_doc)
        )
        lb_policy.attach_to_role(sa.role)

        # 5) Install AWS Load Balancer Controller helm chart via eks.HelmChart
        # values per AWS docs: clusterName, region, vpcId; and tell chart to use our existing serviceAccount
        alb_chart = eks.HelmChart(self, "AWSLoadBalancerControllerChart",
            cluster=cluster,
            chart="aws-load-balancer-controller",
            repository="https://aws.github.io/eks-charts",
            release="aws-load-balancer-controller",
            namespace="kube-system",
            values={
                "clusterName": cluster.cluster_name,
                "region": self.region,
                "vpcId": vpc.vpc_id,
                # IMPORTANT: set serviceAccount.create=false and serviceAccount.name to the service account we created
                "serviceAccount": {
                    "create": False,
                    "name": "aws-load-balancer-controller"
                }
            }
        )

        # 6) Deploy your application Helm chart
        app_chart = eks.HelmChart(self, "MyAppChartFromRepo",
            cluster=cluster,
            chart="recruitair",             # chart name in repository
            repository="https://recruitair-helm-charts.s3.amazonaws.com/charts/",# replace with your repo
            release="recruitair",
            namespace="default",
            values={
                "ingress": {
                    "className": "alb"
                },
                "postgres": {
                    "persistence": {
                        "storageClass": "gp2"
                    }
                }
            },
        )

        # Add outputs for the cluster name so you can fetch kubeconfig if needed
        from aws_cdk import CfnOutput
        CfnOutput(self, "ClusterName", value=cluster.cluster_name)
        CfnOutput(self, "KubeconfigCommand", value=f"aws eks update-kubeconfig --name {cluster.cluster_name} --region {self.region}")
