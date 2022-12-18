import atexit

try:

    print('Doing something...')

    print('\nGoing to trigger an exception, be ready: ')
    raise Exception('Testing exception', 'woo, that was unexpected!')

except Exception as ex:

    # the exception instance
    print('Exception type: ', type(ex))
    # arguments stored in .args
    print('Exception args: ', ex.args)
    # __str__ allows args to be printed directly,
    print('Exception ex obj: ', ex)

    # but may be overridden in exception subclasses

    # unpack args
    x, y = ex.args
    print('Exception x arg =', x)
    print('Exception y arg =', y)
    print('')


def exit_handler():
    print('My application is exiting!\n')
    # w+: Create the file if it does not exist and then open it in write mode.
    file = open('test_on_exit_file', 'w+')
    file.write('Exited :)!')


atexit.register(exit_handler)
