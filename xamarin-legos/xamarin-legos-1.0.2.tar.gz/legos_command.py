import click
import arrow
import os
from tabulate import tabulate
import csv

from nuget import PackageManager
from nuget import Package
from tempfile import gettempdir
from github import Github

try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse

@click.group()
@click.pass_context
def cli(ctx):
    '''This is a command line tool to list the github issues'''
    #TODO: add code to fetch issue details
    ctx.obj = Github()
   
    if ctx.invoked_subcommand is None:
        click.echo("Hello there!")

@cli.command(name='issues')
@click.pass_context
@click.option('--status', default='open', metavar='<text>', help='Indicates the state of the issues to return. Can be either open, closed, or all. Default: open')
@click.option('--repo', metavar='<github_repo>', help='lists the issues for the repo')
def list_issues(ctx, repo, status):
    ''' lists open issues for the repo by default'''
    
    if repo:
        repo_list = [repo]
    else:
        repo_list = get_tracked_repos()

    if repo_list.count == 0:
        click.echo("No tracked repo. Use `legos track --repo <repo_name>`")
    
    gh = ctx.obj

    issues_list = []

    for item in repo_list:
        click.echo(status + " issues from " + item)
        issues = gh.get_repo(item).get_issues(state=status)
        
        for issue in issues:
            localtiem = arrow.get(issue.created_at).to('local').humanize()
            issues_list.append([issue.number, issue.title, localtiem])
    
    print(tabulate(issues_list,tablefmt="plain"))

@cli.command(name='stats')
@click.option('--repo', metavar='<github_repo>', help='get stats for the repo')
@click.pass_context
def project_stats(ctx, repo):
    '''shows the basic project stats like stars, issues, watch and PRs for tracked/single repo'''
    print ("\nProject stats")

    gh = ctx.obj

    if repo is not None:
        print_stats(repo, gh)
        return
    
    repo_list = get_tracked_repos()
    for project in repo_list:
        print_stats(project, gh)

@cli.command(name='labels')
@click.option('--repo', metavar='<github_repo>', help='get labels stats for the repo')
@click.pass_context
def label_stats(ctx, repo):
    '''shows the label stats for the repo'''
    gh = ctx.obj
    
    label_list = ['bug', 'feature', 'need-more-info']

    if repo is not None:
        mylabels = get_labels(gh.get_repo(repo), label_list)
        print_label_stats(repo, gh, mylabels)
        return
    
    repo_list = get_tracked_repos()
    
    for project in repo_list:
        mylabels = get_labels(gh.get_repo(project), label_list)
        print_label_stats(project, gh, mylabels)

def label_count(repo, mylabels):
    myissues = {}
    for label in mylabels:
        issues = repo.get_issues(state='open', labels = [label])
        myissues[label.name] = total_count(issues)
    return myissues

def print_label_stats(repo, git, mylabels):
    project = git.get_repo(repo)
    click.secho(project.name, bold=True)
    click.echo(project.description)

    myissues = label_count(project, mylabels)

    message = "bugs: {0}\tfeature: {1}\tneed-more-info: {2}\t PRs:{3}\n".format(myissues['bug'], myissues['feature'], myissues['need-more-info'], get_pr_count(project))
    print (message)

@cli.command(name='track')
@click.option('--repo', metavar='<github_repo>', help='add the repo to the trac list')
@click.option('--list', is_flag=True, help='Lists all tracked repos')
@click.pass_context
def add_repo(ctx, repo, list):
    '''adds the repo to the tracking list'''
    
    file_name = os.path.join(gettempdir(), 'repos.txt')
    if not os.path.exists(file_name):
        file = open(file_name, 'w')
        if repo:
            file.write(repo + '\n')
        file.close

    repo_list = get_tracked_repos()

    if list or repo is None:
        for item in repo_list:
            print (item)
        return

    file = open(file_name,'a')
    if repo not in repo_list:
        file.write (repo+'\n')
        file.close()
    click.echo(repo+ ' is added to the list')

@cli.command(name='packages')
@click.option("--output", metavar='<file_path>', help="supply file path to export data in csv format")
@click.option("--owner", default='PluginsForXamarin', metavar='<nuget_owner>', help="takes nuget owner name, default is PluginsForXamarin")
@click.pass_context
def packages(ctx, output, owner):
    '''Prints the nuget package stats. WARNING - do not use with user owning large number of packages'''
    nuget = PackageManager()
    packages = nuget.get_packages(owner)

    gh = ctx.obj
    label_list = ['bug', 'feature', 'need-more-info']

    rows = []
    packages_count = len(packages)
    with click.progressbar(packages, label='Fetching numbers, it will take quite long:', length=packages_count) as bar:
        for package in bar:
            if package.project_url is None:
                continue
            result = urlparse(package.project_url)
            repo = gh.get_repo(result.path.strip('/'))
            labels = get_labels(repo, label_list)
            issues = label_count(repo, labels)
            pr_count = get_pr_count(repo)

            try:
                rows.append([package.id, package.version, package.total_downloads, pr_count, issues['bug'], issues['feature'], issues['need-more-info']]) 
            except:
                rows.append([package.id, package.version, package.total_downloads, pr_count, '-1', '-1', '-1']) 

    header = ['package', 'version', 'downloads', 'PRs', 'bugs', 'feature', 'need-more-info']

    if output is not None:
        with open(output, 'w') as csvfile:
            writer = csv.writer(csvfile, dialect='excel')
            writer.writerow(header)
            for row in rows:
                writer.writerow(row)

    print (tabulate(rows, headers=header))


def get_tracked_repos():
    file_name = os.path.join(gettempdir(), 'repos.txt')
    file = open(file_name,'r')
    list_repo = map(lambda p: p.rstrip(), file.readlines())
    file.close()
    return list_repo

def print_stats(project, git):
    repo = git.get_repo(project)
    click.secho(repo.name, bold=True)
    click.echo(repo.description)
    pr_count = get_pr_count(repo)

    stats_text = "stars: {0}\tissues: {1}\twatch: {2}\tPRs: {3}\n".format(repo.stargazers_count, repo.open_issues_count, repo.watchers_count, pr_count)
    click.echo(stats_text)

def get_labels(repo, names):
    labels = []
    for name in names:
        try:
            labels.append(repo.get_label(name))
        except:
            continue
    return labels

def get_pr_count(repo):
    return total_count(repo.get_pulls(state='open'))

def total_count(paginated_list):
    pl_count = 0
    for _ in paginated_list:
        pl_count = pl_count + 1
    return pl_count

if  __name__ == '__main__':
    cli(obj)