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

CMD_PREFIX = '%%'
EMPTY_PLACE_HOLDER = '-'
SAME_TO_PRE_HOLDER = '--'
SAME_TO_PRE_N_HOLDER = '---'

NON_REFER_DEFAULT_SIZE = 2 * math.pi
REFER_DEFAULT_SIZE = 10
MAX_SIZE = 50


# logging.basicConfig(filename='w4.log', level=logging.DEBUG)


def log(s):
    logging.info(s)


def write(wfile, s):
    if is_py2:
        wfile.write(s)
    elif is_py3:
        wfile.write(s.encode())


def vim_lines(content):
    return content.split('\n')


def col_name_idx(lines):
    col_name_line = ''
    for line in lines:
        if line.startswith(CMD_PREFIX) and 'who' in line:
            col_name_line = line
            break

    name_dict = {}
    col_name = col_name_line[2:].split()
    for idx, name in enumerate(col_name):
        name_dict[name] = idx + 1
    return name_dict


def col_split_char(lines):
    for line in lines:
        if line.startswith(CMD_PREFIX) and 'col_split_char' in line:
            return line[2:].split('=')[1]
        # 提早退出
        if not line.startswith(CMD_PREFIX):
            return ' '

    return ' '


def vim_lines_dict(lines):
    name_dict = col_name_idx(lines)
    split_char = col_split_char(lines)
    lines_dict = {}
    items = []
    for idx, line in enumerate(lines):
        if line.startswith(CMD_PREFIX):
            continue
        cols = line.split(split_char)
        if len(cols) < 5 or len(cols) > 6:
            continue

        timestamp = cols[0].strip()
        who = col_handle(cols[name_dict['who']].strip(), 'who', items)
        what = col_handle(cols[name_dict['what']].strip(), 'what', items)
        when = col_handle(cols[name_dict['when']].strip(), 'when', items)
        where = col_handle(cols[name_dict['where']].strip(), 'where', items)

        link = []
        if len(cols) == 6:
            link = cols[5].strip().strip('#').split('#')

        item = {
            'ln': idx + 1,
            'timestamp': timestamp,
            'who': ['@' + w for w in who],
            'what': what,
            'when': when,
            'where': where,
            'link': ['#' + w for w in link]
        }
        items.append(item)
        lines_dict[timestamp] = item

    return lines_dict


def col_handle(col_str, col_name, items):
    if col_str == SAME_TO_PRE_N_HOLDER:
        for item in items[::-1]:
            col_val = item[col_name]
            if isinstance(col_val, list):
                if col_val:
                    return col_val
            else:
                if col_val != EMPTY_PLACE_HOLDER:
                    return col_val
    elif col_str == SAME_TO_PRE_HOLDER:
        last = items[-1]
        return last[col_name]
    elif col_str == EMPTY_PLACE_HOLDER:
        return ''
    else:
        if col_name == 'who':
            return col_str.strip('@').split('@')
        else:
            return col_str


def event_to_tooltip_html(event):
    s = '<sup><a href="#' + str(event['ln']) + '" title="' \
        + join_when_where(event) \
        + ' ' \
        + (''.join(event['who']) + ': ') \
        + event['what'] \
        + '">[' \
        + str(event['ln']) \
        + ']</a></sup>'
    return s


def source_target_event_to_str(source_who, target_who, source_event, target_event):
    return join_when_where(source_event) + ' ' + source_who + ': ' + source_event['what'] \
           + ' => ' \
           + join_when_where(target_event) + ' ' + target_who + ': ' + target_event['what']


def event_to_str(event):
    return join_when_where(event) + ' ' + ''.join(event['who']) + ': ' + event['what']


def join_when_where(event):
    when = event['when']
    where = event['where']
    if when and where:
        return when + ', ' + where
    elif when:
        return when
    elif where:
        return where
    else:
        return ''


def wrap(s, w):
    return [s[i:i + w] for i in range(0, len(s), w)]


def figure_relation_data(timestamp_event_dict):
    # (张三, 李四)->[{source:event, target:event}]，表示张三指向李四的事件
    relation_dict = {}
    for source_timestamp, source_event in timestamp_event_dict.items():
        if source_event['link']:
            for target_timestamp in source_event['link']:
                if source_timestamp == target_timestamp:
                    continue
                if target_timestamp not in timestamp_event_dict:
                    continue
                target_event = timestamp_event_dict[target_timestamp]
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
            source_target_event_str = [source_target_event_to_str(source_who, target_who, e['source'], e['target'])
                                       for e in source_target_event]
            if target_source_who in relation_dict:
                target_source_event = relation_dict[target_source_who]
                target_source_event_str = [source_target_event_to_str(target_who, source_who, e['source'], e['target'])
                                           for e in target_source_event]
                source_target_event_str.extend(target_source_event_str)
                unique_source_target_who.add(target_source_who)

            name = '<p>'.join(source_target_event_str)
            links.append({'source': source_who, 'target': target_who, 'name': name})
            unique_source_target_who.add((source_who, target_who))

    max_cnt = max(who_linked_cnt.values())
    scale = MAX_SIZE / max_cnt
    nodes = []
    unique_who = set()
    for source_who, target_who in unique_source_target_who:
        if source_who not in unique_who:
            cnt = who_linked_cnt[source_who] if source_who in who_linked_cnt else 1
            nodes.append({
                'category': source_who,
                'name': source_who,
                'value': cnt,
                'symbolSize': NON_REFER_DEFAULT_SIZE if source_who not in who_linked_cnt
                else max(cnt * scale, REFER_DEFAULT_SIZE)
            })
            unique_who.add(source_who)
        if target_who not in unique_who:
            cnt = who_linked_cnt[target_who] if target_who in who_linked_cnt else 1
            nodes.append({
                'category': target_who,
                'name': target_who,
                'value': cnt,
                'symbolSize': NON_REFER_DEFAULT_SIZE if target_who not in who_linked_cnt
                else max(cnt * scale, REFER_DEFAULT_SIZE)
            })
            unique_who.add(target_who)
    return {'nodes': nodes, 'links': links, 'categories': [{'name': n} for n in unique_who]}


def event_relation_data(timestamp_event_dict):
    timestamp_linked_cnt = {}
    unique_timestamp = set()
    links = []
    for source_timestamp, source_event in timestamp_event_dict.items():
        if source_event['link']:
            for target_timestamp in source_event['link']:
                if source_timestamp == target_timestamp:
                    continue
                if target_timestamp not in timestamp_event_dict:
                    continue
                if target_timestamp in timestamp_linked_cnt:
                    timestamp_linked_cnt[target_timestamp] = timestamp_linked_cnt[target_timestamp] + 1
                else:
                    timestamp_linked_cnt[target_timestamp] = 1

                unique_timestamp.add(source_timestamp)
                unique_timestamp.add(target_timestamp)
                target_event = timestamp_event_dict[target_timestamp]
                links.append({'source': str(source_event['ln']), 'target': str(target_event['ln'])})

    max_cnt = max(timestamp_linked_cnt.values())
    scale = MAX_SIZE / max_cnt
    nodes = []
    for t in unique_timestamp:
        cnt = timestamp_linked_cnt[t] if t in timestamp_linked_cnt else 1
        event = timestamp_event_dict[t]
        nodes.append({
            'category': t,
            'name': str(event['ln']),
            'desc': event_to_str(event),
            'value': cnt,
            'symbolSize': NON_REFER_DEFAULT_SIZE if t not in timestamp_linked_cnt
            else max(cnt * scale, REFER_DEFAULT_SIZE)
        })

    return {'nodes': nodes, 'links': links, 'categories': [{'name': t} for t in unique_timestamp]}
