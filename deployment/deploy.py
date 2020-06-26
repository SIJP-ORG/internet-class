import boto3
import datetime

now = datetime.datetime.now()
name = now.strftime("msg-%m%d-%H%M%S-%f")

client = boto3.client('cloudformation')

with open('messenger-template.yml', 'r') as f:
    template = f.read()

response = client.create_stack(
    StackName = name,
    TemplateBody = template,
    Parameters = [
        {'ParameterKey': 'MachineName', 'ParameterValue': name},
        {'ParameterKey': 'ImageId', 'ParameterValue': 'ami-026965ecffcdf55c0'},
    ],
    OnFailure = 'DELETE',
    EnableTerminationProtection = False
)

print('StackId: {0}'.format(response['StackId']))

