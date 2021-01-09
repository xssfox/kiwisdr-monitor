import urllib.request
from urllib.parse import urlparse
import boto3
import os

cw = boto3.client('cloudwatch')

def get_status(url):
    status = urllib.request.urlopen(url, timeout=3).read()
    status = status.decode('utf-8').split("\n")
    data = {}
    for line in status:
        try:
            (key, value) = line.split("=",1)
            data[key] = value
        except ValueError:
            pass
    return data
def post_cw_data(host,value, metric="Users", unit="Count"):
    try:
        response = cw.put_metric_data(
            Namespace='kiwisdr',
            MetricData=[
                {
                    'MetricName': metric,
                    'Dimensions': [
                        {
                            'Name': 'host',
                            'Value': host
                        },
                    ],
                    'Value': value,
                    'Unit': unit
                },
            ]
        )
    except:
        pass
def handler(event, context):
    hosts = os.environ.get('HOSTS').split(",")
    for host in hosts:
        try:
            status = get_status(host)
            dem = urlparse(host).netloc
            post_cw_data(dem, float(status['users']))
            post_cw_data(dem, float(status['gps_good']),'GPS-Sats')
            post_cw_data(dem, float(status['uptime']),'Uptime', 'Seconds')
            post_cw_data(dem, 1 if status['status'] == "active" else 0 ,'Active', 'None')
            post_cw_data(dem, 0 if status['offline'] == "no" else 1,'Offline', 'None')
        except:
            pass

if __name__ == "__main__":
    handler({},{})