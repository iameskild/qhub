import json
import subprocess
import functools
import boto3


@functools.lru_cache()
def regions():
    output = subprocess.check_output(["aws", "ec2", "describe-regions"])
    data = json.loads(output.decode("utf-8"))
    return {_["RegionName"]: _["RegionName"] for _ in data["Regions"]}


@functools.lru_cache()
def zones(region):
    output = subprocess.check_output(
        ["aws", "ec2", "describe-availability-zones", "--region", region]
    )
    data = json.loads(output.decode("utf-8"))
    return {_["ZoneName"]: _["ZoneName"] for _ in data["AvailabilityZones"]}


@functools.lru_cache()
def kubernetes_versions(grab_latest_version=True):
    # AWS SDK (boto3) currently doesn't offer an intuitive way to list available kubernetes version. This implementation grabs kubernetes versions for specific EKS addons. It will therefore always be (at the very least) a subset of all kubernetes versions still supported by AWS.
    client = boto3.client("eks")
    supported_kubernetes_versions = list()
    available_addons = client.describe_addon_versions()
    for addon in available_addons.get("addons", None):
        for eksbuild in addon.get("addonVersions", None):
            for k8sversion in eksbuild.get("compatibilities", None):
                supported_kubernetes_versions.append(
                    k8sversion.get("clusterVersion", None)
                )

    # remove duplicate values
    # then sort from oldest to newest available versions
    supported_kubernetes_versions = sorted(list(set(supported_kubernetes_versions)))

    if grab_latest_version:
        return supported_kubernetes_versions[-1]

    return supported_kubernetes_versions


@functools.lru_cache()
def instances(region):
    output = subprocess.check_output(
        ["aws", "ec2", "describe-instance-types", "--region", region]
    )
    data = json.loads(output.decode("utf-8"))
    return {_["InstanceType"]: _["InstanceType"] for _ in data["InstanceTypes"]}
