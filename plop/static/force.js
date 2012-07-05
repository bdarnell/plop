// based on http://mbostock.github.com/d3/ex/bubble.html
startDrawing = function(data) {
    var r = 3200;
    var svg = d3.select("#graph");
    svg.attr("width", r).attr("height", r);
    function node_weight(d) {
        return d.weights.calls ? Math.log(d.weights.calls) : 1;
    }
    console.log("creating force");
    var force = d3.layout.force()
        .charge(function(d) { return -500 * node_weight(d) })
        .linkDistance(function(d) { return 25 * node_weight(d) })
        .size([r,r])
        .nodes(data.nodes)
        .links(data.edges)
        .start();
    console.log("started force");
    var fill = d3.scale.category20c();


    var gnodes = svg.selectAll("g.node")
        .data(data.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);
    gnodes.append("title")
        .text(function(d) { return d.attrs.filename + ":" + d.attrs.lineno + ":" + d.attrs.funcname + ": " + d.weights.calls });
    var circles = gnodes.append("circle")
        .attr("r", function(d) { return 20 * node_weight(d) })
        .attr("fill", function(d) {return fill(d.attrs.filename) });
    var texts = gnodes.append("text")
        .text(function(d) { return d.attrs.funcname })
        .attr("text-anchor", "middle")
        .attr("dy", ".3em")
        .attr("fill", "#000");
    console.log("added nodes");

    var links = svg.selectAll("line")
        .data(data.edges)
        .enter().append("line")
        .style("stroke-width", function(d) { return Math.max(1, Math.log(d.weights.calls)) })
        .style("stroke", "#777")
        .style("stroke-opacity", 0.4)
        .attr("marker-end", "url(#Triangle)");
    console.log("added links");

    force.on("tick", function() {
        console.log("tick");
        circles.attr("cx", function(d) { return d.x })
            .attr("cy", function(d) { return d.y });
        texts.attr("x", function(d) { return d.x })
            .attr("y", function(d) { return d.y });
        links.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
        //force.stop();
    });
}

fetchData = function(filename) {
    d3.json('/data?filename=' + filename, startDrawing);
}
