import boto3
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
            stack.delete()

if __name__ == '__main__':
    main()