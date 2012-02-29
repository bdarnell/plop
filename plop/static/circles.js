// based on http://mbostock.github.com/d3/ex/bubble.html
startDrawing = function(data) {
    var r = 1000;
    function calls_value(d) {
        if (d.weights)
            return d.weights.calls;
        else
            return d3.sum(d.values, calls_value);
    }
    function time_value(d) {
        if (d.weights)
            return d.weights.time;
        else
            return d3.sum(d.values, time_value);
    }
    var pack = d3.layout.pack()
        .size([r, r])
        .children(function(d) { return d.values })
        .value(calls_value);

    var svg = d3.select("#graph");
    var fill = d3.scale.category20c();

    var hier_data = d3.nest()
        .key(function(d) { return d.attrs.filename })
        .entries(data.nodes);
    hier_data = [{'key': 'root', 'values': hier_data}];
    console.log(hier_data);

    function cell() {
        this.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
        this.select("circle")
            .attr("r", function(d) { return d.r });
        this.select("text")
            .text(function(d) { return d.attrs.funcname.substring(0, d.r/3)});
    }
    
    var node = svg.data(hier_data).selectAll("g.node")
        .data(pack.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(cell);
    
    node.append("title")
        .text(function(d) { return d.values ? null : (d.attrs.filename  + ":" + d.attrs.lineno + ":" + d.attrs.funcname)});

    node.append("circle")
        .attr("r", function(d) { return d.r })
        .attr("opacity", function(d) { if (d.key=='root') return 0.1; return d.values ? 0.2 : 0.6})
        .attr("fill", function(d) { return d.key ? fill(d.key) : fill(d.attrs.filename)});

    node.filter(function(d) { return !d.values }).append("text")
        .attr("text-anchor", "middle")
        .attr("dy", ".3em")
        .text(function(d) { return d.attrs.funcname.substring(0, d.r/3)});

    d3.select("#calls").on("click", function() {
        svg.selectAll("g.node")
            .data(pack.value(calls_value))
            .transition()
            .duration(1000)
            .call(cell);
    });
    d3.select("#time").on("click", function() {
        svg.selectAll("g.node")
            .data(pack.value(time_value))
            .transition()
            .duration(1000)
            .call(cell);
        
    });

}

fetchData = function() {
    d3.json('/data', startDrawing);
}
