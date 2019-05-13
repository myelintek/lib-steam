import os
import re
import click
from subprocess import check_output, STDOUT
from api import MyelindlApi, MyelindlApiError


## Buckets ##
@click.command(name="mb")
@click.argument('name', required=True)
def mk_bk(name):
    """make a bucket"""
    try:
        bk_name = None
        if name.startswith('bk/'):
            check_output("mc mb {}".format(name), shell=True, stderr=STDOUT)
            bk_name = name[3:]
        else:
            check_output("mc mb bk/{}".format(name), shell=True, stderr=STDOUT)
            bk_name = name
        # register to server
        api = MyelindlApi()
        api.bucket_add(bk_name)
    except Exception as e:
        click.echo(click.style("Bucket created failed. Bucket name contains invalid characters", fg='red'))
        return
    click.echo(click.style("Bucket `{}` created successfully.".format(name), fg='green'))


@click.command(name="rb")
@click.option('--force', is_flag=True, help="allow a recursive remove operation")
@click.argument('name', required=True)
def rm_bk(force, name):
    """remove a bucket"""
    try:
        bk_name = name
        if name.startswith('bk/'):
            bk_name = name[3:]
        api = MyelindlApi()
        api.bucket_del(bk_name)
    except Exception as e:
        pass
    try:
        if force:
            check_output("mc rb --force bk/{}".format(bk_name), shell=True, stderr=STDOUT)
        else:
            check_output("mc rb bk/{}".format(bk_name), shell=True, stderr=STDOUT)
    except Exception as e:
        click.echo("Bucket deleted failed. {}".format(e))
        return
    click.echo(click.style("Bucket `{}` deleted successfully.".format(name), fg='green'))
 

## Objects ##
@click.command()
@click.argument('target', required=False, nargs=-1)
def ls(target):
    """list buckets and objects"""
    try:
        if target:
            args = ["{}".format(a) for a in target]
            objs = " ".join(args)
            out = check_output("mc ls {}".format(objs), shell=True)
            for line in out.splitlines():
                if 'run-' not in line:
                    match = re.search('(\[.*\])\s+([^\s]+B) (.*)', line)
                    if match:
                        click.echo(click.style(match.group(1), fg='green')+'\t'+
                                   click.style(match.group(2), fg='yellow')+' '+
                                   click.style(match.group(3), fg='bright_cyan'))
        else:
            click.echo(click.style("Are you want to list bucket? try `steam data ls bk/`", fg='green'))
    except Exception as e:
        click.echo(click.style("ls failed. {}".format(e), fg='red'))


@click.command()
@click.argument('source', required=True, nargs=-1)
def cat(source):
    """display object contents"""
    try:
        args = [a for a in source]
        objs = " ".join(args)
        os.system("mc cat {}".format(objs))
    except Exception as e:
        click.echo(click.style("cat object failed. {}".format(e), fg='red'))


@click.command()
@click.option('-n', '--lines', default=10, help="print the first 'n' lines (default: 10)")
@click.argument('source', required=True, nargs=-1)
def head(lines, source):
    """display first 'n' lines of an object"""
    try:
        args = [a for a in source]
        objs = " ".join(args)
        os.system("mc head -n {} {}".format(lines, objs))
    except Exception as e:
        click.echo(click.style("cat object failed. {}".format(e), fg='red'))


@click.command()
@click.option('-r', '--recursive', is_flag=True, help="copy recursively")
@click.argument('source', required=True, nargs=-1)
@click.argument('target', required=True)
def cp(recursive, source, target):
    """copy objects"""
    try:
        out = None
        args = [a for a in source]
        objs = " ".join(args)
        if recursive:
            os.system("mc cp --recursive {} {}".format(objs, target))
        else:
            os.system("mc cp {} {}".format(objs, target))
    except Exception as e:
        click.echo(click.style("copy failed. {}".format(e), fg='red'))


@click.command()
@click.option('-r', '--recursive', is_flag=True, help="remove recursively")
@click.argument('target', required=True, nargs=-1)
def rm(recursive, target):
    """remove objects"""
    try:
        args = [a for a in target]
        objs = " ".join(args)
        if recursive:
            os.system("mc rm --recursive --force {} ".format(objs))
        else:
            os.system("mc rm {}".format(objs))
    except Exception as e:
        click.echo(click.style("remove failed. {}".format(e), fg='red'))


@click.command()
@click.option('--overwrite', is_flag=True, help="overwrite object(s) on target")
@click.option('--remove', is_flag=True, help="remove extraneous object(s) on target")
@click.argument('source', required=True)
@click.argument('target', required=True)
def mirror(overwrite, remove, source, target):
    """synchronize object(s) to a remote site"""
    try:
        cmd = "mc mirror "
        if overwrite:
            cmd += "--overwrite "
        if remove:
            cmd += "--remove "
        cmd += "{} {}".format(source, target)
        os.system(cmd)
    except Exception as e:
        click.echo(click.style("mirror failed. {}".format(e), fg='red'))


@click.group(help='Groups of commands to manage datasets')
def data():
    pass

data.add_command(mk_bk)
data.add_command(rm_bk)
data.add_command(ls)
data.add_command(cat)
data.add_command(head)
data.add_command(cp)
data.add_command(rm)
data.add_command(mirror)
