import os
import re

import bs4
import requests
from bs4 import BeautifulSoup


def coll_container(soup, title, childs):
    new_tag = soup.new_tag("div")
    new_tag.attrs['class'] = 'padded'
    button = soup.new_tag('button', type="button")
    button.attrs['class'] = "collapsible"
    button.string = title

    cont_tag = soup.new_tag('div', )
    cont_tag.attrs['class'] = "content"

    for child in childs:
        cont_tag.append(child)

    new_tag.append(button)
    new_tag.append(cont_tag)

    return new_tag

def line_container(soup, childs):
    new_tag = soup.new_tag("div")
    for child in childs:
        new_tag.append(child)

    return new_tag

def focus_container(soup, childs):
    new_tag = soup.new_tag("div")
    for child in childs:
        new_tag.append(child)

    return new_tag

change_emptyspace = lambda x: x.replace('-', ' ').replace('_', ' ')


def parse_higlighted_doc(link, content_save, service, topic):

    local_head = link[link.rindex('#')+1:]
    local_parsed_head = change_emptyspace(local_head)
    global_id = change_emptyspace(link[link.rindex('/')+1:link.rindex('#')])

    glocal_id = local_parsed_head +" -- "+ global_id
    file_name_cache = f'data/aws/links/{glocal_id}.txt'

    if not os.path.exists(file_name_cache):
        text = requests.get(link).text
        with open(file_name_cache, 'w') as f:
            f.write(text)
    else:
        with open(file_name_cache, 'r') as f:
            text = f.read()

    text = re.sub('href="./', f'href="{link[:link.rindex("/")+1]}', text)
    text = re.sub('src="((?!http)\w+)/', fr'src="{link[:link.rindex("/")+1]}\1/', text)

    soup = BeautifulSoup(text, 'html.parser')

    content = soup.find(id='main-col-body')

    starters, focused, enders = [], [], []
    mode = 0
    for child in content.children:
        child_str = str(child)
        if isinstance(child, bs4.Tag) and 'id' in child.attrs  \
                and child.attrs['id'] == local_head:
            mode += 1
        elif mode ==1 and child.name == 'h1':
            mode += 1


        if mode == 0:
            starters.append(child)
        elif mode == 1:
            focused.append(child)
        else:
            enders.append(child)

    main_body = content_save.find(id='main-col-body')
    starters_strs = ' '.join([(str(list(ss.strings)) if list(ss.strings) else '')  for ss in starters])


    if starters_strs.strip():
        main_body.append(coll_container(content_save, f"Prefix - {local_parsed_head}", starters))

    main_body.append(coll_container(content_save,
                                    f'{local_parsed_head}:{service}:{topic}', focused))

    if enders:
        main_body.append(coll_container(content_save, f"Postfix - {local_parsed_head}", enders))

    return content_save



    print()


def make_combined_html_doc(links, save_name='scrolled_conts.html'):
    with open('data/static/basic_doc2.html', 'r') as f:
        content_save = BeautifulSoup(f.read(), 'html.parser')

    for ind,(ll, service, topic) in enumerate(links):
        if ind % (len(links) // 10) == 10:
            print(f'parsed {ind} links of {len(links)}')
        parse_higlighted_doc(ll, content_save, service, topic)

    with open(f'data/aws/{save_name}', 'w') as f:
        f.write(str(content_save))


if __name__ == '__main__':
    pass
    with open('data/aws/links.txt', 'r') as f:
        links = f.read().splitlines()
    raise Exception('Wrong format links ...')
    make_combined_html_doc(links)