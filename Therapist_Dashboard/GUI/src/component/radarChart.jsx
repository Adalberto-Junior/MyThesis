import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

export default function RadarChart ({ width, height, data, variables }) {
  const svgRef = useRef(null);
  const radius = Math.min(width, height) / 2;

  useEffect(() => {
    const svg = d3.select(svgRef.current).attr("width", width).attr("height", height);
    svg.selectAll("*").remove(); // Clear previous chart

    const angleSlice = (2 * Math.PI) / variables.length;
    const scale = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).range([0, radius]);

    const g = svg.append("g").attr("transform", `translate(${width / 2},${height / 2})`);

    // Draw grid
    for (let i = 0; i <= 5; i++) {
      g.append("circle")
        .attr("r", (radius / 5) * i)
        .attr("fill", "none")
        .attr("stroke", "gray")
        .attr("opacity", 0.3);
    }

    // Draw axes
    variables.forEach((d, i) => {
      const x = Math.cos(angleSlice * i - Math.PI / 2) * radius;
      const y = Math.sin(angleSlice * i - Math.PI / 2) * radius;
      g.append("line").attr("x1", 0).attr("y1", 0).attr("x2", x).attr("y2", y).attr("stroke", "gray");
    });

    // Draw data path
    const radarLine = d3.lineRadial().radius(d => scale(d.value)).angle((d, i) => i * angleSlice);
    g.append("path")
      .datum(data)
      .attr("d", radarLine)
      .attr("fill", "lightblue")
      .attr("stroke", "blue")
      .attr("opacity", 0.6);
  }, [data, width, height]);

  return <svg ref={svgRef}></svg>;
};
