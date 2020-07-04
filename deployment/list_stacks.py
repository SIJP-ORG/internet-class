import boto3
import argparse

def parse_argument():
    '''
    Argument definition and help message.
    '''
    parser = argparse.ArgumentParser(description='List up all stacks.')
    parser.add_argument('-p', '--python-ip-list', dest='python_ip_list', action='store_true')
    parser.add_argument('-i', '--ip-only', dest='ip_only', action='store_true')
    return parser.parse_args()

def main():
    args = parse_argument()

    cfr = boto3.resource('cloudformation')
    
    if not args.ip_only and not args.python_ip_list:
        print('Name, Status, IP')
        
    for stack in cfr.stacks.all():
        if stack.name.startswith('msg-'):
            public_ip = find_public_ip(stack.outputs)
            if args.python_ip_list:
                print('    \'{0}\','.format(public_ip))
            elif args.ip_only:
                print(format(public_ip))
            else:
                print('{0}, {1}, {2}'.format(stack.name, stack.stack_status, public_ip))

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