#coding:utf8
import os, sys
import urllib.request
import json
import getopt
import re

dir = os.path.split(os.path.realpath(__file__))[0]
url_prefix = (sys.argv[1] if len(sys.argv) > 1 else '').strip('/')
if url_prefix != '':
    url_prefix = '/' + url_prefix
root_dir = os.getcwd()

def listdir(path):
    files = os.listdir(path)
    files.sort(key=lambda a: f"1_{a}" if os.path.isfile(os.path.join(path, a)) else f"0_{a}")
    return files

def index_file_path(path = ''):
    index_dir = os.path.join(root_dir, path)
    if not os.path.isdir(index_dir):
        os.makedirs(index_dir)

    index_file = os.path.join(path, 'README.md')
    if not os.path.isfile(index_file):
        with open(index_file, 'w') as f:
            pass

    return index_file, url_prefix + '/' + (urllib.request.pathname2url(path) + '/' if path != '' else '')

def create_index_file(path = ''):
    index_file, index_url = index_file_path(path)
    with open(os.path.join(root_dir, index_file), 'r+', encoding='utf8') as f:
        lines = []

        for file in listdir(os.path.join(root_dir, path)):
            fullpath = os.path.join(path, file)

            if fullpath in ['_navbar.md', '_sidebar.md', 'index.html']:
                continue

            if file in ['README.md', '.gitignore']:
                continue

            if os.path.isdir(fullpath):
                # 目录
                lines.append('- [<span class="fa fa-folder-o">&nbsp;%s</span>](%s)' % (file, index_file_path(fullpath)[1]))
            elif file[-3:] == '.md':
                # 内部文档
                lines.append('- [<span class="fa fa-file-o">&nbsp;%s</span>](%s)' % (file, url_prefix + '/' + urllib.request.pathname2url(fullpath)))
            else:
                # 外部链接
                lines.append('- [<span class="fa fa-file-o">&nbsp;%s</span>](/%s \':ignore\')' % (file, urllib.request.pathname2url(fullpath)))

        custom = False
        lineno = 0
        for line in f.readlines():
            lineno += 1

            if line.strip() == '----':
                custom = True

            if custom:
                lines.append(line.rstrip('\r\n'))

        f.seek(0)
        f.truncate()
        f.write('\n'.join(lines))

    return index_file, index_url


def build_dir(sidebar, path='', segment=[], depth=0):
    global md_files

    children = []

    for file in listdir(os.path.join(root_dir, path)):
        fullpath = os.path.join(path, file)

        if fullpath in ['_navbar.md', '_sidebar.md', 'index.html']:
            continue

        if file in ['README.md', '.gitignore']:
            continue

        child = {'is_file': True}
        children.append(child)

        if os.path.isdir(fullpath):
            _, url = create_index_file(fullpath)

            sidebar.write('%s- [%s](%s)\n' % ('\t' * depth, file, url))

            child['is_file'] = False
            child['title'] = file
            child['url'] = url
            child['children'] = build_dir(sidebar, path=fullpath, depth=depth+1)

            continue

        if file[-3:] != '.md':
            continue

        url = url_prefix + '/' + urllib.request.pathname2url(fullpath)
        sidebar.write('%s- [%s](%s)\n' % ('\t' * depth, file, url))

        child['title'] = file[:-3]
        child['url'] = url

    return children

with open(os.path.join(root_dir, '_sidebar.md'), 'w') as sidebar:
    index_file, index_url = create_index_file()
    tree = build_dir(sidebar)

with open(os.path.join(root_dir, '_navbar.md'), 'w') as navbar:
    navbar.write(f'- [首页](/)\n')
    for child in tree:
        if child['is_file']:
            continue

        navbar.write('- [%s](%s)\n' % (child['title'], child['url']))

        for _child in child['children']:
            if _child['is_file']:
                continue

            navbar.write('\t- [%s](%s)\n' % (_child['title'], _child['url']))

with open(os.path.join(dir, 'index.html'), 'r', encoding='utf8') as tpl:
    with open(os.path.join(root_dir, 'index.html'), 'w') as html:
        content = tpl.read()
        content = re.sub('{{url_prefix}}', url_prefix, content)
        html.write(content)
