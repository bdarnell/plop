// based on http://mbostock.github.com/d3/ex/bubble.html
startDrawing = function(data) {
    var r = 1200;
    var treemap = d3.layout.treemap()
        .size([r,r])
        .sticky(true)
        .children(function(d) { return d.values })
        .value(function(d) { return d.weights.calls });

    var div = d3.select("#treemap");
    var fill = d3.scale.category20c();

    var hier_data = d3.nest()
        .key(function(d) { return d.attrs.filename })
        .entries(data.nodes);

    div.data([{'key': 'root', 'values':hier_data}]).selectAll("div")
        .data(treemap.nodes)
        .enter().append("div")
        .attr("class", "cell")
        .style("background", function (d) { return d.values ? fill(d.key) : null })
        .text(function(d) { return d.values ? null : d.attrs.funcname })
        .attr("title", function(d) { return d.values ? null : (d.attrs.filename  + ":" + d.attrs.lineno + ":" + d.attrs.funcname)})
        .call(cell);

    d3.select("#calls").on("click", function() {
        d3.selectAll("line").remove();
        div.selectAll("div")
            .data(treemap.value(function(d) { return d.weights.calls }))
            .transition()
            .duration(1000)
            .call(cell);
                 
    });
    d3.select("#time").on("click", function() {
        d3.selectAll("line").remove();
        div.selectAll("div")
            .data(treemap.value(function(d) { return d.weights.time }))
            .transition()
            .duration(1000)
            .call(cell);
                 
    });

    function cell() {
        this.style("left", function(d) { return d.x + "px" })
            .style("top", function(d) { return d.y + "px" })
            .style("width", function(d) { return Math.max(0, d.dx-1) + "px"})
            .style("height", function(d) { return Math.max(0, d.dy-1) + "px"})
            .style("position", "absolute")
            .style("overflow", "hidden")
            .style("border", "solid 1px white")
        ;
    }

    d3.selectAll("div.cell")
        .on("click", function() {
            var mydatum = d3.select(this).datum();

            
            var svg = d3.select("#overlay");
            svg.selectAll("line")
                .data(data.edges.filter(function(d) { return (data.nodes[d.source] == mydatum || data.nodes[d.target] == mydatum) }))
                .enter().append("line")
                .attr("x1", function(d) { var n = data.nodes[d.source]; return n.x + (n.dx/2) })
                .attr("y1", function(d) { var n = data.nodes[d.source]; return n.y + (n.dy/2) })
                .attr("x2", function(d) { var n = data.nodes[d.source]; return n.x + (n.dx/2) })
                .attr("y2", function(d) { var n = data.nodes[d.source]; return n.y + (n.dy/2) })
                .style("stroke", "#000")
                .style("stroke-width", function(d) { return Math.max(1, Math.log(d.weights.calls)) })
                .style("stroke-opacity", 0.6)
                .attr("marker-end", "url(#Triangle)")
                .transition()
                .duration(1000)
                .attr("x2", function(d) { var n = data.nodes[d.target]; return n.x + (n.dx/2) })
                .attr("y2", function(d) { var n = data.nodes[d.target]; return n.y + (n.dy/2) })
            ;
        })
;
    /**/
}

fetchData = function() {
    d3.json('/data', startDrawing);
}
