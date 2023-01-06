$(document).ready(function () {
    let is_empty = function (s) {
        return s === null || s === undefined || s === '';
    };

    let display_figure_relation_graph = function (graph) {
        let container = echarts.init(document.getElementById('graph'));
        let option = {
            title: {
                text: '风云际会',
                top: 'top',
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: function (params) {
                    return params['data']['name'];
                },
                extraCssText: "max-width:400px; white-space:pre-wrap; font-size: 50%"
            },
            // legend: [{
            //     data: graph.categories.map(function (a) {
            //         return a.name;
            //     })
            // }],
            series: [
                {
                    name: 'figure relation',
                    type: 'graph',
                    layout: 'force',
                    force: {
                        edgeLength: [50, 300],
                        repulsion: 500,
                        gravity: 0.02
                    },
                    draggable: true,
                    data: graph.nodes,
                    links: graph.links,
                    categories: graph.categories,
                    roam: true,
                    label: {
                        show: true,
                        position: 'right',
                        formatter: '{b}'
                    },
                    labelLayout: {
                        hideOverlap: true
                    },
                    emphasis: {
                        focus: 'adjacency',
                        lineStyle: {
                            width: 3
                        },
                        label: {
                            show: true,
                            position: 'right',
                            formatter: '{b}'
                        }
                    },
                    lineStyle: {
                        curveness: 0.3
                    }
                }
            ]
        };
        container.setOption(option, true);

        window.onresize = function() {
            container.resize();
        };
    };

    let display_event_relation_graph = function (graph) {
        let container = echarts.init(document.getElementById('graph'));
        let option = {
            title: {
                text: '来龙去脉',
                top: 'top',
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: function (params) {
                    if (params['dataType'] === 'edge') {
                        return params['name'];
                    }
                    return params['data']['desc'];
                },
                extraCssText: "max-width:400px; white-space:pre-wrap; font-size: 50%"
            },
            series: [
                {
                    name: 'event relation',
                    type: 'graph',
                    layout: 'force',
                    force: {
                        edgeLength: [50, 300],
                        repulsion: 500,
                        gravity: 0.02
                    },
                    draggable: true,
                    edgeSymbol: ['circle', 'arrow'],
                    edgeSymbolSize: [0, 7],
                    data: graph.nodes,
                    links: graph.links,
                    categories: graph.categories,
                    roam: true,
                    label: {
                        show: true,
                        position: 'right',
                        formatter: '{b}'
                    },
                    labelLayout: {
                        hideOverlap: true
                    },
                    emphasis: {
                        focus: 'adjacency',
                        lineStyle: {
                            width: 3
                        },
                        label: {
                            show: true,
                            position: 'right',
                            formatter: '{b}'
                        }
                    },
                    lineStyle: {
                        curveness: 0.3
                    }
                }
            ]
        };
        container.setOption(option, true);

        window.onresize = function() {
            container.resize();
        };
    };

    $(function () {
        $(document).tooltip();
    });

    $(function () {
        let cmd = ['/all', '/characters', '/events'];
        $('#kw').autocomplete({
            source: function (req, resp) {
                let re = $.ui.autocomplete.escapeRegex(req.term);
                let matcher = new RegExp('^' + re, 'i');
                let a = $.grep(cmd, function (item, index) {
                    return matcher.test(item);
                });
                resp(a);
            }
        });
    });

    let url = new URL(window.location.href)
    $.get(
        'http://127.0.0.1:' + url.port + '/query.json?kw=' + encodeURIComponent('/all'),
        function (data) {
            let html = '<table><caption>故事线</caption>';
            $.each(data.data, function (i, e) {
                html += e;
            })
            html += '</table>'
            $('.markdown-body').html(html);
        },
        'json'
    );

    $(document).keypress(function (e) {
        let mask = $('#mask');
        switch (e.keyCode) {
            case 13:
                if (mask.css('display') === 'none') {
                    mask.css({'display': 'block'});
                    setTimeout(function () {
                        $("#kw").focus();
                    }, 50)
                } else {
                    mask.css({'display': 'none'});
                    let kw = $('#kw').val();
                    if (is_empty(kw)) {
                        return;
                    }
                    $.get(
                        'http://127.0.0.1:' + url.port + '/query.json?kw=' + encodeURIComponent(kw),
                        function (data) {
                            $("#kw").val('')
                            switch (kw) {
                                case '/characters':
                                case '/events':
                                    $('#graph').css({'display': 'block'});
                                    $('.markdown-body').html('')
                                    if (kw === '/characters') {
                                        display_figure_relation_graph(data.data);
                                    } else if (kw === '/events') {
                                        display_event_relation_graph(data.data);
                                    }
                                    break;
                                case '/all':
                                default:
                                    $('#graph').css({'display': 'none'});
                                    let html = '<table><caption>故事线</caption>';
                                    $.each(data.data, function (i, e) {
                                        html += e;
                                    })
                                    html += '</table>'
                                    $('.markdown-body').html(html);
                            }
                        },
                        'json'
                    );
                }
                break;
            case 27:
                mask.css({'display': 'none'});
                break
        }
    });
});