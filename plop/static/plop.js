// based on http://mbostock.github.com/d3/ex/bubble.html
startDrawing = function(data) {
    var r = 2400;
    var svg = d3.select("#graph").append("svg")
        .attr("width", r)
        .attr("height", r)
    var bubble = d3.layout.pack()
        .sort(function(d) { return -d.weights.calls })
        .size([r, r])
        .children(function(d) { if (d.weights) return []; else return d.children})
        .value(function(d) { return Math.log(d.weights.calls) });
    var fill = d3.scale.category20c();
    var gnodes = svg.selectAll("g.node")
        .data(bubble.nodes({children: data.nodes})
              .filter(function(d) { return !d.children}))
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"});
    gnodes.append("title")
        .text(function(d) { return d.attrs.filename + ":" + d.attrs.lineno + ":" + d.attrs.funcname + ": " + d.weights.calls });
    gnodes.append("circle")
        .attr("r", function(d) { return d.r })
        .attr("fill", function(d) {return fill(d.attrs.filename) });
    gnodes.append("text")
        .text(function(d) { return d.attrs.funcname.substring(0, d.r/3) })
        .attr("text-anchor", "middle")
        .attr("dy", ".3em");
}

fetchData = function() {
    d3.json('/data', startDrawing);
}
