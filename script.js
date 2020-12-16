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


    let div = document.getElementById(div_id)
    div.innerHTML = "";
    let pure_g = document.createElement("div");
    pure_g.classList.add('pure-g')
    pure_g.setAttribute('id', `bg-card-pure-g`);
    div.appendChild(pure_g);
   // game['battlegrounds'].sort((a, b) => {
   //     return a['bot_icons'].length > b['bot_icons'].length ? -1 : 1;
   // })
    for (let i = 0; i < game['battlegrounds'].length; i++) {
        let curr_bg = game['battlegrounds'][i]
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
    let pure_g = d3.select('#' + div_id + " #bg-card-pure-g")
  //  game['battlegrounds'].sort((a, b) => {
  //      return a['bot_icons'].length > b['bot_icons'].length ? -1 : 1;
  //  })
    for (let i = 0; i < game['battlegrounds'].length; i++) {
        let curr_bg = game['battlegrounds'][i]
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
    let div = document.getElementById(div_id)
    div.innerHTML = "";
    let pure_g = document.createElement("div");
    pure_g.classList.add('pure-g')
    div.appendChild(pure_g);
    for (let i = 0; i < game['graphs'].length; i++) {
        let curr_graph = game['graphs'][i];
        if (curr_graph['id'] === 'events') {
            continue;
        }

        let pure_u = document.createElement("div");
        pure_u.classList.add('pure-u-1');

        let bg_title = document.createElement("h3");
        bg_title.classList.add('chart-title');
        bg_title.innerHTML = curr_graph.title;
        pure_u.appendChild(bg_title);

        let chart_div = document.createElement('div');
        chart_div.setAttribute('id', `d3-chart-${i}`);
        pure_u.appendChild(chart_div);

        pure_g.appendChild(pure_u);


        create_graph(`d3-chart-${i}`, curr_graph, game);

        // let svg = d3.select(`#d3-chart-${i}`).append("svg")
        // let width = Math.random() * 1000 + 400;
        // svg.attr('width', width + 'px')
        //     .attr('height', '300px')
        //     .append('rect')
        //     .attr('width', width + 'px')
        //     .attr('height', '300px')
        //     .attr('fill', `hsl(${300 - i * 20}, 90%, 60%)`);
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
    let div = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    update_battleground(div_id, bg, game);
}

function update_battleground(div_id, bg, game) {
    // TODO Only update if the bg actually has changed
    const margin = {top: 2, right: 8, bottom: 2, left: 8};
    const width = document.getElementById(div_id).offsetWidth;
    const height = document.getElementById(div_id).offsetHeight;
    const cell_width = (width - margin.left - margin.right) / bg['bg_map'][0].length;
    const cell_height = (height - margin.bottom - margin.top) / bg['bg_map'].length;
    const svg = d3.select('#' + div_id + " svg g")
    const div = d3.select(".tooltip")
    const text_fill_from_cell = (cell) => {
        if (cell === '#') {
            return "#626262";
        } else if (game['bot_icons'].indexOf(cell) >= 0) {
            let hue = hue_from_icon(game['bot_icons'], cell)
            return `hsl(${hue}, 100%, 50%)`;
        } else if (game['port_icons'].indexOf(cell) >= 0) {
            let hue = hue_from_icon(game['port_icons'], cell)
            return `hsl(${hue}, 100%, 25%)`;
        } else if (game['coin_icons'].indexOf(cell) >= 0) {
            let hue = hue_from_icon(game['coin_icons'], cell)
            return `hsl(${hue}, 100%, 50%)`;
        } else {
            return "#000000";
        }
    }
    const rect_fill_from_cell = (cell) => {
        if (cell === '#') {
            return text_fill_from_cell(cell);
            // } else if (game['bot_icons'].indexOf(cell) >= 0) {
            //     // return "none"
            //     let hue = hue_from_icon(game['bot_icons'], cell)
            //     return `hsl(${hue}, 20%, 80%)`;
            // } else if (game['port_icons'].indexOf(cell) >= 0) {
            //     return "none"
            // let hue = hue_from_icon(game['port_icons'], cell)
            // return `hsl(${hue}, 20%, 80%)`
        } else {
            return "#d9d9d9"
        }
    }
    const rect_stroke_from_cell = (cell) => {
        if (cell === '#') {
            return text_fill_from_cell(cell);
            // } else if (game['bot_icons'].indexOf(cell) >= 0) {
            //     // let hue = hue_from_icon(game['bot_icons'], cell)
            //     // return `hsl(${hue}, 100%, 80%)`;
            //     return rect_fill_from_cell(cell);
            // } else if (game['port_icons'].indexOf(cell) >= 0) {
            //     return rect_fill_from_cell(cell);
        } else if (cell_width < 10) {
            return rect_fill_from_cell(cell);
        } else {
            return "#cbcbcb"
        }
    }
    const text_font_weight_from_cell = (cell) => {
        if (cell === '#') {
            return 'light';
        } else if (game['port_icons'].includes(cell) || game['coin_icons'].includes(cell)) {
            return 'light';
        } else {
            return "bold"
        }
    }
    const mouseover_from_cell = (cell) => {
        // Tool tip vibes
        if (game['port_icons'].includes(cell) || game['bot_icons'].includes(cell) || game['coin_icons'].includes(cell)) {
            return (mouseEvent, d) => {
                let tool_tip_content;
                let pos = [];
                let port_icon = '';
                if (cell !== '' || cell !== '#') {
                    for (let bgi = 0; bgi < game['battlegrounds'].length; bgi++){
                        if (game['battlegrounds'][bgi]['bot_icons'].includes(cell)) {
                            port_icon = game['battlegrounds'][bgi]['port_icon'];
                            let bg_map = game['battlegrounds'][bgi]['bg_map'];
                            for (let r = 0; r < bg_map.length; r ++) {
                                for (let c = 0; c < bg_map[r].length; c ++) {
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
                    console.log(d)
                    tool_tip_content += `Bot ${d.text_content} (${d.username})<br>`;
                    tool_tip_content += `Health: ${d.bot_data.health}/100<br>`;
                    tool_tip_content += `Coins: [ `;
                    for (let i = 0; i < d.bot_data.coins.length; i++) {
                        let coin = d.bot_data.coins[i];
                        tool_tip_content += `${coin.value}x '${coin.originator_icon.toLowerCase()}'`;
                        if (i !== d.bot_data.coins.length - 1 ) {
                            tool_tip_content += `, `;
                        }
                    }
                    tool_tip_content += ` ]<br>`;
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
    }
    const mouseout_from_cell = (cell) => {
        // if (game['port_icons'].includes(cell) || game['bot_icons'].includes(cell)) {
        return (d) => {
            div.transition()
                .duration(200)
                .style("opacity", 0);
            d3.select(this).style("fill", rect_fill_from_cell(cell))

        }
    }
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
    }
    const bot_from_cell = (cell) => {
        if (game['bot_icons'].includes(cell)) {
            for (let i = 0; i < game['bots'].length; i++) {
                if (game['bots'][i]['bot_icon'] === cell) {
                    return game['bots'][i];
                }
            }
        } 
        return ''
    }
    

    let data = [];
    let xpos = 1;
    let ypos = 1;
    for (let col = 0; col < bg['bg_map'].length; col++) {
        data.push([]);
        for (let row = 0; row < bg['bg_map'][0].length; row++) {
            data[col].push({
                key: (game['bot_icons'].includes(bg['bg_map'][row][col])) ? bg['bg_map'][row][col] : `${bg["port_icon"]}-${col}-${row}`,
                map_port_icon: bg['port_icon'],
                map_row: row,
                map_col: col,
                bot_data: bot_from_cell(bg['bg_map'][row][col]),
                rect_x: xpos,
                rect_y: ypos,
                rect_width: cell_width,
                rect_height: cell_height,
                rect_fill: rect_fill_from_cell(bg['bg_map'][row][col]),
                rect_stroke: rect_stroke_from_cell(bg['bg_map'][row][col]),
                text_content: bg['bg_map'][row][col],
                text_fill: text_fill_from_cell(bg['bg_map'][row][col]),
                text_font_weight: text_font_weight_from_cell(bg['bg_map'][row][col]),
                mouseover: mouseover_from_cell(bg['bg_map'][row][col]),
                mouseout: mouseout_from_cell(bg['bg_map'][row][col]),
                username: username_from_cell(bg['bg_map'][row][col]),
            })
            xpos += cell_width;
        }
        xpos = 1;
        ypos += cell_height;
    }

    const t = svg.transition()
        .duration(500);

    svg.selectAll("rect")
      .data(data.flat(), element => element.key)
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
      .data(data.flat(), element => element.key)
      .join(
        enter => enter.append("text")
            .attr("font-size", (1.2 * cell_width).toString() + 'px')
            .attr("text-anchor", 'middle')
            .attr("alignment-baseline", 'middle')
            .attr("x", d => d.rect_x + 0.5 * d.rect_width)
            .attr("y", d => d.rect_y + 0.6 * d.rect_height)
            .attr('fill', d => d.text_fill)
            .attr("font-weight", d => d.text_font_weight)
            .text(d => d.text_content)
            .on('mouseover', (mouseEvent, d) => d.mouseover(mouseEvent, d))
            .on('mouseout', (mouseEvent, d) => d.mouseout(mouseEvent, d))
            .on('mouseout', (d, i) => i.mouseout(i))
            .attr("opacity", "0")
          .call(enter => enter.transition(t)
              .attr("opacity", "1")
            ),

        update => update
          .call(update => update.transition(t)
            .attr("x", d => d.rect_x + 0.5 * d.rect_width)
            .attr("y", d => d.rect_y + 0.6 * d.rect_height)
            ),

        exit => exit
            .attr("opacity", "1")
          .call(exit => exit.transition(t)
            .attr("opacity", "0").remove()
          )
      );
}

function init_graph() {
}

function create_coins_per_bot() {
}

function update_coins_per_bot() {
}

function create_bot_locations() {
}

function update_bot_locations() {
}

function create_graph(div_id, graph, game) {
    const COLOURS = ["#c4ad3a",
        "#715fcd",
        "#73b638",
        "#c24cb5",
        "#4fbd6a",
        "#da4478",
        "#55b48f",
        "#d04934",
        "#49b9d3",
        "#d9842d",
        "#6380c5",
        "#687428",
        "#be86dd",
        "#3d7d3e",
        "#d983b3",
        "#a3b165",
        "#97487a",
        "#97692f",
        "#b35355",
        "#e29371"]

    // set the dimensions and margins of the graph
    const tick_width = 10
    const margin = {top: 10, right: 10, bottom: 40, left: 40};
    const width = game.tick * tick_width;
    const height = 300;

    let unique_series = [];
    let per_series_data = []
    for (let i = 0; i < graph.data.length; i++) {
        if (!unique_series.includes(graph.data[i][graph.series_key])) {
            unique_series.push(graph.data[i][graph.series_key]);
            per_series_data.push([]);
        }
    }
    unique_series.sort((a, b) => (a < b) ? -1 : 1);
    // Restructure the data. Each element in data corrosponds to a different series' data
    for (let i = 0; i < graph.data.length; i++) {
        per_series_data[unique_series.indexOf(graph.data[i][graph.series_key])].push(graph.data[i]);
    }

    // append the svg object to the body of the page
    d3.select('#' + div_id).selectAll("svg").remove();
    const svg = d3.select('#' + div_id)
        .append("svg")
        .attr("height", height + margin.top + margin.bottom)
        .attr("width", width + margin.left + margin.right)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    const xScale = d3.scaleLinear()
        .domain([game.tick, 0])
        .range([0, width]);

    const yScale = d3.scaleLinear()
        .domain(d3.extent(graph.data, d => d[graph.y_key]))
        .range([height, 0]);

    const colour = d3.scaleOrdinal()
        .domain(unique_series)
        .range(COLOURS.splice(0, unique_series.length));

    // Filter out all the fractional ticks:
    const yAxisTicks = yScale.ticks()
        .filter(tick => Number.isInteger(tick));
    const yAxis = d3.axisLeft(yScale)
        .tickValues(yAxisTicks)
        .tickFormat(d3.format('d'));


    const lineGenerator = d3.line()
        .x(d => xScale(d[graph.x_key]))
        .y(d => yScale(d[graph.y_key]));

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale))
        .append("text")
        .attr("y", '2.5em')
        .attr("x", 0)
        .style("text-anchor", "start")
        .style("alignment-baseline", "bottom")
        .text(graph.x_label);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", '-1.5em')
        .attr("x", 0)
        .style("text-anchor", "end")
        .text(graph.y_label);

    let series = svg.selectAll(".series")
        .data(per_series_data)
        .enter().append("g")
        .attr("class", "series");

    series.append("path")
        .attr("class", "line")
        .attr("d", d => lineGenerator(d))
        .style("stroke", d => {
            return colour(d[0].bot_icon);
        });

    // series.append("text")
    //     .datum(function (d) {
    //         return {
    //             name: d.name,
    //             value: d.values[d.values.length - 1]
    //         };
    //     })
    //     .attr("transform", d => "translate(" + xScale(d.value[graph.x_key]) + "," + yScale(d.value[graph.y_key]) + ")")
    //     .attr("x", 3)
    //     .attr("dy", ".35em")
    //     .text(d => d.name);

    // series.selectAll("circle")
    //     .data(d => d.values)
    //     .enter()
    //     .append("circle")
    //     .attr("r", 3)
    //     .attr("cx", d => xScale(d[graph.x_key]))
    //     .attr("cy", d => yScale(d[graph.y_key]))
    //     .style("fill", (d, i, j) => colour(series[j].name));
}


