$(document).ready(function () {

    function updateWithState(state) {
       /*
{
  "games": [
    "game_2020-04-24T00:55:45.688987"
  ],
  "nodes": [
    "game_2020-04-24T00:55:45.688987/MSHSTU001",
    "game_2020-04-24T00:55:45.688987/KNXBOY001"
  ]
}
       */
        // update the schedule card
        let ul = document.getElementById("node_list");
        ul.innerHTML = "";
        console.log(state);
        for (let i = 0; i < state['nodes'].length; i++) {
            let li = document.createElement("li");
            let sn = state['nodes'][i].split("/")[1];
            let a = document.createElement("a");
            a.setAttribute('href', `https://people.cs.uct.ac.za/~KNXBOY001/gm/${sn}`);
            a.innerHTML = sn;
            li.appendChild(a);
            ul.appendChild(li);
        }

    }

    function loadD3() {
        let svg = d3.select("svg");
        let width = +svg.attr("width");
        let height = +svg.attr("height");
        
        var simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(function(d) { return d.id; }))
            //.force("charge", d3.forceManyBody().strength(-200))
        		.force('charge', d3.forceManyBody()
              .strength(-200)
              .theta(0.8)
              .distanceMax(150)
            )
        // 		.force('collide', d3.forceCollide()
        //       .radius(d => 40)
        //       .iterations(2)
        //     )
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        
        const graph = {
          "nodes": [
            {"id": "1", "group": 1, "label": 'KNXBOY001'},
            {"id": "2", "group": 2, "label": 'NCHABE003'},
            {"id": "3", "group": 3, "label": 'MMBMUH004'},
            {"id": "4", "group": 4, "label": 'HYWLUC001'},
            {"id": "5", "group": 5, "label": 'MSHSTU001'},
            {"id": "6", "group": 1, "label": 'WBHMIK002'},
            {"id": "7", "group": 2, "label": 'RBCANN002'},
            {"id": "8", "group": 3, "label": 'FSTJON003'},
            {"id": "9", "group": 4, "label": 'GRHMAR992'},
            {"id": "10", "group": 5, "label": 'MXMBRK002'}
          ],
          "links": [
            {"source": "1", "target": "2", "value": 1},
            {"source": "2", "target": "3", "value": 1},
            {"source": "3", "target": "4", "value": 1},
            {"source": "4", "target": "5", "value": 1},
            {"source": "5", "target": "6", "value": 1},
            {"source": "6", "target": "7", "value": 1},
            {"source": "7", "target": "8", "value": 1},
            {"source": "8", "target": "9", "value": 1},
            {"source": "9", "target": "10", "value": 1},
            {"source": "10", "target": "1", "value": 1},
            {"source": "5", "target": "3", "value": 1},
            {"source": "1", "target": "9", "value": 1},
            {"source": "8", "target": "2", "value": 1},
            {"source": "3", "target": "6", "value": 1},
          ]
        }
          
          
        function run(graph) {
          
          graph.links.forEach(function(d){
        //     d.source = d.source_id;    
        //     d.target = d.target_id;
          });           
        
          var link = svg.append("g")
                        .style("stroke", "#aaa")
                        .selectAll("line")
                        .data(graph.links)
                        .enter().append("line");
        
          var node = svg.append("g")
                    .attr("class", "nodes")
          .selectAll("circle")
                    .data(graph.nodes)
          .enter().append("circle")
                  .attr("r", 2)
                  .call(d3.drag()
                      .on("start", dragstarted)
                      .on("drag", dragged)
                      .on("end", dragended));
          
          var label = svg.append("g")
              .attr("class", "labels")
              .selectAll("text")
              .data(graph.nodes)
              .enter().append("text")
                .attr("class", "label")
                .text(function(d) { return d.label; });
        
          simulation
              .nodes(graph.nodes)
              .on("tick", ticked);
        
          simulation.force("link")
              .links(graph.links);
        
          function ticked() {
            link
                .attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });
        
            node
                 .attr("r", 16)
                 .style("fill", "#efefef")
                 .style("stroke", "#424242")
                 .style("stroke-width", "1px")
                 .attr("cx", function (d) { return d.x+5; })
                 .attr("cy", function(d) { return d.y-3; });
            
            label
            		.attr("x", function(d) { return d.x; })
                    .attr("y", function (d) { return d.y; })
                    .style("font-size", "10px").style("fill", "#333");
          }
        }
        
        function dragstarted(d) {
          if (!d3.event.active) simulation.alphaTarget(0.3).restart()
          d.fx = d.x
          d.fy = d.y
        //  simulation.fix(d);
        }
        
        function dragged(d) {
          d.fx = d3.event.x
          d.fy = d3.event.y
        //  simulation.fix(d, d3.event.x, d3.event.y);
        }
        
        function dragended(d) {
          d.fx = d3.event.x
          d.fy = d3.event.y
          if (!d3.event.active) simulation.alphaTarget(0);
          //simulation.unfix(d);
        }
          
        run(graph)    
    }
    loadD3();
    $.ajaxSetup({cache: false});
    let interval = 250;
    function update() {
        $.when($.ajax('state.json'))
            .then(function (stateResponse) {
                //console.log(stateResponse);

                updateWithState(stateResponse);

            }, function () {
                console.log('Error while loading gamestate/layout');
            });
        setTimeout(update, interval);
    }

    setTimeout(update, interval);


});
