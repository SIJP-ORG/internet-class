import boto3
import argparse
import textwrap
import datetime

def parse_argument():
    '''
    Argument definition and help message.
    '''
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Create speicified number of CloudFormation stacks.
            Please specify the following three environment variables.
             a) AWS_DEFAULT_REGION=us-west-2
             b) AWS_ACCESS_KEY_ID
             c) AWS_SECRET_ACCESS_KEY
            '''))
    parser.add_argument('-n', '--number-of-instances', dest='number_of_instances', type=int, default=1)
    parser.add_argument('-a', '--ami-id', dest='ami_id', default='ami-09cfab33a38e0f0e8')
    return parser.parse_args()

def main():
    args = parse_argument()
    for index in range (0, args.number_of_instances):
        launch(index, args.ami_id)
        

def launch(index, ami_id):
    now = datetime.datetime.now()
    name = now.strftime("msg-%m%d-%H%M%S-%f")
    print('Launch #{0} from {1} as {2}'.format(index, ami_id, name))

    client = boto3.client('cloudformation')

    with open('messenger-template.yml', 'r') as f:
        template = f.read()

    response = client.create_stack(
        StackName = name,
        TemplateBody = template,
        Parameters = [
            {'ParameterKey': 'MachineName', 'ParameterValue': name},
            {'ParameterKey': 'ImageId', 'ParameterValue': ami_id},
        ],
        OnFailure = 'DO_NOTHING',
        EnableTerminationProtection = False
    )

    if response.get('StackId'):
        print('  Successfully launched.')
    else:
        print('  Error: ' + str(response))

if __name__ == '__main__':
    main()