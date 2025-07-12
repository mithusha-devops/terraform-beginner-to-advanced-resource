import requests
import jmespath
import xlsxwriter

 
def get_cluster_ent_id(cluster_name):

    cluster_ent_id = []
    
    url = f"{DYNATRACE_ENV_URL}/api/v2/entities"

    headers = {
        "Authorization": f"Api-Token {API_TOKEN}"
    }
    params = {
        "entitySelector": f"type(KUBERNETES_CLUSTER),entityName.equals({cluster_name})",
        "pageSize": 50
    }
    response = requests.get(url, headers=headers, params=params)
    response_json = response.json()
    cluster_id = jmespath.search("entities[0].entityId", response_json)
    cluster_ent_id.append(cluster_id)
    return cluster_ent_id
    


def get_ns_ids(url, cluster_ent_id):
     
     ns_list = []
     
     headers = {
    "Authorization": f"Api-Token {API_TOKEN}"
}
     params = {    
     "from": "-30d",
     "to": "now",
     "resolution": "Inf"
     }
     url = f'{url}/{cluster_ent_id[0]}'
     response = requests.get(url, headers=headers, params=params)
     if response.status_code == 200:
        ns_list.append(jmespath.search("fromRelationships.isClusterOfNamespace[].id", response.json()))
        return ns_list

def get_names_of_ns(url, ns_id):
   
        url = f'{url}/{ns_id}'
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            ns_name = jmespath.search("displayName", response.json())
            return ns_name
ns_names = []

def get_list_of_app_id(url, namespace):
    url = f'{url}/{namespace[0]}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Getting List of Cloud Application Entity Id's", flush=True)
        app_list = jmespath.search("fromRelationships.isNamespaceOfCa[].id", response.json())
        return app_list
 
def get_names_of_app(url, app_id):
    url = f'{url}/{app_id}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:

        app_name = jmespath.search("displayName", response.json())
        return app_name
   

def get_max_value(type, cloud_application_id, metric):
    url = "https://vdg36483.live.dynatrace.com/api/v2/metrics/query"
    token = "dt0c01.5PTB5L4SPU2CDWUCS7H4YZAA.JQRSAPZZNDBLHFGGVK5TCL2IZ7PJ4KVCYQY34WDHKAR76APS2PD633FDS3IX7XR3"
    headers = {
        'Authorization': f'Api-Token {token}',
        'Accept': 'application/json'
    }
    
    params = {
        "metricSelector": f"(builtin:containers.{type}.usagePercent:filter(in(\"dt.entity.container_group_instance\",entitySelector(\"type(CONTAINER_GROUP_INSTANCE),fromRelationships.IS_CGI_OF_CA(type(CLOUD_APPLICATION),type(CLOUD_APPLICATION),entityId({cloud_application_id}))\"))):parents:parents:splitBy(\"dt.entity.cloud_application\"):{metric})",
        "from": "-30d",
        "to": "now",
        "resolution": "Inf"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    metric_value = None
    if 'result' in data and len(data['result']) > 0:
        for result in data['result']:
            if 'data' in result and len(result['data']) > 0:
                for point in result['data']:
                    if 'values' in point and point['values']:
                        values = [v for v in point['values'] if v is not None]
                        if values:
                            current_max = max(values)
                            if metric_value is None or current_max > metric_value:
                                metric_value = current_max
    if metric_value is not None:
        metric_value = round(metric_value, 3)
    return metric_value

def create_excel_report(cloud_app_ids, app_names, namespace, clustername, workbook):

    worksheet = workbook.add_worksheet(f'{clustername}_{namespace}')
    for col_id, app_id in enumerate(cloud_app_ids):


        worksheet.write('A1', 'MICROSERVICE NAME')

        worksheet.write('B1', 'Max CPU (%)')
        worksheet.write('C1', 'Avg CPU (%)')
        worksheet.write('D1', 'Max Memory (%)')
        worksheet.write('E1', 'Avg Memory (%)')
        
        max_cpu = get_max_value("cpu", app_id, "max") or "None"
        avg_cpu = get_max_value("cpu", app_id, "avg") or "None"
        max_memory = get_max_value("memory", app_id, "max") or "None"
        avg_memory = get_max_value("memory", app_id, "avg") or "None"
        worksheet.write(f'A{col_id+2}', app_names[col_id])
        
        if max_cpu == "None" or avg_cpu == "None" or max_memory == "None" or avg_memory == "None":
            worksheet.write(f'B{col_id+2}', max_cpu)
            worksheet.write(f'C{col_id+2}', avg_cpu)
            worksheet.write(f'D{col_id+2}', max_memory)
            worksheet.write(f'E{col_id+2}', avg_memory)
        else:
            worksheet.write(f'B{col_id+2}', max_cpu)
            worksheet.write(f'C{col_id+2}', avg_cpu)
            worksheet.write(f'D{col_id+2}', max_memory)
            worksheet.write(f'E{col_id+2}', avg_memory)
    
    print("Excel file 'utilization.xlsx' created successfully.")



if __name__ == "__main__":
  
  DYNATRACE_ENV_URL = "https://vdg36483.live.dynatrace.com"
  API_TOKEN = "dt0c01.5PTB5L4SPU2CDWUCS7H4YZAA.JQRSAPZZNDBLHFGGVK5TCL2IZ7PJ4KVCYQY34WDHKAR76APS2PD633FDS3IX7XR3"
  input_details = {"ekscluster-dev": "prod-a", "ekscluster-test": "prod-a"}
  metrics_host = f"{DYNATRACE_ENV_URL}/api/v2/metrics/query"
  url = f"{DYNATRACE_ENV_URL}/api/v2/entities"
  headers = {
        "Authorization": f"Api-Token {API_TOKEN}"
    }

  workbook = xlsxwriter.Workbook('utilization.xlsx')
  for clustername, namespace in input_details.items():
    ns_ids_matched = []
    app_names = []
    cluster_name = clustername
    namespace = namespace
    cluster_entity_ids = get_cluster_ent_id(cluster_name)
    namspace_ids_list = get_ns_ids(url, cluster_entity_ids)
    for ns_id in namspace_ids_list[0]:
        ns_name = get_names_of_ns(url, ns_id)
        if ns_name == namespace:
            ns_ids_matched.append(ns_id)
        else:
            continue
    app_ids = get_list_of_app_id(url,  ns_ids_matched)
    for app_id in app_ids:
        app_names.append(get_names_of_app(url, app_id))
    create_excel_report(app_ids, app_names, namespace, clustername, workbook)
  workbook.close()
