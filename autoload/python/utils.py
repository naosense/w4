#!/bin/usr env python
# -.- coding: utf-8 -.-

import sys
import math
import logging

_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)


# logging.basicConfig(filename='w4.log', level=logging.DEBUG)


def log(str):
    logging.info(str)


def write(wfile, str):
    if is_py2:
        wfile.write(str)
    elif is_py3:
        wfile.write(str.encode())


def vim_lines(content):
    return content.split('\n')


def col_name_idx(lines):
    col_name_line = ''
    for line in lines:
        if line.startswith('%%') and 'who' in line:
            col_name_line = line
            break

    name_dict = {}
    col_name = col_name_line[2:].split()
    for idx, name in enumerate(col_name):
        name_dict[name] = idx + 1
    return name_dict


def col_split_char(lines):
    for line in lines:
        if line.startswith('%%') and 'col_split_char' in line:
            return line[2:].split('=')[1]
        # 提早退出
        if not line.startswith('%%'):
            return ' '

    return ' '


def vim_lines_dict(lines):
    name_dict = col_name_idx(lines)
    split_char = col_split_char(lines)
    lines_dict = {}
    for ln, line in enumerate(lines):
        if line.startswith('%%'):
            continue
        cols = line.split(split_char)
        if len(cols) < 5 or len(cols) > 6:
            continue

        timestamp = cols[0].strip()
        who = cols[name_dict['who']].strip().strip('@').split('@')
        what = cols[name_dict['what']].strip()
        when = cols[name_dict['when']].strip()
        where = cols[name_dict['where']].strip()

        link = []
        if len(cols) == 6:
            link = cols[5].strip().strip('#').split('#')

        lines_dict[timestamp] = {
            'ln': ln,
            'timestamp': timestamp,
            'who': ['@' + w for w in who],
            'what': what,
            'when': when,
            'where': where,
            'link': ['#' + w for w in link]
        }

    return lines_dict


def event_to_tooltip_html(event):
    s = '<sup><a href="#" title="' \
        + event['when'] + ', ' \
        + event['where'] \
        + ' ' \
        + (''.join(event['who']) + ': ') \
        + event['what'] \
        + '">[' \
        + event['timestamp'] \
        + ']</a></sup>'
    return s


def event_to_str(from_figure, to_figure, from_event, to_event):
    s = from_event['when'] + ', ' + from_event['where'] + ' ' + from_figure + ': ' + from_event['what'] \
        + ' => ' \
        + to_event['when'] + ', ' + to_event['where'] + ' ' + to_figure + ': ' + to_event['what']
    return s


def wrap(s, w):
    return [s[i:i + w] for i in range(0, len(s), w)]


def figure_relation_data(vim_lines_dict):
    # (张三, 李四)->[{source:event, target:event}]，表示张三指向李四的事件
    relation_dict = {}
    for source_timestamp, source_event in vim_lines_dict.items():
        if source_event['link']:
            for target_timestamp in source_event['link']:
                if source_timestamp == target_timestamp:
                    continue
                target_event = vim_lines_dict[target_timestamp]
                for source_who in source_event['who']:
                    for target_who in target_event['who']:
                        source_to_target = {'source': source_event, 'target': target_event}
                        if (source_who, target_who) in relation_dict:
                            relation_dict[(source_who, target_who)].append(source_to_target)
                        else:
                            relation_dict[(source_who, target_who)] = [source_to_target]

    # 计算人物被引用的次数，用于计算关系图中人物的大小
    who_linked_cnt = {}
    # merge(张三->李四)和(李四->张三)的关联事件
    unique_source_target_who = set()
    links = []
    for source_target_who, source_target_event in relation_dict.items():
        target_who = source_target_who[1]
        if target_who in who_linked_cnt:
            who_linked_cnt[target_who] = who_linked_cnt[target_who] + len(source_target_event)
        else:
            who_linked_cnt[target_who] = len(source_target_event)

        if source_target_who not in unique_source_target_who:
            source_who, target_who = source_target_who
            target_source_who = target_who, source_who
            source_target_event_str = [event_to_str(source_who, target_who, e['source'], e['target'])
                                       for e in source_target_event]
            if target_source_who in relation_dict:
                target_source_event = relation_dict[target_source_who]
                target_source_event_str = [event_to_str(target_who, source_who, e['source'], e['target'])
                                           for e in target_source_event]
                source_target_event_str.extend(target_source_event_str)
                unique_source_target_who.add(target_source_who)

            name = '<p>'.join(source_target_event_str)
            links.append({'source': source_who, 'target': target_who, 'name': name})
            unique_source_target_who.add((source_who, target_who))

    max_cnt = max(who_linked_cnt.values())
    max_size = 50
    scale = max_size / max_cnt
    nodes = []
    unique_who = set()
    for source_who, target_who in unique_source_target_who:
        if source_who not in unique_who:
            cnt = who_linked_cnt[source_who] if source_who in who_linked_cnt else 1
            nodes.append({
                'category': source_who,
                'name': source_who,
                'value': cnt,
                'symbolSize': 2 * math.pi if source_who not in who_linked_cnt else max(cnt * scale, 10)
            })
            unique_who.add(source_who)
        if target_who not in unique_who:
            cnt = who_linked_cnt[target_who] if target_who in who_linked_cnt else 1
            nodes.append({
                'category': target_who,
                'name': target_who,
                'value': cnt,
                'symbolSize': 2 * math.pi if target_who not in who_linked_cnt else max(cnt * scale, 10)
            })
            unique_who.add(target_who)
    return {'nodes': nodes, 'links': links, 'categories': [{'name': n} for n in unique_who]}
