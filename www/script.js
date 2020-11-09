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

// Deprecated
export function __draw_battleground__(div_id, bg_port_icon) {
    // Get the bg_map from the text file
    const cell_width = 20;
    const cell_height = 20;
    let selected_game_path = get_param("game", "");
    $.ajax({
        url: "../" + selected_game_path + "/" + bg_port_icon + '.log'
    }).done(bg_map => {
        let map = [];
        bg_map.split('\n').forEach(d => {
            if (d.length > 0) {
                map.push(d.split(''))
            }
        })

        // set the dimensions and margins of the graph
        const margin = {top: 10, right: 10, bottom: 10, left: 10};
        const width = cell_width * map[0].length;
        const height = cell_height * map.length;

        // append the svg object to the body of the page
        d3.select('#' + div_id).selectAll("svg").remove();
        const svg = d3.select('#' + div_id)
            .append("svg")
            // .attr("width", document.getElementById(div_id).offsetWidth)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

        const grid_data = [];
        let xpos = 1;
        let ypos = 1;

        for (let row = 0; row < map.length; row++) {
            grid_data.push([]);
            for (let column = 0; column < map[0].length; column++) {
                grid_data[row].push({
                    x: xpos,
                    y: ypos,
                    width: cell_width,
                    height: cell_height,
                    content: map[row][column],
                    click: 0,
                })
                xpos += cell_width;
            }
            xpos = 1;
            ypos += cell_height;
        }

        let row = svg.selectAll(".row")
            .data(grid_data)
            .enter().append("g")
            .attr("class", "row");
        const COL_HOVER = ["#eee", "#aaa"];
        const COL_NO_HOVER = ["#fff", "#aaa"];
        let square_group = row.selectAll(".cell")
            .data(d => d)
            .enter().append("g")
            .attr("class", "square")
            .on('click', function (d) {
                d.click++;
                d3.select(this).selectAll('rect').style("fill", COL_NO_HOVER[(d.click) % 2]);
                // d3.select(this).selectAll('text').style("fill", ((d.click) % 2 === 0) ? "#000000" : "#4f4f4f");
            })
            .on('mouseover', function (d) {
                d3.select(this).selectAll('rect').style("fill", COL_HOVER[(d.click) % 2]);
                // d3.select(this).selectAll('text').style("fill", ((d.click) % 2 === 0) ? "#000000" : "#1d1d1d");
            })
            .on('mouseout', function (d) {
                d3.select(this).selectAll('rect').style("fill", COL_NO_HOVER[(d.click) % 2]);
                // d3.select(this).selectAll('rect').style("fill", ((d.click) % 2 === 0) ? "#ff0000" : "#c2d000");
                // d3.select(this).selectAll('text').style("fill", ((d.click) % 2 === 0) ? "#000000" : "#000000");
            })
        ;
        let square = svg.selectAll('.cell')
            .append("rect")
            .attr("x", d => d.x)
            .attr("y", d => d.y)
            .attr("width", d => d.width)
            .attr("height", d => d.height)
            .style("fill", d => ((d.click) % 2 === 0) ? "#ffffff" : "#a5a5a5")
            .style("stroke", "#222");

        let text = svg.selectAll('.cell')
            .append("text")
            .attr("text-anchor", 'middle')
            .attr("alignment-baseline", 'middle')
            // .style("fill", d => ((d.click) % 2 === 0) ? "#a5a5a5" : "#ffffff")
            .attr("x", d => d.x + 0.5 * d.width)
            .attr("y", d => d.y + 0.5 * d.height)
            .text(d => d.content);
    });

}

function create_battleground(div_id, bg, game) {
    // set the dimensions and margins of the graph
    const margin = {top: 2, right: 8, bottom: 2, left: 8};
    const width = document.getElementById(div_id).offsetWidth;
    const height = document.getElementById(div_id).offsetHeight;
    const cell_width = (width - margin.left - margin.right) / bg['bg_map'][0].length;
    const cell_height = (height - margin.bottom - margin.top) / bg['bg_map'].length;

    // append the svg object to the body of the page
    d3.select('#' + div_id).selectAll("svg").remove();
    const svg = d3.select('#' + div_id)
        .append("svg")
        .attr("height", height + margin.top + margin.bottom)
        .attr("width", width + margin.left + margin.right)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    const grid_data = [];
    let xpos = 1;
    let ypos = 1;

    for (let col = 0; col < bg['bg_map'].length; col++) {
        grid_data.push([]);
        for (let row = 0; row < bg['bg_map'][0].length; row++) {
            grid_data[col].push({
                x: xpos,
                y: ypos,
                width: cell_width,
                height: cell_height,
                content: bg['bg_map'][row][col],
                colour: bg['bg_map'][row][col] === '#' ? 'lightgrey' : 'black',
                click: 0,
            })
            xpos += cell_width;
        }
        xpos = 1;
        ypos += cell_height;
    }

    let row = svg.selectAll(".row")
        .data(grid_data)
        .enter().append("g")
        .attr("class", "row");
    // const COL_HOVER = ["#eee", "#aaa"];
    // const COL_NO_HOVER = ["#fff", "#aaa"];
    let cell_g = row.selectAll(".cell")
        .data(d => d)
        .enter().append("g")
        .attr("class", "cell")
    // .on('click', function (d) {
    //     d.click++;
    //     d3.select(this).selectAll('rect').style("fill", COL_NO_HOVER[(d.click) % 2]);
    //     // d3.select(this).selectAll('text').style("fill", ((d.click) % 2 === 0) ? "#000000" : "#4f4f4f");
    // })
    // .on('mouseover', function (d) {
    //     d3.select(this).selectAll('rect').style("fill", COL_HOVER[(d.click) % 2]);
    //     // d3.select(this).selectAll('text').style("fill", ((d.click) % 2 === 0) ? "#000000" : "#1d1d1d");
    // })
    // .on('mouseout', function (d) {
    //     d3.select(this).selectAll('rect').style("fill", COL_NO_HOVER[(d.click) % 2]);
    //     // d3.select(this).selectAll('rect').style("fill", ((d.click) % 2 === 0) ? "#ff0000" : "#c2d000");
    //     // d3.select(this).selectAll('text').style("fill", ((d.click) % 2 === 0) ? "#000000" : "#000000");
    // });

    let cell = svg.selectAll('.cell')
        .append("rect")
        .attr("x", d => d.x)
        .attr("y", d => d.y)
        .attr("width", d => d.width)
        .attr("height", d => d.height)
        .style("fill", d => ((d.click) % 2 === 0) ? "#ffffff" : "#a5a5a5")
        .style("stroke", "#c1c1c1");

    let text = svg.selectAll('.cell')
        .append("text")
        .attr("font-size", (15 / 11.863 * cell_width).toString() + 'px')
        .attr("text-anchor", 'middle')
        .attr("alignment-baseline", 'middle')
        .attr("x", d => d.x + 0.5 * d.width)
        .attr("y", d => d.y + 0.5 * d.height)
        .attr('fill', d => d.colour ? d.colour : 'grey')
        .attr("font-weight", 'bold')
        .text(d => d.content);
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
    // console.log(graph)
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
    console.log(per_series_data);

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

export function __draw_coins_per_bot__(div_id) {
    let selected_game_path = get_param("game", "");

    $.ajax({
        url: "../" + selected_game_path + "/bot_info.json"
    }).done(bot_info => {
        let COLOURS = ["#c4ad3a",
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
        const MAX_HISTORY = 2000; // Only show ticks upto MAX_HISTORY ticks in the past
        let unique_bots = [];
        let bots = [];
        for (let i = 0; i < bot_info.length; i++) {
            if (!unique_bots.includes(bot_info[i]['bot_icon'])) {
                unique_bots.push(bot_info[i]['bot_icon']);
                bots.push([]);
            }
        }

        unique_bots.sort((a, b) => (a < b) ? -1 : 1);
        const present = d3.max(bot_info, (d) => d.tick);
        // Restructure the data. Each element in data corrosponds to a different bot's data
        for (let i = 0; i < bot_info.length; i++) {
            if (bot_info[i].tick >= present - MAX_HISTORY) {
                bots[unique_bots.indexOf(bot_info[i].bot_icon)].push(bot_info[i]);
            }
        }

        // set the dimensions and margins of the graph
        const margin = {top: 10, right: 70, bottom: 50, left: 40};
        const width = document.getElementById(div_id).offsetWidth - margin.left - margin.right
        const height = 400 - margin.top - margin.bottom

        d3.select('#' + div_id).selectAll("svg").remove();
        // append the svg object to the body of the page
        const svg = d3.select('#' + div_id)
            .append("svg")
            .attr("height", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        const xScale = d3.scaleLinear()
            .domain([Math.max(0, present - MAX_HISTORY), present])
            .range([0, width]);

        const yScale = d3.scaleLinear()
            .domain(d3.extent(bot_info, (e) => e.total_coins))
            .range([height, 0]);

        const colour = d3.scaleOrdinal()
            .domain(unique_bots)
            .range(COLOURS.splice(0, unique_bots.length));

        // Filter out all the fractional ticks for total_coins:
        const yAxisTicks = yScale.ticks()
            .filter(tick => Number.isInteger(tick));
        const yAxis = d3.axisLeft(yScale)
            .tickValues(yAxisTicks)
            .tickFormat(d3.format('d'));

        const line = d3.line()
            .x(d => xScale(d.tick))
            .y(d => yScale(d.total_coins));

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(xScale))
            .append("text")
            .attr("y", '2.5em')
            .attr("x", 0)
            .style("text-anchor", "start")
            .style("alignment-baseline", "bottom")
            .text("Game tick");

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", '-1.5em')
            .attr("x", 0)
            .style("text-anchor", "end")
            .text("Number of coins");


        let x_offset = 5;
        let y_offset = 0;
        for (let i = 0; i < bots.length; i++) {
            let legend = svg.append('g')
                .datum(bots[i])
                .attr('class', 'legend')
                .on('mouseover', () => { // on mouse in show line, circles and text
                    d3.selectAll("path.line").style("opacity", d => d[0].bot_icon === bots[i][0].bot_icon ? 1.0 : 0.3);
                })
                .on('mouseout', () => { // on mouse out hide line, circles and text
                    d3.selectAll("path.line").style("opacity", 0.9);
                });
            if (y_offset > height) {
                x_offset += 30;
                y_offset = 0;
            }

            legend.append('rect')
                .attr('x', width + x_offset)
                .attr('y', (d, _) => y_offset)
                .attr('width', 10)
                .attr('height', 10)
                .style('fill', d => colour(d[0].bot_icon));
            legend.append('text')
                .attr("alignment-baseline", 'middle')
                .attr('x', width + 12 + x_offset)
                .attr('y', (d, _) => (y_offset) + 7)
                .text(d => d[0].bot_icon);
            y_offset += 20
            svg.append("path")
                .datum(bots[i])
                .attr("class", "line")
                .style("opacity", "0.9")
                .style("stroke", d => colour(d[0].bot_icon))
                .attr("d", line)
                .on('mouseover', () => { // on mouse in show line, circles and text
                    d3.selectAll("path.line").style("opacity", d => d[0].bot_icon === bots[i][0].bot_icon ? 1.0 : 0.3);
                })
                .on('mouseout', () => { // on mouse out hide line, circles and text
                    d3.selectAll("path.line").style("opacity", "0.9");
                });

        }
    });
}

export function draw_bot_locs(div_id) {
    let selected_game_path = get_param("game", "");
    $.ajax({
        url: "../" + selected_game_path + "/bot_info.json"
    }).done(bot_info => {
        const MAX_HISTORY = 2000; // Only show ticks upto 300 ticks in the past
        let COLOURS = ["#c4ad3a",
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
        let unique_bots = [];
        let unique_battlegrounds = [];
        let bots = [];
        for (let i = 0; i < bot_info.length; i++) {
            if (!unique_bots.includes(bot_info[i]['bot_icon'])) {
                unique_bots.push(bot_info[i]['bot_icon']);
                bots.push([]);
            }
            if (!unique_battlegrounds.includes(bot_info[i]['bg_port_icon'].toString())) {
                unique_battlegrounds.push(bot_info[i]['bg_port_icon'].toString());
            }
        }
        unique_bots.sort((a, b) => (a < b) ? -1 : 1);
        unique_battlegrounds.sort((a, b) => (a < b) ? -1 : 1);
        const present = d3.max(bot_info, (d) => d.tick);
        // Restructure the data. Each element in data corrosponds to a different bot's data
        for (let i = 0; i < bot_info.length; i++) {
            if (bot_info[i].tick >= present - MAX_HISTORY) {
                bots[unique_bots.indexOf(bot_info[i].bot_icon)].push(bot_info[i]);
            }
        }

        // set the dimensions and margins of the graph
        const margin = {top: 10, right: 70, bottom: 50, left: 40};
        const width = document.getElementById(div_id).offsetWidth - margin.left - margin.right
        const height = 400 - margin.top - margin.bottom
        d3.select('#' + div_id).selectAll("svg").remove();
        // append the svg object to the body of the page
        const svg = d3.select('#' + div_id)
            .append("svg")
            .attr("height", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


        const xScale = d3.scaleLinear()
            .domain([Math.max(0, present - MAX_HISTORY), present])
            .range([0, width]);

        const yScale0 = d3.scaleBand()
            .domain(unique_battlegrounds)
            .rangeRound([height, 0])
            .paddingInner(0.5);

        // const yScale1 = d3.scaleBand()
        const yScale1 = d3.scaleBand()
            .domain(unique_bots)
            .rangeRound([0, yScale0.bandwidth()])
        // .paddingInner(0.25)
        // .domain(d3.extent(bot_info, (e) => e.total_coins))
        // .range([height, 0]);

        const colour = d3.scaleOrdinal()
            .domain(unique_bots)
            .range(COLOURS.splice(0, unique_bots.length));

        // // Filter out all the fractional ticks for total_coins:
        // const yAxisTicks = yScale.ticks()
        //     .filter(tick => Number.isInteger(tick));
        // const yAxis = d3.axisLeft(yScale)
        //     .tickValues(yAxisTicks)
        //     .tickFormat(d3.format('d'));

        const line = d3.line()
            .x(d => xScale(d.tick))
            .y(d => yScale0(d.bg_port_icon) + yScale1(d.bot_icon));

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(xScale))
            .append("text")
            .attr("y", '2.5em')
            .attr("x", 0)
            .style("text-anchor", "start")
            .style("alignment-baseline", "bottom")
            .text("Game tick");

        let yAxis = d3.axisLeft(yScale0).tickSize(0);
        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", '-1.5em')
            .attr("x", -height * 0.5)
            .style("text-anchor", "middle")
            // .style("alignment-baseline", "bottom")
            .text("Battleground");


        let x_offset = 5;
        let y_offset = 0;
        for (let i = 0; i < bots.length; i++) {
            let legend = svg.append('g')
                .datum(bots[i])
                .attr('class', 'legend')
                .on('mouseover', () => { // on mouse in show line, circles and text
                    d3.selectAll("path.line").style("opacity", d => d[0].bot_icon === bots[i][0].bot_icon ? 1.0 : 0.3);
                })
                .on('mouseout', () => { // on mouse out hide line, circles and text
                    d3.selectAll("path.line").style("opacity", "1");
                });
            if (y_offset > height) {
                x_offset += 30;
                y_offset = 0;
            }
            legend.append('rect')
                .attr('x', width + x_offset)
                .attr('y', (d, _) => y_offset)
                .attr('width', 10)
                .attr('height', 10)
                .style('fill', d => colour(d[0].bot_icon));
            legend.append('text')
                .attr("alignment-baseline", 'middle')
                .attr('x', width + 12 + x_offset)
                .attr('y', (d, _) => (y_offset) + 7)
                .text(d => d[0].bot_icon);
            y_offset += 20

            svg.append("path")
                .datum(bots[i])
                .attr("class", "line")
                .style("stroke", d => colour(d[0].bot_icon))
                .attr("d", line)
                .on('mouseover', () => { // on mouse in show line, circles and text
                    d3.selectAll("path.line").style("opacity", d => d[0].bot_icon === bots[i][0].bot_icon ? 1.0 : 0.3);
                })
                .on('mouseout', () => { // on mouse out hide line, circles and text
                    d3.selectAll("path.line").style("opacity", "1");
                });

        }
    });
}

export function update_following() {
    let cmb_following = document.getElementById("cmb_following");
    let cmb_game = document.getElementById("cmb_game");
    let forwarding_url;
    if (cmb_game.value !== 'Overview') {
        forwarding_url = 'follow.html?game=' + cmb_game.value;
        if (cmb_following.value !== 'Overview') {
            forwarding_url += '&following=' + cmb_following.value;
        }
    } else {
        forwarding_url = '../index.html';
    }
    window.location.href = forwarding_url;
}

export function cache_and_update() {
    // FIXME this fails if the client doesn't already have some of the game state
    // AJAX the current game_id and tick to get_gamestate.php
    $.ajax({
        url: "../get_gamestate.php",
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            "game_id": get_param('game', '').replace('games/', ''),
            "last_seen_tick": "1"
        })
    }).done(data => {
        // console.log(data);
        // Split the patches up into different patch objects

        // Apply each of the patches

        // const dmp = new diff_match_patch();
        // const diff = dmp.diff_main('Hello World.', 'Goodbye World.');
        // // Result: [(-1, "Hell"), (1, "G"), (0, "o"), (1, "odbye"), (0, " World.")]
        // dmp.diff_cleanupSemantic(diff);
        // // Result: [(-1, "Hello"), (1, "Goodbye"), (0, " World.")]
        // alert(diff);
    });
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
    div.appendChild(pure_g);
    for (let i = 0; i < game['battlegrounds'].length; i++) {
        let curr_bg = game['battlegrounds'][i]
        let pure_u = document.createElement("div");
        pure_u.classList.add(i < 4 ? 'pure-u-lg-6-24' : 'pure-u-lg-3-24');
        pure_u.classList.add(i < 3 ? 'pure-u-md-8-24' : 'pure-u-md-4-24');
        pure_u.classList.add(i < 2 ? 'pure-u-sm-12-24' : 'pure-u-sm-6-24');
        pure_u.classList.add(i < 1 ? 'pure-u-1-1' : 'pure-u-12-24');
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

        //     let svg = d3.select(`#d3-bg-${i}`).append("svg")
        //     svg.attr('width', '100%')
        //         .attr('height', '100%')
        //         .append('rect')
        //         .attr('width', '100%')
        //         .attr('height', '100%')
        //         .attr('fill', `hsl(${i * 20}, 90%, 60%)`);
        // }

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
