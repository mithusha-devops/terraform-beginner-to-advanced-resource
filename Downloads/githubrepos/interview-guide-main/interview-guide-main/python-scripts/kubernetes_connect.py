from kubernetes import *
import base64
import json
import csv

def kube_connection():

    cluster_endpoint = ""
    cluster_ca_cert = r"ca.crt"
    token = ""
    configuration = client.Configuration()

    configuration.host = cluster_endpoint

    configuration.api_key = {"authorization": f"Bearer {token}"}
    configuration.ssl_ca_cert = cluster_ca_cert
    configuration.verify_ssl = True

    api_client = client.ApiClient(configuration)
  
    return client, api_client

    # v1 = client.CoreV1Api(api_client)
    
 

def fetch_hpa_details(client, api_client):
    print("\nFetching HPA min/max pod settings...")
    rows = []
    try:
        autoscaling_v1 = client.AutoscalingV2Api(api_client)
        hpas = autoscaling_v1.list_horizontal_pod_autoscaler_for_all_namespaces()
        for hpa in hpas.items:
            rows.append([hpa.metadata.namespace, hpa.metadata.name, hpa.spec.min_replicas, hpa.spec.max_replicas])
        return rows
            
    except Exception as e:
          print(f"Error fetching HPAs: {e}")



def fetch_deployment_resources(client, api_client):
    print("\nFetching CPU/Memory requests and limits from deployments...")
    rows = []
    try:
        apps_v1 = client.AppsV1Api(api_client)
        deployments = apps_v1.list_deployment_for_all_namespaces()
        for deploy in deployments.items:
            if "php-apache" in deploy.metadata.name:  # Filter deployments with name containing "buyflow"
                ns = deploy.metadata.namespace
                deploy_name = deploy.metadata.name
                containers = deploy.spec.template.spec.containers
                for c in containers:
                            cname = c.name
                            resources = c.resources
                            reqs = resources.requests or {}
                            lims = resources.limits or {}
                            cpu_req = reqs.get("cpu", "none")
                            mem_req = reqs.get("memory", "none")
                            cpu_lim = lims.get("cpu", "none")
                            mem_lim = lims.get("memory", "none")
                            rows.append([ns, deploy_name, cname, cpu_req, mem_req, cpu_lim, mem_lim])
        
        hpa_values = fetch_hpa_details(client, api_client)
        deployement_hpa_list = rows[0] + hpa_values[0]
        # Write the results to CSV
        with open("deployment_resources.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Namespace", "Deployment", "Container", "CPU Request", "Memory Request", "CPU Limit", "Memory Limit","Namespace", "HPA Name", "Min Pods", "Max Pods"])
            writer.writerows([deployement_hpa_list])
       
        print(f"Deployment resources have been written to 'deployment_resources.csv'.")
    except Exception as e:
        print(f"Error fetching HPAs: {e}")


if __name__ == "__main__":     
     client, api_client = kube_connection()
     fetch_hpa_details(client, api_client)
     fetch_deployment_resources(client, api_client)
