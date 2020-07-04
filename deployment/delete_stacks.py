import boto3
import botocore
import argparse

def parse_argument():
    '''
    Argument definition and help message.
    '''
    parser = argparse.ArgumentParser(description='Delete all stacks.')
    return parser.parse_args()

def main():
    args = parse_argument()

    cfr = boto3.resource('cloudformation')

    for stack in cfr.stacks.all():
        if (stack.name.startswith('msg-')):
            print('Deleting stack {0}'.format(stack.name))
            try:
                stack.delete()
            except botocore.exceptions.ClientError as e:
                print('Failed: {0}'.format(e))

if __name__ == '__main__':
    main()