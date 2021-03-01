let div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

export function get_param(param, defaultvalue) {
    if (window.location.href.indexOf(param) > -1) {
        let vars = {};
        let parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi,
            (m, key, value) => {
                vars[key] = value;
            });
        return vars[param]
    }
    return defaultvalue;
}

export function create_bg_card(div_id, game) {
    //      1st unit: pure-u-lg-8-24 pure-u-md-12-24 pure-u-1-1
    //      2nd unit: pure-u-lg-8-24 pure-u-md-12-24 pure-u-12-24
    //      3rd unit: pure-u-lg-8-24 pure-u-md-6-24 pure-u-12-24
    //      rest : pure-u-lg-4-24 pure-u-md-6-24 pure-u-12-24
    //
    // <div class="pure-u-md-8-24 pure-u-sm-12-24 pure-u-1-1">
    //     <div class="square-box-outer">
    //         <div class="square-box-inner">
    //             <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
    //                 <rect width="100%" height="100%" fill="hsl(0, 90%, 50%)"/>
    //             </svg>
    //         </div>
    //     </div>
    // </div>


    let div = document.getElementById(div_id);
    div.innerHTML = "";
    let pure_g = document.createElement("div");
    pure_g.classList.add('pure-g');
    pure_g.setAttribute('id', `bg-card-pure-g`);
    div.appendChild(pure_g);
    // game['battlegrounds'].sort((a, b) => {
    //     return a['bot_icons'].length > b['bot_icons'].length ? -1 : 1;
    // })
    for (let i = 0; i < game['battlegrounds'].length; i++) {
        let curr_bg = game['battlegrounds'][i];
        let pure_u = document.createElement("div");
        pure_u.classList.add('pure-u-lg-6-24');
        pure_u.classList.add('pure-u-md-8-24');
        pure_u.classList.add('pure-u-sm-12-24');
        pure_u.classList.add('pure-u-1-1');

        // pure_u.classList.add(i < 4 ? 'pure-u-lg-6-24' : 'pure-u-lg-3-24');
        // pure_u.classList.add(i < 3 ? 'pure-u-md-8-24' : 'pure-u-md-4-24');
        // pure_u.classList.add(i < 2 ? 'pure-u-sm-12-24' : 'pure-u-sm-6-24');
        // pure_u.classList.add(i < 1 ? 'pure-u-1-1' : 'pure-u-12-24');
        // pure_u.setAttribute('id', `bg-card-pure-u-${curr_bg['port_icon']}`);
        //pure_u.addEventListener('click', (e) => {
        //    // Re-order the game battlegrounds, then re-draw the whole thing
        //    let removed = game['battlegrounds'].splice(i, 1)[0];
        //    game['battlegrounds'].unshift(removed);
        //    create_bg_card(div_id, game)
        //});
        pure_g.appendChild(pure_u);

        let bg_title = document.createElement("h3");
        bg_title.classList.add('bg-title');
        let width = curr_bg['bg_map'].length;
        let height = curr_bg['bg_map'][0].length;
        bg_title.innerHTML = `Battleground ${curr_bg['port_icon']}`;
        pure_u.appendChild(bg_title);

        let outer_box = document.createElement("div");
        outer_box.classList.add('square-box-outer');
        pure_u.appendChild(outer_box);

        let inner_box = document.createElement("div");
        inner_box.classList.add('square-box-inner');
        inner_box.setAttribute('id', `d3-bg-${i}`);
        outer_box.appendChild(inner_box);

        create_battleground(`d3-bg-${i}`, curr_bg, game)
    }
}

export function update_bg_card(div_id, game) {
    let pure_g = d3.select('#' + div_id + " #bg-card-pure-g");
    //  game['battlegrounds'].sort((a, b) => {
    //      return a['bot_icons'].length > b['bot_icons'].length ? -1 : 1;
    //  })
    for (let i = 0; i < game['battlegrounds'].length; i++) {
        let curr_bg = game['battlegrounds'][i];
        let pure_u = document.getElementById(`bg-card-pure-u-${curr_bg['port_icon']}`);
        // pure_u.className = ""
        // pure_u.classList.add(i < 4 ? 'pure-u-lg-6-24' : 'pure-u-lg-3-24');
        // pure_u.classList.add(i < 3 ? 'pure-u-md-8-24' : 'pure-u-md-4-24');
        // pure_u.classList.add(i < 2 ? 'pure-u-sm-12-24' : 'pure-u-sm-6-24');
        // pure_u.classList.add(i < 1 ? 'pure-u-1-1' : 'pure-u-12-24');

        // Update the ith battleground
        // console.time(`update d3-bg-${i}`);
        //if (curr_bg['bot_icons'].includes(game.moving)) {
        update_battleground(`d3-bg-${i}`, curr_bg, game)
        //}
        //  console.timeEnd(`update d3-bg-${i}`);
    }
}

export function create_graph_card(div_id, game) {
    let div = document.getElementById(div_id);
    div.innerHTML = "";
    let pure_g = document.createElement("div");
    pure_g.classList.add('pure-g');
    div.appendChild(pure_g);


    let metrics = game['metrics'];

    const graph_details = {
        "game.totals.coins": {
            title: "Total Coins in the Game",
            x_axis_label: "Game ticks",
            x_axis_units: "",
            y_axis_label: "Number of Coins",
            y_axis_units: ""
        },
        "game.totals.bots": {
            title: "Total Bots in the Game",
            x_axis_label: "Game ticks",
            x_axis_units: "",
            y_axis_label: "Number of Bots",
            y_axis_units: ""
        },
        "bot.totals.coins": {
            title: "Coins per Bot over time",
            x_axis_label: "Game ticks",
            x_axis_units: "",
            y_axis_label: "Number of Coins",
            y_axis_units: ""
        },
        "bot.totals.health": {
            title: "Health per Bot over time",
            x_axis_label: "Game ticks",
            x_axis_units: "",
            y_axis_label: "Bot Health",
            y_axis_units: ""
        },
    };

    let graphs = [];

    console.log(graph_details);
    for (let i = 0; i < metrics.length; i++) {
        if (!graphs.map(e => e.name).includes(metrics[i]['name'])) {
            console.log(metrics[i]['name']);
            graphs.push({
                name: metrics[i]['name'],
                list_of_values: [],
                config: graph_details[metrics[i]['name']],
                series: []
            });
        }
        let curr_graph = graphs.find(e => e.name === metrics[i]['name']);
        curr_graph.list_of_values.push(
            metrics[i]['values']
        );
        let bot = game.bots.find(bot => {
            return bot.bot_url === metrics[i]['identifiers']['bot_url'];
        });
        curr_graph.series.push({
            series_url: bot !== undefined ? bot.bot_url : "",
            series_label: bot !== undefined ? bot.name : `Series ${curr_graph.list_of_values.length}`,
            series_id: `id${curr_graph.list_of_values.length - 1}`,
        });
    }


    for (let i = 0; i < graphs.length; i++) {
        let curr_graph = graphs[i];
        console.log(curr_graph);
        let chart_div = document.createElement('div');
        chart_div.setAttribute('id', `d3-chart-${i}`);
        let pure_u = document.createElement("div");
        pure_u.classList.add('pure-u-md-1-2', 'pure-u-1');
        pure_u.appendChild(chart_div);
        pure_g.appendChild(pure_u);
        create_graph(
            `d3-chart-${i}`,
            curr_graph,
            game
        );

    }

}

function hue_from_icon(array, cell) {
    return Math.round(((array.indexOf(cell) * (75 / 360)) % 360) * 100);
}

function create_battleground(div_id, bg, game) {
    // set the dimensions and margins of the graph
    const margin = {top: 2, right: 8, bottom: 2, left: 8};
    const width = document.getElementById(div_id).offsetWidth;
    const height = document.getElementById(div_id).offsetHeight;

    // append the svg object to the body of the page
    d3.select('#' + div_id).selectAll("svg").remove();
    const svg = d3.select('#' + div_id)
        .append("svg")
        .attr("height", height + margin.top + margin.bottom)
        .attr("width", width + margin.left + margin.right)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    update_battleground(div_id, bg, game);
}

function update_battleground(div_id, bg, game) {
    // TODO Only update if the bg actually has changed
    const margin = {top: 2, right: 8, bottom: 2, left: 8};
    const width = document.getElementById(div_id).offsetWidth;
    const height = document.getElementById(div_id).offsetHeight;
    const cell_width = (width - margin.left - margin.right) / bg['bg_map'][0].length;
    const cell_height = (height - margin.bottom - margin.top) / bg['bg_map'].length;
    const svg = d3.select('#' + div_id + " svg g");
    const div = d3.select(".tooltip");

    const text_fill_from_cell = (cell) => {
        if (cell === '#') {
            return "#626262";
        } else if (game['bot_icons'].indexOf(cell) >= 0) {
            let hue = hue_from_icon(game['bot_icons'], cell);
            return `hsl(${hue}, 100%, 50%)`;
        } else if (game['port_icons'].indexOf(cell) >= 0) {
            let hue = hue_from_icon(game['port_icons'], cell);
            return `hsl(${hue}, 100%, 25%)`;
        } else if (game['coin_icons'].indexOf(cell) >= 0) {
            let hue = hue_from_icon(game['coin_icons'], cell);
            return `hsl(${hue}, 100%, 50%)`;
        } else {
            return "#000000";
        }
    };
    const rect_fill_from_cell = (cell) => {
        if (cell === '#') {
            return text_fill_from_cell(cell);
        } else {
            return "#d9d9d9"
        }
    };
    const rect_stroke_from_cell = (cell) => {
        if (cell === '#') {
            return text_fill_from_cell(cell);
        } else if (cell_width < 10) {
            return rect_fill_from_cell(cell);
        } else {
            return "#cbcbcb"
        }
    };
    const text_font_weight_from_cell = (cell) => {
        if (cell === '#') {
            return 'light';
        } else if (game['port_icons'].includes(cell) || game['coin_icons'].includes(cell)) {
            return 'light';
        } else {
            return "bold"
        }
    };
    const mouseover_from_cell = (cell) => {
        // Tool tip vibes
        if (game['port_icons'].includes(cell) || game['bot_icons'].includes(cell) || game['coin_icons'].includes(cell)) {
            return (mouseEvent, d) => {
                let tool_tip_content;
                let pos = [];
                let port_icon = '';
                if (cell !== '' || cell !== '#') {
                    for (let bgi = 0; bgi < game['battlegrounds'].length; bgi++) {
                        if (game['battlegrounds'][bgi]['bot_icons'].includes(cell)) {
                            port_icon = game['battlegrounds'][bgi]['port_icon'];
                            let bg_map = game['battlegrounds'][bgi]['bg_map'];
                            for (let r = 0; r < bg_map.length; r++) {
                                for (let c = 0; c < bg_map[r].length; c++) {
                                    if (bg_map[r][c] === cell) {
                                        pos = [r, c];
                                        break;
                                    }
                                }
                            }
                        }
                    }
                }
                tool_tip_content = `Location: ${d.map_row}, ${d.map_col}<br>`;
                if (game['port_icons'].includes(cell)) {
                    tool_tip_content += `Port ${d.text_content} (${d.username})<br>`;

                } else if (game['bot_icons'].includes(cell)) {
                    tool_tip_content += `Bot ${d.text_content} (${d.username})<br>`;
                    tool_tip_content += `Health: ${d.bot_data.health}/100<br>`;

                    let num_coins = 0;
                    for (let i = 0; i < d.bot_data.coins.length; i++) {
                        num_coins += d.bot_data.coins[i].value;
                    }
                    tool_tip_content += `Coins: ` + num_coins + `<br>`;
                    tool_tip_content += `Last move: ${d.bot_data.move_dict.action} ${d.bot_data.move_dict.direction}<br>`;

                } else if (game['coin_icons'].includes(cell)) {
                    tool_tip_content += `Coin ${d.text_content}<br>`;
                }

                d3.select(".tooltip").transition()
                    .duration(200)
                    .style("opacity", .9);
                d3.select(".tooltip").html(tool_tip_content)
                    .style("left", (mouseEvent.pageX) + "px")
                    .style("top", (mouseEvent.pageY) + "px");
                d3.select(this).style("fill", "grey")
            }
        } else {
            return (d) => {
            };
        }
    };
    const mouseout_from_cell = (cell) => {
        // if (game['port_icons'].includes(cell) || game['bot_icons'].includes(cell)) {
        return (d) => {
            div.transition()
                .duration(200)
                .style("opacity", 0);
            d3.select(this).style("fill", rect_fill_from_cell(cell))

        }
    };
    const username_from_cell = (cell) => {
        if (game['port_icons'].includes(cell)) {
            for (let i = 0; i < game['battlegrounds'].length; i++) {
                if (game['battlegrounds'][i]['port_icon'] === cell) {
                    return game['battlegrounds'][i]['username'];
                }
            }
        } else if (game['bot_icons'].includes(cell)) {
            for (let i = 0; i < game['bots'].length; i++) {
                if (game['bots'][i]['bot_icon'] === cell) {
                    return game['bots'][i]['username'];
                }
            }
        } else {
            return 'undefined'
        }
    };
    const bot_from_cell = (cell) => {
        if (game['bot_icons'].includes(cell)) {
            for (let i = 0; i < game['bots'].length; i++) {
                if (game['bots'][i]['bot_icon'] === cell) {
                    return game['bots'][i];
                }
            }
        }
        return ''
    };


    let bot_data = [];
    let map_data = [];
    let xpos = 1;
    let ypos = 1;
    for (let col = 0; col < bg['bg_map'].length; col++) {
        bot_data.push([]);
        map_data.push([]);
        for (let row = 0; row < bg['bg_map'][0].length; row++) {
            let curr_item = bg['bg_map'][row][col];
            map_data[col].push({
                key: (game['bot_icons'].includes(curr_item)) ? curr_item : `${bg["port_icon"]}-${col}-${row}`,
                map_row: row,
                map_col: col,
                rect_x: xpos,
                rect_y: ypos,
                rect_width: cell_width,
                rect_height: cell_height,
                rect_fill: rect_fill_from_cell(curr_item),
                rect_stroke: rect_stroke_from_cell(curr_item)
            });
            bot_data[col].push({
                key: (game['bot_icons'].includes(curr_item)) ? curr_item : `${bg["port_icon"]}-${col}-${row}`,
                map_port_icon: bg['port_icon'],
                map_row: row,
                map_col: col,
                bot_data: bot_from_cell(curr_item),
                rect_x: xpos,
                rect_y: ypos,
                rect_width: cell_width,
                rect_height: cell_height,
                rect_fill: rect_fill_from_cell(curr_item),
                rect_stroke: rect_stroke_from_cell(curr_item),
                text_content: curr_item.toUpperCase() === curr_item ? curr_item : "💰",
                text_fill: text_fill_from_cell(curr_item),
                text_font_weight: text_font_weight_from_cell(curr_item),
                mouseover: mouseover_from_cell(curr_item),
                mouseout: mouseout_from_cell(curr_item),
                username: username_from_cell(curr_item),
            });
            xpos += cell_width;
        }
        xpos = 1;
        ypos += cell_height;
    }

    const t = svg.transition()
        .duration(250);

    svg.selectAll("rect")
        .data(map_data.flat(), d => d.key)
        .join(
            enter => enter.append("rect")
                .attr("x", d => d.rect_x)
                .attr("y", d => d.rect_y)
                .attr("width", d => d.rect_width)
                .attr("height", d => d.rect_height)
                .style("stroke", d => d.rect_stroke)
                .style("fill", d => d.rect_fill)
                .call(enter => enter.transition(t)
                ),

            update => update
                .attr("x", d => d.rect_x)
                .attr("y", d => d.rect_y)
                .call(update => update.transition(t)
                ),

            exit => exit
                .attr("opacity", "1")
                .call(exit => exit.transition(t)
                    .attr("opacity", "0").remove()
                )
        );

    svg.selectAll("text")
        .data(bot_data.flat(), element => element.key)
        .join(
            enter => enter.append("text")
                .attr("font-size", (1.2 * cell_width).toString() + 'px')
                .attr("text-anchor", "middle")
                .attr("x", d => d.rect_x + 0.5 * d.rect_width)
                .attr("y", d => d.rect_y + 0.9 * d.rect_height)
                .attr('fill', d => d.text_fill)
                .attr("font-weight", d => d.text_font_weight)
                .text(d => d.text_content)
                .on('mouseover', (mouseEvent, d) => d.mouseover(mouseEvent, d))
                .on('mouseout', (mouseEvent, d) => d.mouseout(mouseEvent, d))
                .attr("opacity", "0")
                .call(enter => enter.transition(t)
                    .attr("opacity", "1")
                ),

            update => update
                .call(update => update.transition(t)
                    .attr("x", d => d.rect_x + 0.5 * d.rect_width)
                    .attr("y", d => d.rect_y + 0.9 * d.rect_height)
                ),

            exit => exit
                .attr("opacity", "1")
                .call(exit => exit.transition(t)
                    .attr("opacity", "0").remove()
                )
        );
}

function create_graph(div_id, graph, game) {
    let datas = graph.list_of_values;
    let graph_config = graph.config;
    // console.log(datas);
    // set the dimensions and margins of the datas
    const margin = {top: 30, right: 10, bottom: 40, left: 40};
    const width = document.getElementById(div_id).offsetWidth - margin.left - margin.right;
    const height = 200 - margin.top - margin.bottom;

    let data = [];
    let extent_x = [0, 0];
    let extent_y = [0, 0];
    for (let ds_idx = 0; ds_idx < datas.length; ds_idx++) {
        let coords = [];
        for (let item_idx = 0; item_idx < datas[ds_idx].length; item_idx++) {
            extent_y[0] = Math.min(extent_y[0], datas[ds_idx][item_idx][0]);
            extent_y[1] = Math.max(extent_y[1], datas[ds_idx][item_idx][0]);
            extent_x[0] = Math.min(extent_x[0], datas[ds_idx][item_idx][1]);
            extent_x[1] = Math.max(extent_x[1], datas[ds_idx][item_idx][1]);
            coords.push({
                y: datas[ds_idx][item_idx][0],
                x: datas[ds_idx][item_idx][1],
                id: `${ds_idx}`
            })
        }
        data.push({
            id: `${ds_idx}`,
            coords: coords,
            series_label: graph.series[ds_idx].series_label,
            series_id: graph.series[ds_idx].series_id,
            series_url: graph.series[ds_idx].series_url
        })

    }
    // console.log(data);
    const xScale = d3.scaleLinear()
        .range([0, width])
        .domain(extent_x);

    const yScale = d3.scaleLinear()
        .rangeRound([height, 0])
        .domain(extent_y);


    // ---------------------------------------------
    // Append the svg object to the body of the page
    // ---------------------------------------------
    d3.select('#' + div_id).selectAll("svg").remove();
    const svg = d3.select('#' + div_id)
        .append("svg")
        .attr("height", height + margin.top + margin.bottom)
        .attr("width", width + margin.left + margin.right)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    const yaxis = d3.axisLeft().scale(yScale);
    const xaxis = d3.axisBottom().scale(xScale);

    const lineCreator = d3.line()
        .x(function (d) {
            return xScale(d.x);
        })
        .y(function (d) {
            return yScale(d.y);
        });


    // ----------
    // Title text
    // ----------
    svg.append("text")
        .attr("transform", "translate(" + (width / 2) + " ," +
            (-margin.top * 0.2) + ")")
        .style("text-anchor", "middle")
        .style("font-weight", "middle")
        .style("font-size", "18px")
        .text(graph_config.title);

    // ---------------------
    // X axis label and axes
    // ---------------------
    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xaxis);

    let x_axis_text = `${graph_config.x_axis_label}`;
    if (graph_config.x_axis_units !== "") {
        x_axis_text += ` (${graph_config.x_axis_units})`
    }
    svg.append("text")
        .attr("transform", "translate(" + (width) + " ," +
            (height + margin.bottom * 0.9) + ")")
        .style("text-anchor", "end")
        .style("font-size", "15px")
        .text(x_axis_text);

    // ---------------------
    // Y axis label and axes
    // ---------------------
    svg.append("g")
        .attr("class", "axis")
        .call(yaxis);

    let y_axis_text = `${graph_config.y_axis_label}`;
    if (graph_config.y_axis_units !== "") {
        y_axis_text += ` (${graph_config.y_axis_units})`
    }
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x", 0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .style("font-size", "15px")
        .text(y_axis_text);


    // -----------------------------
    // Lines and path configurations
    // -----------------------------
    const lines = svg.selectAll("lines")
        .data(data)
        .enter()
        .append("g");

    lines.append("path")
        .attr("d", d => lineCreator(d.coords))
        .on("mouseout", (mouseEvent, d) => {
            d3.selectAll(".bot-id" + d.id)
                .classed("selected", false);
        })
        .on("mouseover", (mouseEvent, d) => {
            d3.selectAll(".bot-id" + d.id)
                .classed("selected", true);
        })
        .attr("class", (d) => "bot-id" + d.id + " line should-color")
        .style("stroke", (d) => `hsl(${hue_from_icon(data.map(e => e.id), d.id)}, 100%, 50%)`);

    // -------------------------
    // Legend and legend entries
    // -------------------------
    if (data.length > 1) {
        let legend_entries = svg.append("g")
            .attr("class", "legend_group")
            .selectAll("g");

        legend_entries
            .data(data).enter()
            .append("text")
            .attr("x", (d) => (d.id * 50))
            .attr("y", height + margin.bottom * 0.9)
            .attr("class", (d) => "bot-id" + d.id + " ")
            .style("font-size", "12px")
            .on("mouseout", (mouseEvent, d) => {
                d3.selectAll(".bot-id" + d.id)
                    .classed("selected", false);
            })
            .on("mouseover", (mouseEvent, d) => {
                d3.selectAll(".bot-id" + d.id)
                    .classed("selected", true);
            })
            .text((d) => d.series_label);

        legend_entries.data(data).enter().append("circle")
            .attr("class", (d) => "bot-id" + d.id + " should-color")
            .style("fill", (d) => `hsl(${hue_from_icon(data.map(e => e.id), d.id)}, 100%, 50%)`)
            .attr("cx", (d) => (d.id * 50) - 5)
            .attr("cy", height + margin.bottom * 0.9 - 4)
            .on("mouseout", (mouseEvent, d) => {
                d3.selectAll(".bot-id" + d.id).classed("selected", false);
            })
            .on("mouseover", (mouseEvent, d) => {
                d3.selectAll(".bot-id" + d.id).classed("selected", true);
            })
            .attr("r", 3);
    }
}


