import boto3
import argparse

def parse_argument():
    '''
    Argument definition and help message.
    '''
    parser = argparse.ArgumentParser(description='List up all stacks.')
    return parser.parse_args()

def main():
    args = parse_argument()

    cfr = boto3.resource('cloudformation')

    print('Name, Status, IP')
    for stack in cfr.stacks.all():
        if (stack.name.startswith('msg-')):
            print('{0}, {1}, {2}'.format(stack.name, stack.stack_status, find_public_ip(stack.outputs)))

def find_public_ip(outputs):
    public_ip = 'unknown'

    if outputs:
        for output in outputs:
            if output['OutputKey'] == 'PublicIp':
                public_ip = output['OutputValue']
                break

    return public_ip

if __name__ == '__main__':
    main()