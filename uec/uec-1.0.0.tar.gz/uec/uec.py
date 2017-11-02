import click
import sys
import getpass
from .user import User


@click.group()
def main():
    pass


@click.command()
@click.option('-o', 'info', type=(int, int), default=(-1, -1), help='Show the gpa list, input the [year] you want to show firstly,'
                                                                    'and input [1] for the first, [2] for the second term.')
def gpa(info):
    """Show gpa list."""
    user = get_user_info()

    if info[0] == -1 and info[1] == -1:
        user.get.gpa()
    else:
        user.get.gpa_by(info[0], info[1])


@click.command()
def lecture():
    """Show lecture list."""
    user = get_user_info()
    user.get.lecture()


@click.command()
@click.option('-o', 'flag', type=int, default=0, help='Show the canceled lecture list, '
                                                      '[0] for the graduate, '
                                                      '[1] for the undergraduate student.')
def canceled(flag):
    """Show canceled lecture list."""
    User.get_canceled_lecture_list(flag)


# add command to group
main.add_command(gpa)
main.add_command(lecture)
main.add_command(canceled)


def get_user_info():
    # get user info
    if sys.stdin.isatty():
        print('Enter your uec username and password to login...')
        username = input('Username: ')
        password = getpass.getpass('Password: ')
    else:
        print('Username: ')
        username = sys.stdin.readline().rstrip()
        print('Password: ')
        password = sys.stdin.readline().rstrip()

    # return user
    user = User(username, password)
    return user

if __name__ == "__main__":
    main()
