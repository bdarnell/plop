// based on http://mbostock.github.com/d3/ex/bubble.html
startDrawing = function(data) {
    var r = 1600;
    var svg = d3.select("#graph").append("svg")
        .attr("width", r)
        .attr("height", r)
    console.log("creating force");
    var force = d3.layout.force()
        .charge(-320)
        .linkDistance(200)
        .size([r,r])
        .nodes(data.nodes)
        .links(data.edges)
        .start();
    console.log("started force");
    var fill = d3.scale.category20c();

    var links = svg.selectAll("line")
        .data(data.edges)
        .enter().append("line")
        .style("stroke-width", 3)
        .style("stroke", "#777")
        .style("stroke-opacity", 0.6);
    console.log("added links");

    var gnodes = svg.selectAll("g.node")
        .data(data.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);
    gnodes.append("title")
        .text(function(d) { return d.attrs.filename + ":" + d.attrs.lineno + ":" + d.attrs.funcname + ": " + d.weights.calls });
    var circles = gnodes.append("circle")
        .attr("r", function(d) { return 4*Math.log(d.weights.calls) })
        .attr("fill", function(d) {return fill(d.attrs.filename) });
    var texts = gnodes.append("text")
        .text(function(d) { return d.attrs.funcname })
        .attr("text-anchor", "middle")
        .attr("dy", ".3em")
        .attr("fill", "#000");
    console.log("added nodes");


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

fetchData = function() {
    d3.json('/data', startDrawing);
}
