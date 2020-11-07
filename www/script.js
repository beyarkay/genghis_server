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

export function draw_battleground(div_id, bg_port_icon) {
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
        let square_group = row.selectAll(".square")
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
        let square = svg.selectAll('.square')
            .append("rect")
            .attr("x", d => d.x)
            .attr("y", d => d.y)
            .attr("width", d => d.width)
            .attr("height", d => d.height)
            .style("fill", d => ((d.click) % 2 === 0) ? "#ffffff" : "#a5a5a5")
            .style("stroke", "#222");

        let text = svg.selectAll('.square')
            .append("text")
            .attr("text-anchor", 'middle')
            .attr("alignment-baseline", 'middle')
            // .style("fill", d => ((d.click) % 2 === 0) ? "#a5a5a5" : "#ffffff")
            .attr("x", d => d.x + 0.5 * d.width)
            .attr("y", d => d.y + 0.5 * d.height)
            .text(d => d.content);
    });

}

export function draw_coins_per_bot(div_id) {
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