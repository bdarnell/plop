// based on http://mbostock.github.com/d3/ex/bubble.html
(function () {
  'use strict';

  var svg,
    svgRoot,
    width = window.innerWidth,
    height = window.innerHeight;

  var zoomListener = d3.behavior.zoom()
    .scaleExtent([0.1, 3])
    .on("zoom", function(){
      svg.attr("transform", ["translate(", d3.event.translate, ")scale(", d3.event.scale, ")"].join(""));
    });

  var nodeWeight = function(d) {
    return d.weights.calls ? Math.log(d.weights.calls) : 1;
  }

  var updateWindow = function(){
    var x = window.innerWidth || document.documentElement.clientWidth;
    var y = window.innerHeight|| document.documentElement.clientHeight;

    svgRoot.attr("width", x).attr("height", y);
  }

  var dataReady = function(data) {
    svgRoot = d3.select("#graph");
    svg = svgRoot.append("g");
    zoomListener(svgRoot);
    updateWindow();
    startDrawing(data);
  };

  var startDrawing = function(data){
    console.log("creating force");
    var force = d3.layout.force()
      .charge(function(d) { return -500 * nodeWeight(d) })
      .linkDistance(function(d) { return 25 * nodeWeight(d) })
      .size([width, height])
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
      .attr("r", function(d) { return 20 * nodeWeight(d) })
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
      circles.attr("cx", function(d) { return d.x })
        .attr("cy", function(d) { return d.y });
      texts.attr("x", function(d) { return d.x })
        .attr("y", function(d) { return d.y });
      links.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
    });
  }

  window.fetchData = function(filename) {
    d3.json('/data?filename=' + filename, dataReady);
  }
  window.dataReady = dataReady;
  window.onresize = updateWindow;

})();
