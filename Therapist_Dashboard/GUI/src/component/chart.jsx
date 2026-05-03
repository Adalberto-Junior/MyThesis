import React, { useRef, useEffect, useState, useMemo } from "react";
import * as d3 from 'd3';


export function RadarChart({
  data,
  width = 600,
  height = 500,
  levels = 10,
  margin = { top: 60, right: 60, bottom: 60, left: 60 },
  maxValue
}) {
  const ref = useRef();

  useEffect(() => {
    // console.log("Dados recebidos pelo RadarChart:", data);
    const svg = d3.select(ref.current);
    svg.selectAll('*').remove();

    // Preparação para lidar com valores negativos
    const values = data.map(d => d.value);
    const minVal = d3.min(values);
    const maxValOrig = maxValue ?? d3.max(values);
    const offset = minVal < 0 ? -minVal : 0;
    const maxVal = maxValOrig + offset;

    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;
    const cx = margin.left + innerW / 2;
    const cy = margin.top + innerH / 2;
    const radius = Math.min(innerW, innerH) / 2;
    const allAxes = data.map(d => d.axis);
    const total = allAxes.length;
    const angleSlice = (Math.PI * 2) / total;

    // Escala linear de 0 a maxVal para [0, radius]
    const rScale = d3.scaleLinear()
      .domain([0, maxVal])
      .range([0, radius]);

    const g = svg.append('g')
      .attr('transform', `translate(${cx},${cy})`);

    // Desenha níveis de grid
    for (let lvl = 0; lvl < levels; lvl++) {
      const rLvl = radius * ((lvl + 1) / levels);
      g.append('circle')
        .attr('r', rLvl)
        .style('fill', 'none')
        .style('stroke', '#bbb')
        .style('stroke-width', '0.5px');
      g.append('text')
        .attr('x', 4)
        .attr('y', -rLvl)
        .attr('dy', '0.4em')
        .style('font-size', '10px')
        .style('fill', '#666')
        .text(((lvl + 1) * maxVal / levels - offset).toFixed(2));
    }

    // Eixos e legendas
    const axis = g.selectAll('.axis')
      .data(allAxes)
      .enter().append('g')
      .attr('class', 'axis');

    axis.append('line')
      .attr('x1', 0).attr('y1', 0)
      .attr('x2', (_, i) => rScale(maxVal * 1.05) * Math.cos(angleSlice * i - Math.PI/2))
      .attr('y2', (_, i) => rScale(maxVal * 1.05) * Math.sin(angleSlice * i - Math.PI/2))
      .style('stroke', '#ccc')
      .style('stroke-width', '1px');

    // axis.append('text')
    //   .attr('class', 'legend')
    //   .attr('x', (_, i) => rScale(maxVal * 1.15) * Math.cos(angleSlice * i - Math.PI/2))
    //   .attr('y', (_, i) => rScale(maxVal * 1.15) * Math.sin(angleSlice * i - Math.PI/2))
    //   .attr('dy', '0.35em')
    //   .style('font-size', '11px')
    //   .style('fill', '#333')
    //   .style('text-anchor', 'middle')
    //   .text(d => d);
    
    // axis.append('text')
    //   .attr('class', 'legend')
    //   .attr('text-anchor', 'middle')
    //   .attr('transform', (_, i) => {
    //     const angleDeg = (angleSlice * i * 180 / Math.PI) - 90;
    //     const x = rScale(maxVal * 1.15) * Math.cos(angleSlice * i - Math.PI/2);
    //     const y = rScale(maxVal * 1.15) * Math.sin(angleSlice * i - Math.PI/2);
    //     return `translate(${x}, ${y}) rotate(${angleDeg})`;
    //   })
    //   .style('font-size', '11px')
    //   .style('fill', '#333')
    //   .text(d => d);

    axis.append('text')
      .attr('class', 'legend')
      .attr('text-anchor', 'middle')
      .attr('transform', (_, i) => {
        const angle = angleSlice * i;
        const angleDeg = angle * 180 / Math.PI - 90;

        const x = rScale(maxVal * 1.15) * Math.cos(angle - Math.PI/2);
        const y = rScale(maxVal * 1.15) * Math.sin(angle - Math.PI/2);

        // Se o ângulo estiver entre 90° e 270°, invertemos (para manter leitura correta)
        const flip = angleDeg > 90 && angleDeg < 270 ? 180 : 0;

        return `translate(${x}, ${y}) rotate(${angleDeg + flip})`;
      })
      .style('font-size', '11px')
      .style('fill', '#333')
      .text((d, i) => d);



    // Gerar a área do radar ajustando cada valor com offset
    const radarLine = d3.lineRadial()
      .radius(d => rScale(d.value + offset))
      .angle((_, i) => i * angleSlice)
      .curve(d3.curveLinearClosed);

    g.append('path')
      .datum(data)
      .attr('d', radarLine)
      .style('fill', '#3b82f6')
      .style('fill-opacity', 0.3)
      .style('stroke', '#3b82f6')
      .style('stroke-width', '2px');

    // Pontos interativos + tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute')
      .style('background', '#fff')
      .style('padding', '4px 8px')
      .style('border', '1px solid #999')
      .style('border-radius', '4px')
      .style('pointer-events', 'none')
      .style('opacity', 0);

    g.selectAll('.radarCircle')
      .data(data)
      .enter().append('circle')
      .attr('class', 'radarCircle')
      .attr('r', 4)
      .attr('cx', (_, i) => rScale(data[i].value + offset) * Math.cos(angleSlice * i - Math.PI/2))
      .attr('cy', (_, i) => rScale(data[i].value + offset) * Math.sin(angleSlice * i - Math.PI/2))
      .style('fill', '#3b82f6')
      .style('fill-opacity', 0.8)
      .on('mouseover', (event, d) => {
        tooltip.transition().duration(200).style('opacity', 0.9);
        tooltip.html(`<strong>${d.axis}</strong>: ${d.value.toFixed(2)}`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', () => tooltip.transition().duration(200).style('opacity', 0));
  }, [data, width, height, levels, margin, maxValue]);

  return (
    <svg ref={ref} width={width} height={height}></svg>
  );
}



// src/component/charts.jsx (atualize apenas o BarChart)
export function BarChart({ data, width = 400, height = 200, margin = { top: 20, right: 20, bottom: 30, left: 40 } }) {
  const ref = useRef();

  useEffect(() => {
    const svg = d3.select(ref.current);
    svg.selectAll('*').remove();

    // calcula domínio considerando negativos
    const minVal = d3.min(data);
    const maxVal = d3.max(data);
    const yDomain = [Math.min(0, minVal), Math.max(0, maxVal)];

    const x = d3.scaleBand()
      .domain(data.map((_, i) => i))
      .range([margin.left, width - margin.right])
      .padding(0.1);

    const y = d3.scaleLinear()
      .domain(yDomain)
      .nice()
      .range([height - margin.bottom, margin.top]);

    const g = svg.append('g');

    // eixos
    g.append('g')
      .attr('transform', `translate(0,${y(0)})`)       // baseline no zero
      .call(d3.axisBottom(x).tickFormat(i => i + 1));

    g.append('g')
      .attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(y));

    // tooltip (como antes)
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute')
      .style('background', '#fff')
      .style('padding', '4px 8px')
      .style('border', '1px solid #999')
      .style('border-radius', '4px')
      .style('pointer-events', 'none')
      .style('opacity', 0);

    // desenha barras acima e abaixo da baseline
    g.selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', (_, i) => x(i))
      .attr('y', d => d >= 0 ? y(d) : y(0))               // se negativo, partem da base
      .attr('height', d => Math.abs(y(d) - y(0)))        // altura sempre positiva
      .attr('width', x.bandwidth())
      .style('fill', '#3b82f6')
      .on('mouseover', (event, d) => {
        tooltip.transition().duration(200).style('opacity', 0.9);
        tooltip.html(d.toFixed(2))
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', () => tooltip.transition().duration(200).style('opacity', 0));
  }, [data, width, height, margin]);

  return <svg ref={ref} width={width} height={height}></svg>;
}

// src/component/StaticBarChart.jsx
// import React, { useRef, useEffect } from 'react';
// import * as d3 from 'd3';

export function StaticBarChart({
  data,             // [{ axis: 'avg_BBEon_1', value:  -2.5 }, ...]
  width = 600,
  height = 400,
  margin = { top: 20, right: 20, bottom: 30, left: 120 }
}) {
  const ref = useRef();

  useEffect(() => {
    if (!data || data.length === 0) return;

    const svg = d3.select(ref.current);
    svg.selectAll('*').remove();

    // eixos
    const x = d3.scaleLinear()
      .domain([
        d3.min(data, d => d.value),
        d3.max(data, d => d.value)
      ])
      .nice()
      .range([margin.left, width - margin.right]);

    const y = d3.scaleBand()
      .domain(data.map(d => d.axis))
      .range([margin.top, height - margin.bottom])
      .padding(0.1);

    // bars
    svg.append('g')
      .selectAll('rect')
      .data(data)
      .enter()
      .append('rect')
        .attr('x', d => x(Math.min(0, d.value)))
        .attr('y', d => y(d.axis))
        .attr('width', d => Math.abs(x(d.value) - x(0)))
        .attr('height', y.bandwidth())
        .attr('fill', d => d.value >= 0 ? '#3b82f6' : '#f87171')
      .on('mouseover', (event, d) => {
        tooltip
          .style('opacity', 1)
          .html(`<strong>${d.axis}</strong>: ${d.value.toFixed(2)}`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', () => tooltip.style('opacity', 0));

    // X Axis
    svg.append('g')
      .attr('transform', `translate(0,${margin.top})`)
      .call(d3.axisTop(x).ticks(5));

    // Y Axis
    svg.append('g')
      .attr('transform', `translate(${x(0)},0)`)
      .call(d3.axisLeft(y).tickSize(0))
      .selectAll('text')
        .style('font-size', '0.85em');

    // Tooltip
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute')
      .style('background', '#fff')
      .style('padding', '4px 8px')
      .style('border', '1px solid #999')
      .style('border-radius', '4px')
      .style('pointer-events', 'none')
      .style('opacity', 0);

  }, [data, width, height, margin]);

  return <svg ref={ref} width={width} height={height}></svg>;
}


export function LineChart({ data }) {
  const ref = useRef();

  useEffect(() => {
    d3.select(ref.current).selectAll("*").remove();
    if (!data || data.length < 2) return;

    const margin = { top: 20, right: 20, bottom: 50, left: 50 };
    const width = 1150 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = d3
      .select(ref.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom);

    const chart = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Escalas
    const x = d3
      .scalePoint()
      .domain(data.map((d) => d.axis))
      .range([0, width]);

    const y = d3
      .scaleLinear()
      .domain([d3.min(data, (d) => d.value) - 1, d3.max(data, (d) => d.value) + 1])
      .range([height, 0]);

    // Eixos
    chart
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .attr("transform", "rotate(-45)")
      .style("text-anchor", "end");

    chart.append("g").call(d3.axisLeft(y));

    // Linha
    const line = d3
      .line()
      .x((d) => x(d.axis))
      .y((d) => y(d.value));

    chart
      .append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "#4f46e5")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Tooltip container
    const tooltip = d3
      .select(ref.current)
      .append("div")
      .style("position", "absolute")
      .style("background", "#fff")
      .style("border", "1px solid #ccc")
      .style("border-radius", "4px")
      .style("padding", "6px 10px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("opacity", 0)
      .style("box-shadow", "0 2px 6px rgba(0, 0, 0, 0.2)");

    // Pontos
    chart
      .selectAll("circle")
      .data(data)
      .enter()
      .append("circle")
      .attr("cx", (d) => x(d.axis))
      .attr("cy", (d) => y(d.value))
      .attr("r", 4)
      .attr("fill", "#4f46e5")
      .on("mouseover click", function (event, d) {
        const bounds = ref.current.getBoundingClientRect();
        tooltip
          .html(`<strong>${d.axis}</strong><br/>Valor: ${d.value}`)
          .style("left", `${event.clientX - bounds.left + 10}px`)
          .style("top", `${event.clientY - bounds.top - 30}px`)
          .style("opacity", 1);
      })
      .on("mouseout", () => tooltip.style("opacity", 0));
  }, [data]);

  return <div ref={ref} style={{ position: "relative" }} />;
}

// Gráficos por categoria
export function LineChartCategory({ dataGroup }) {
  const ref = useRef();

  useEffect(() => {
    d3.select(ref.current).selectAll("*").remove();

    if (!dataGroup || Object.keys(dataGroup).length === 0) return;

    const margin = { top: 20, right: 30, bottom: 50, left: 50 };
    const width = 1150 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = d3
      .select(ref.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Pegar todos os pontos de tempo
    const allAxis = new Set();
    const allValues = [];

    Object.values(dataGroup).forEach(series => {
      series.forEach(d => {
        allAxis.add(d.axis);
        allValues.push(d.value);
      });
    });

    const x = d3.scalePoint()
      .domain(Array.from(allAxis))
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([d3.min(allValues) - 1, d3.max(allValues) + 1])
      .range([height, 0]);

    // Eixos
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .attr("transform", "rotate(-45)")
      .style("text-anchor", "end");

    svg.append("g").call(d3.axisLeft(y));

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Tooltip container
    const tooltip = d3.select(ref.current)
      .append("div")
      .style("position", "absolute")
      .style("background", "#fff")
      .style("border", "1px solid #ccc")
      .style("padding", "4px 8px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("opacity", 0);

    // Linhas e círculos
    Object.entries(dataGroup).forEach(([label, series], index) => {
      const line = d3.line()
        .x(d => x(d.axis))
        .y(d => y(d.value));

      svg.append("path")
        .datum(series)
        .attr("fill", "none")
        .attr("stroke", color(index))
        .attr("stroke-width", 2)
        .attr("d", line);

      svg.selectAll(`.circle-${label}`)
        .data(series)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.axis))
        .attr("cy", d => y(d.value))
        .attr("r", 3)
        .attr("fill", color(index))
        .on("mouseover", function (event, d) {
          tooltip
            .html(`<strong>${label}</strong><br/>${d.axis}: ${d.value}`)
            .style("left", `${event.pageX + 10}px`)
            .style("top", `${event.pageY - 28}px`)
            .style("opacity", 1);
        })
        .on("mouseout", () => tooltip.style("opacity", 0));
    });
  }, [dataGroup]);

  return <div ref={ref} style={{ position: "relative" }} />;
}



// export function AcousticSpaceD3({ data }) {
//   const svgRef = useRef();

//   useEffect(() => {
//     if (!data || data.length === 0) return;

//     const margin = { top: 20, right: 30, bottom: 40, left: 50 };
//     const width = 600 - margin.left - margin.right;
//     const height = 500 - margin.top - margin.bottom;

//     const svg = d3.select(svgRef.current)
//       .attr("width", width + margin.left + margin.right)
//       .attr("height", height + margin.top + margin.bottom);

//     svg.selectAll("*").remove(); // limpar SVG

//     const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

//     // Escalas invertidas
//     const x = d3.scaleLinear()
//       .domain(d3.extent(data, d => d.F2)).nice()
//       .range([width, 0]); // invertido

//     const y = d3.scaleLinear()
//       .domain(d3.extent(data, d => d.F1)).nice()
//       .range([0, height]); // invertido

//      const tooltip = d3
//       .select(svgRef.current)
//       .append("div")
//       .style("position", "absolute")
//       .style("background", "#fff")
//       .style("border", "1px solid #ccc")
//       .style("border-radius", "4px")
//       .style("padding", "6px 10px")
//       .style("font-size", "12px")
//       .style("pointer-events", "none")
//       .style("opacity", 0)
//       .style("box-shadow", "0 2px 6px rgba(0, 0, 0, 0.2)");

//     // Eixos
//     g.append("g")
//       .attr("transform", `translate(0,${height})`)
//       .call(d3.axisBottom(x))
//       .append("text")
//       .attr("x", width / 2)
//       .attr("y", 35)
//       .attr("fill", "#000")
//       .text("F2 (Hz)");

//     g.append("g")
//       .call(d3.axisLeft(y))
//       .append("text")
//       .attr("transform", "rotate(-90)")
//       .attr("x", -height / 2)
//       .attr("y", -40)
//       .attr("fill", "#000")
//       .text("F1 (Hz)");

//     // Pontos + etiquetas
//     g.selectAll(".dot")
//       .data(data)
//       .enter()
//       .append("circle")
//       .attr("cx", d => x(d.F2))
//       .attr("cy", d => y(d.F1))
//       .attr("r", 5)
//       .style("fill", "#4e79a7");

//     g.selectAll(".label")
//       .data(data)
//       .enter()
//       .append("text")
//       .attr("x", d => x(d.F2))
//       .attr("y", d => y(d.F1) - 10)
//       .attr("text-anchor", "middle")
//       .text(d => d.id)
//       .style("font-size", "14px");

//   }, [data]);

//   return <svg ref={svgRef}></svg>;
// };


export function AcousticSpaceD31({ data }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || data.length === 0) return;

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = 900 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom);

    svg.selectAll("*").remove(); // limpar SVG

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    g.append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", width)
    .attr("height", height)
    .style("fill", "none")
    .style("stroke", "#000")
    .style("stroke-width", 2);

    // Escalas invertidas
    const x = d3.scaleLinear()
      .domain(d3.extent(data, d => d.F2)).nice()
      .range([width, 0]); // invertido

    const y = d3.scaleLinear()
      .domain(d3.extent(data, d => d.F1)).nice()
      .range([0, height]); // invertido
      

    // Grade
    const xGrid = d3.axisBottom(x).tickSize(-height).tickFormat("");
    const yGrid = d3.axisLeft(y).tickSize(-width).tickFormat("");

    // Eixo X com grid cinzenta
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x)
        .tickSize(-height)  // ativa linhas da grid
        .tickPadding(10))
      .selectAll(".tick line")
      .attr("stroke", "#ccc") // cinzento claro
      .select(".domain").remove();

    // Eixo Y com grid cinzenta
    g.append("g")
      .call(d3.axisLeft(y)
        .tickSize(-width)   // ativa linhas da grid
        .tickPadding(10))
      .selectAll(".tick line")
      .attr("stroke", "#ccc") // cinzento claro
      .select(".domain").remove();

    // g.append("g")
    //   .attr("class", "x grid")
    //   .attr("transform", `translate(0,${height})`)
    //   .call(xGrid);

    // g.append("g")
    //   .attr("class", "y grid")
    //   .call(yGrid);

    // Eixos
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .append("text")
      .attr("x", width / 2)
      .attr("y", 35)
      .attr("fill", "#000")
      .text("F2 (Hz)");

    g.append("g")
      .call(d3.axisLeft(y))
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", -40)
      .attr("fill", "#000")
      .text("F1 (Hz)");

    // Tooltip (div flutuante)
    const tooltip = d3.select("body")
      .append("div")
      .style("position", "absolute")
      .style("background", "#fff")
      .style("border", "1px solid #ccc")
      .style("padding", "8px")
      .style("border-radius", "6px")
      .style("pointer-events", "none")
      .style("font-size", "18px")
      .style("opacity", 0);

    // Pontos + eventos de tooltip
    g.selectAll(".dot")
      .data(data)
      .enter()
      .append("circle")
      .attr("cx", d => x(d.F2))
      .attr("cy", d => y(d.F1))
      .attr("r", 5)
      .style("fill", "#4e79a7")
      .on("mouseover", (event, d) => {
        tooltip.transition().duration(200).style("opacity", 1);
        tooltip.html(`<strong>${d.id}</strong><br>F1: ${d.F1} Hz<br>F2: ${d.F2} Hz`)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 30) + "px");
      })
      .on("mouseout", () => {
        tooltip.transition().duration(200).style("opacity", 0);
      });

    // Etiquetas (opcional)
    g.selectAll(".label")
      .data(data)
      .enter()
      .append("text")
      .attr("x", d => x(d.F2))
      .attr("y", d => y(d.F1) - 10)
      .attr("text-anchor", "middle")
      .text(d => d.id)
      .style("font-size", "16px");

  }, [data]);

  return <svg ref={svgRef}></svg>;
}

//################Modernizado########################
export function AcousticSpaceD3({ data = [] }) {
  const svgRef = useRef();

  // Margens e dimensões são estáticos → useMemo evita recriação
  const { width, height, margin } = useMemo(() => {
    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    return {
      margin,
      width: 800 - margin.left - margin.right,
      height: 500 - margin.top - margin.bottom,
    };
  }, []);

  // Escalas são recalculadas quando os dados mudam
  const xScale = useMemo(() => {
    return d3.scaleLinear()
      .domain(d3.extent(data, d => d.F2))
      .nice()
      .range([width, 0]); // invertido
  }, [data, width]);

  const yScale = useMemo(() => {
    return d3.scaleLinear()
      .domain(d3.extent(data, d => d.F1))
      .nice()
      .range([0, height]); // invertido
  }, [data, height]);

  useEffect(() => {
    const svg = d3.select(svgRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom);

    svg.selectAll("*").remove(); // Limpa o SVG antes de redesenhar

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Fundo
    g.append("rect")
      .attr("width", width)
      .attr("height", height)
      .style("fill", "none")
      .style("stroke", "#000")
      .style("stroke-width", 2);

    // Eixo X
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickSize(-height).tickPadding(10))
      .call(g => g.selectAll(".tick line").attr("stroke", "#ccc"))
      .call(g => g.select(".domain").remove());

    // Eixo Y
    g.append("g")
      .call(d3.axisLeft(yScale).tickSize(-width).tickPadding(10))
      .call(g => g.selectAll(".tick line").attr("stroke", "#ccc"))
      .call(g => g.select(".domain").remove());

    // Labels de eixos
    g.append("text")
      .attr("x", width / 2)
      .attr("y", height + 35)
      .attr("text-anchor", "middle")
      .attr("fill", "#000")
      .text("F2 (Hz)");

    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", -40)
      .attr("text-anchor", "middle")
      .attr("fill", "#000")
      .text("F1 (Hz)");

    // Tooltip (criado uma vez e atualizado nos eventos)
    const tooltip = d3.select("body")
      .append("div")
      .attr("class", "tooltip")
      .style("position", "absolute")
      .style("background", "#fff")
      .style("border", "1px solid #ccc")
      .style("padding", "8px")
      .style("border-radius", "6px")
      .style("pointer-events", "none")
      .style("font-size", "14px")
      .style("opacity", 0);

    // Pontos
    g.selectAll(".dot")
      .data(data)
      .enter()
      .append("circle")
      .attr("cx", d => xScale(d.F2))
      .attr("cy", d => yScale(d.F1))
      .attr("r", 5)
      .attr("fill", "#4e79a7")
      .on("mouseover", (event, d) => {
        tooltip.transition().duration(150).style("opacity", 1);
        tooltip
          .html(`<strong>${d.id.replace(/_/g, " ")}</strong><br>F1: ${d.F1} Hz<br>F2: ${d.F2} Hz`)
          .style("left", `${event.pageX + 10}px`)
          .style("top", `${event.pageY - 30}px`);
      })
      .on("mouseout", () => tooltip.transition().duration(150).style("opacity", 0));

    // Etiquetas
    g.selectAll(".label")
      .data(data)
      .enter()
      .append("text")
      .attr("x", d => xScale(d.F2))
      .attr("y", d => yScale(d.F1) - 10)
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .text(d => d.id.replace(/_/g, " "));

    // Limpeza do tooltip ao desmontar o componente
    return () => tooltip.remove();

  }, [data, xScale, yScale, width, height, margin]);

  return <svg ref={svgRef} className="w-full h-auto" />;
}



// export function AcousticSpaceD3V2({ data }) {
//   const svgRef = useRef();

//   useEffect(() => {
//     if (!data || data.length === 0) return;

//     const margin = { top: 20, right: 30, bottom: 40, left: 50 };
//     const width = 600 - margin.left - margin.right;
//     const height = 500 - margin.top - margin.bottom;

//     const svg = d3.select(svgRef.current)
//       .attr("width", width + margin.left + margin.right)
//       .attr("height", height + margin.top + margin.bottom);

//     svg.selectAll("*").remove(); // limpar SVG

//     const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

//     g.append("rect")
//       .attr("x", 0)
//       .attr("y", 0)
//       .attr("width", width)
//       .attr("height", height)
//       .style("fill", "none")
//       .style("stroke", "#000")
//       .style("stroke-width", 2);

//     const x = d3.scaleLinear()
//       .domain(d3.extent(data, d => d.F2)).nice()
//       .range([width, 0]);

//     const y = d3.scaleLinear()
//       .domain(d3.extent(data, d => d.F1)).nice()
//       .range([0, height]);

//     // Eixos com grid
//     g.append("g")
//       .attr("transform", `translate(0,${height})`)
//       .call(d3.axisBottom(x).tickSize(-height).tickPadding(10))
//       .selectAll(".tick line").attr("stroke", "#ccc");

//     g.append("g")
//       .call(d3.axisLeft(y).tickSize(-width).tickPadding(10))
//       .selectAll(".tick line").attr("stroke", "#ccc");

//     g.append("g")
//       .attr("transform", `translate(0,${height})`)
//       .call(d3.axisBottom(x))
//       .append("text")
//       .attr("x", width / 2)
//       .attr("y", 35)
//       .attr("fill", "#000")
//       .text("F2 (Hz)");

//     g.append("g")
//       .call(d3.axisLeft(y))
//       .append("text")
//       .attr("transform", "rotate(-90)")
//       .attr("x", -height / 2)
//       .attr("y", -40)
//       .attr("fill", "#000")
//       .text("F1 (Hz)");

//     // Paleta de cores por data
//     const labels = Array.from(new Set(data.map(d => d.label)));
//     const color = d3.scaleOrdinal().domain(labels).range(d3.schemeCategory10);

//     const tooltip = d3.select("body")
//       .append("div")
//       .style("position", "absolute")
//       .style("background", "#fff")
//       .style("border", "1px solid #ccc")
//       .style("padding", "8px")
//       .style("border-radius", "4px")
//       .style("pointer-events", "none")
//       .style("font-size", "14px")
//       .style("opacity", 0);

//     // Pontos
//     g.selectAll(".dot")
//       .data(data)
//       .enter()
//       .append("circle")
//       .attr("cx", d => x(d.F2))
//       .attr("cy", d => y(d.F1))
//       .attr("r", 5)
//       .style("fill", d => color(d.label || "default"))
//       .on("mouseover", (event, d) => {
//         tooltip.transition().duration(200).style("opacity", 1);
//         tooltip.html(`<strong>${d.id}</strong><br>F1: ${d.F1} Hz<br>F2: ${d.F2} Hz<br>Data: ${d.label}`)
//           .style("left", (event.pageX + 10) + "px")
//           .style("top", (event.pageY - 30) + "px");
//       })
//       .on("mouseout", () => {
//         tooltip.transition().duration(200).style("opacity", 0);
//       });

//     // Etiquetas dos pontos
//     g.selectAll(".label")
//       .data(data)
//       .enter()
//       .append("text")
//       .attr("x", d => x(d.F2))
//       .attr("y", d => y(d.F1) - 10)
//       .attr("text-anchor", "middle")
//       .text(d => d.id)
//       .style("font-size", "14px");

//     // Legenda
//     const legend = svg.append("g")
//       .attr("transform", `translate(${margin.left},${height + margin.top + 60})`);

//     labels.forEach((label, i) => {
//       const legendRow = legend.append("g")
//         .attr("transform", `translate(${i * 160}, 0)`);

//       legendRow.append("rect")
//         .attr("width", 14)
//         .attr("height", 14)
//         .attr("fill", color(label));

//       legendRow.append("text")
//         .attr("x", 20)
//         .attr("y", 12)
//         .attr("fill", "#000")
//         .style("font-size", "14px")
//         .text(label);
//     });

//     // Cleanup do tooltip ao desmontar
//     return () => {
//       tooltip.remove();
//     };

//   }, [data]);

//   return <svg ref={svgRef}></svg>;
// }


// export function AcousticSpaceD3V2({ data }) {
//   const svgRef = useRef();

//   useEffect(() => {
//     if (!data || data.length === 0) return;

//     // --- Configuração básica ---
//     const margin = { top: 20, right: 30, bottom: 60, left: 50 };
//     const width = 600 - margin.left - margin.right;
//     const height = 500 - margin.top - margin.bottom;

//     const svg = d3
//       .select(svgRef.current)
//       .attr("width", width + margin.left + margin.right)
//       .attr("height", height + margin.top + margin.bottom);

//     svg.selectAll("*").remove(); // limpa o conteúdo

//     const g = svg
//       .append("g")
//       .attr("transform", `translate(${margin.left},${margin.top})`);

//     // --- Escalas (mantendo inversão para F1/F2) ---
//     const x = d3
//       .scaleLinear()
//       .domain(d3.extent(data, (d) => d.F2))
//       .nice()
//       .range([width, 0]);

//     const y = d3
//       .scaleLinear()
//       .domain(d3.extent(data, (d) => d.F1))
//       .nice()
//       .range([0, height]);

//     // --- Fundo / Moldura ---
//     g.append("rect")
//       .attr("x", 0)
//       .attr("y", 0)
//       .attr("width", width)
//       .attr("height", height)
//       .attr("fill", "none")
//       .attr("stroke", "#333")
//       .attr("stroke-width", 1.5);

//     // --- Eixos + Grid ---
//     const xAxis = d3.axisBottom(x).tickSize(-height).tickPadding(8);
//     const yAxis = d3.axisLeft(y).tickSize(-width).tickPadding(8);

//     g.append("g")
//       .attr("transform", `translate(0,${height})`)
//       .call(xAxis)
//       .call((g) => g.selectAll(".tick line").attr("stroke", "#ccc"))
//       .call((g) => g.select(".domain").remove())
//       .append("text")
//       .attr("x", width / 2)
//       .attr("y", 40)
//       .attr("fill", "#000")
//       .attr("text-anchor", "middle")
//       .attr("font-size", "14px")
//       .text("F2 (Hz)");

//     g.append("g")
//       .call(yAxis)
//       .call((g) => g.selectAll(".tick line").attr("stroke", "#ccc"))
//       .call((g) => g.select(".domain").remove())
//       .append("text")
//       .attr("transform", "rotate(-90)")
//       .attr("x", -height / 2)
//       .attr("y", -40)
//       .attr("fill", "#000")
//       .attr("text-anchor", "middle")
//       .attr("font-size", "14px")
//       .text("F1 (Hz)");

//     // --- Paleta de cores dinâmica ---
//     const labels = Array.from(new Set(data.map((d) => d.label)));
//     const color = d3.scaleOrdinal(labels, d3.schemeCategory10);

//     // --- Tooltip (flutuante e removido no cleanup) ---
//     const tooltip = d3
//       .select("body")
//       .append("div")
//       .style("position", "absolute")
//       .style("background", "#fff")
//       .style("border", "1px solid #ccc")
//       .style("padding", "8px")
//       .style("border-radius", "6px")
//       .style("pointer-events", "none")
//       .style("font-size", "14px")
//       .style("opacity", 0);

//     // --- Pontos ---
//     g.selectAll(".dot")
//       .data(data)
//       .join("circle")
//       .attr("class", "dot")
//       .attr("cx", (d) => x(d.F2))
//       .attr("cy", (d) => y(d.F1))
//       .attr("r", 5)
//       .attr("fill", (d) => color(d.label || "default"))
//       .on("mouseover", (event, d) => {
//         tooltip.transition().duration(150).style("opacity", 1);
//         tooltip
//           .html(
//             `<strong>${d.id}</strong><br/>F1: ${d.F1} Hz<br/>F2: ${d.F2} Hz<br/>Data: ${
//               d.label || "-"
//             }`
//           )
//           .style("left", `${event.pageX + 10}px`)
//           .style("top", `${event.pageY - 30}px`);
//       })
//       .on("mouseout", () =>
//         tooltip.transition().duration(150).style("opacity", 0)
//       );

//     // --- Etiquetas (pequenas acima dos pontos) ---
//     g.selectAll(".label")
//       .data(data)
//       .join("text")
//       .attr("class", "label")
//       .attr("x", (d) => x(d.F2))
//       .attr("y", (d) => y(d.F1) - 10)
//       .attr("text-anchor", "middle")
//       .attr("font-size", "12px")
//       .attr("fill", "#333")
//       .text((d) => d.id);

//     // --- Legenda automática ---
//     const legend = svg
//       .append("g")
//       .attr("transform", `translate(${margin.left},${height + margin.top + 50})`);

//     labels.forEach((label, i) => {
//       const legendRow = legend
//         .append("g")
//         .attr("transform", `translate(${i * 140}, 0)`);

//       legendRow
//         .append("rect")
//         .attr("width", 14)
//         .attr("height", 14)
//         .attr("fill", color(label));

//       legendRow
//         .append("text")
//         .attr("x", 20)
//         .attr("y", 12)
//         .attr("font-size", "13px")
//         .attr("fill", "#000")
//         .text(label);
//     });

//     // --- Cleanup ---
//     return () => {
//       tooltip.remove();
//     };
//   }, [data]);

//   return <svg ref={svgRef} className="mx-auto block" />;
// };

export function AcousticSpaceD3V2({ data }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || data.length === 0) return;

    // --- Configuração básica ---
    const margin = { top: 20, right: 30, bottom: 60, left: 50 };
    const width = 900 - margin.left - margin.right;
    const height = 700 - margin.top - margin.bottom;

    const svg = d3
      .select(svgRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom);

    svg.selectAll("*").remove(); // limpar conteúdo

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // --- Escalas iniciais ---
    const x = d3
      .scaleLinear()
      .domain(d3.extent(data, (d) => d.F2))
      .nice()
      .range([width, 0]);

    const y = d3
      .scaleLinear()
      .domain(d3.extent(data, (d) => d.F1))
      .nice()
      .range([0, height]);

    // --- Fundo / Moldura ---
    g.append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", width)
      .attr("height", height)
      .attr("fill", "none")
      .attr("stroke", "#333")
      .attr("stroke-width", 1.5);

    // --- Eixos com grid ---
    const xAxis = g
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).tickSize(-height).tickPadding(8));

    const yAxis = g.append("g").call(d3.axisLeft(y).tickSize(-width).tickPadding(8));

    xAxis.selectAll(".tick line").attr("stroke", "#ccc");
    yAxis.selectAll(".tick line").attr("stroke", "#ccc");
    xAxis.select(".domain").remove();
    yAxis.select(".domain").remove();

    xAxis
      .append("text")
      .attr("x", width / 2)
      .attr("y", 40)
      .attr("fill", "#000")
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .text("F2 (Hz)");

    yAxis
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", -40)
      .attr("fill", "#000")
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .text("F1 (Hz)");

    // --- Paleta de cores dinâmica ---
    const labels = Array.from(new Set(data.map((d) => d.label)));
    const color = d3.scaleOrdinal(labels, d3.schemeCategory10);

    // --- Tooltip ---
    const tooltip = d3
      .select("body")
      .append("div")
      .style("position", "absolute")
      .style("background", "#fff")
      .style("border", "1px solid #ccc")
      .style("padding", "8px")
      .style("border-radius", "6px")
      .style("pointer-events", "none")
      .style("font-size", "14px")
      .style("opacity", 0);

    // --- Pontos + Labels ---
    const pointsGroup = g.append("g").attr("class", "points-group");

    pointsGroup
      .selectAll("circle")
      .data(data)
      .join("circle")
      .attr("cx", (d) => x(d.F2))
      .attr("cy", (d) => y(d.F1))
      .attr("r", 5)
      .attr("fill", (d) => color(d.label || "default"))
      .on("mouseover", (event, d) => {
        tooltip.transition().duration(150).style("opacity", 1);
        tooltip
          .html(
            `<strong>${d.id.replace(/_/g, " ")}</strong><br/>F1: ${d.F1} Hz<br/>F2: ${d.F2} Hz<br/>Data: ${
              d.label || "-"
            }`
          )
          .style("left", `${event.pageX + 10}px`)
          .style("top", `${event.pageY - 30}px`);
      })
      .on("mouseout", () =>
        tooltip.transition().duration(150).style("opacity", 0)
      );

    pointsGroup
      .selectAll("text")
      .data(data)
      .join("text")
      .attr("x", (d) => x(d.F2))
      .attr("y", (d) => y(d.F1) - 10)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("fill", "#333")
      .text((d) => d.id.replace(/_/g, " "));

    // --- Legenda ---
    const legend = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${height + margin.top + 45})`);

    labels.forEach((label, i) => {
      const legendRow = legend
        .append("g")
        .attr("transform", `translate(${i * 140}, 0)`);

      legendRow.append("rect").attr("width", 14).attr("height", 14).attr("fill", color(label));

      legendRow
        .append("text")
        .attr("x", 20)
        .attr("y", 12)
        .attr("font-size", "13px")
        .attr("fill", "#000")
        .text(label);
    });

    // --- Zoom + Pan ---
    const zoom = d3.zoom()
      .scaleExtent([0.5, 5]) // limites de zoom
      .translateExtent([[0, 0], [width, height]]) // evita pan infinito
      .on("zoom", (event) => {
        const transform = event.transform;
        const zx = transform.rescaleX(x);
        const zy = transform.rescaleY(y);

        xAxis.call(d3.axisBottom(zx).tickSize(-height).tickPadding(8));
        yAxis.call(d3.axisLeft(zy).tickSize(-width).tickPadding(8));

        pointsGroup
          .selectAll("circle")
          .attr("cx", (d) => zx(d.F2))
          .attr("cy", (d) => zy(d.F1));

        pointsGroup
          .selectAll("text")
          .attr("x", (d) => zx(d.F2))
          .attr("y", (d) => zy(d.F1) - 10);
      });

    svg.call(zoom);

    // --- Cleanup ---
    return () => {
      tooltip.remove();
    };
  }, [data]);

  return <svg ref={svgRef} className="mx-auto block" />;
};


// export function Boxplot({ data, width = 400, height = 300 }) {
//   const svgRef = useRef();

//   useEffect(() => {
//     if (!data || data.length === 0) return;

//     // Clear previous content
//     d3.select(svgRef.current).selectAll("*").remove();

//     const margin = { top: 20, right: 30, bottom: 30, left: 40 };
//     const innerWidth = width - margin.left - margin.right;
//     const innerHeight = height - margin.top - margin.bottom;

//     const svg = d3
//       .select(svgRef.current)
//       .attr("width", width)
//       .attr("height", height)
//       .append("g")
//       .attr("transform", `translate(${margin.left},${margin.top})`);

//     // Boxplot stats
//     const sorted = data.slice().sort(d3.ascending);
//     const q1 = d3.quantile(sorted, 0.25);
//     const median = d3.quantile(sorted, 0.5);
//     const q3 = d3.quantile(sorted, 0.75);
//     const min = d3.min(sorted);
//     const max = d3.max(sorted);

//     // Scales
//     const xScale = d3.scaleBand().domain(["F0"]).range([0, innerWidth]).padding(0.5);
//     const yScale = d3.scaleLinear().domain([min, max]).nice().range([innerHeight, 0]);

//     // Y axis with grid lines
//     svg.append("g")
//       .call(d3.axisLeft(yScale)
//         .tickSize(-innerWidth) // Extend ticks across the width
//         .tickFormat(d => d))   // Keep default formatting
//       .call(g => g.selectAll(".tick line").attr("stroke", "#ccc")) // Light gray grid lines
//       .call(g => g.select(".domain").remove()); // Remove axis line

//     // Box
//     svg.append("rect")
//       .attr("x", xScale("F0"))
//       .attr("y", yScale(q3))
//       .attr("height", yScale(q1) - yScale(q3))
//       .attr("width", xScale.bandwidth())
//       .attr("stroke", "black")
//       .attr("fill", "#69b3a2");

//     // Median line
//     svg.append("line")
//       .attr("x1", xScale("F0"))
//       .attr("x2", xScale("F0") + xScale.bandwidth())
//       .attr("y1", yScale(median))
//       .attr("y2", yScale(median))
//       .attr("stroke", "black");

//     // Whiskers
//     svg.append("line")
//       .attr("x1", xScale("F0") + xScale.bandwidth() / 2)
//       .attr("x2", xScale("F0") + xScale.bandwidth() / 2)
//       .attr("y1", yScale(min))
//       .attr("y2", yScale(q1))
//       .attr("stroke", "black");

//     svg.append("line")
//       .attr("x1", xScale("F0") + xScale.bandwidth() / 2)
//       .attr("x2", xScale("F0") + xScale.bandwidth() / 2)
//       .attr("y1", yScale(q3))
//       .attr("y2", yScale(max))
//       .attr("stroke", "black");

//     // Whisker caps
//     svg.append("line")
//       .attr("x1", xScale("F0") + xScale.bandwidth() / 4)
//       .attr("x2", xScale("F0") + (3 * xScale.bandwidth()) / 4)
//       .attr("y1", yScale(min))
//       .attr("y2", yScale(min))
//       .attr("stroke", "black");

//     svg.append("line")
//       .attr("x1", xScale("F0") + xScale.bandwidth() / 4)
//       .attr("x2", xScale("F0") + (3 * xScale.bandwidth()) / 4)
//       .attr("y1", yScale(max))
//       .attr("y2", yScale(max))
//       .attr("stroke", "black");

//   }, [data, width, height]);

//   return <svg ref={svgRef}></svg>;
// }

// export function Boxplot({ data, width = 500, height = 300 }) {
//   const svgRef = useRef();
//   console.log("Boxplot data:", data);

//   useEffect(() => {
//     if (!data || data.length === 0) return;

//     d3.select(svgRef.current).selectAll("*").remove();

//     const margin = { top: 20, right: 30, bottom: 30, left: 40 };
//     const innerWidth = width - margin.left - margin.right;
//     const innerHeight = height - margin.top - margin.bottom;

//     const svg = d3
//       .select(svgRef.current)
//       .attr("width", width)
//       .attr("height", height);

//     const plotArea = svg
//       .append("g")
//       .attr("transform", `translate(${margin.left},${margin.top})`);

//     // 🔹 Normalize: if `data` is an array, turn it into { id: values }
//     let dataMap = {};
//     if (Array.isArray(data)) {
//       data.forEach(d => {
//         if (d.id && d.F0) {
//           dataMap[d.id] = d.F0; // adjust if you want a different feature than F0
//         }
//       });
//     } else {
//       dataMap = data; // already in object format
//     }

//     const categories = Object.keys(dataMap);
//     const allValues = categories.flatMap(key => dataMap[key]);
//     const min = d3.min(allValues);
//     const max = d3.max(allValues);

//     const xScale = d3.scaleBand()
//       .domain(categories)
//       .range([0, innerWidth])
//       .padding(0.4);

//     const yScale = d3.scaleLinear()
//       .domain([min, max])
//       .nice()
//       .range([innerHeight, 0]);

//     const colorScale = d3.scaleOrdinal()
//       .domain(categories)
//       .range(d3.schemeCategory10);

//     // Grid lines
//     plotArea.append("g")
//       .call(d3.axisLeft(yScale)
//         .tickSize(-innerWidth)
//         .tickFormat(""))
//       .call(g => g.selectAll(".tick line").attr("stroke", "#e0e0e0"))
//       .call(g => g.select(".domain").remove());

//     // Y Axis
//     plotArea.append("g").call(d3.axisLeft(yScale));

//     // X Axis
//     plotArea.append("g")
//       .attr("transform", `translate(0,${innerHeight})`)
//       .call(d3.axisBottom(xScale));

//     const boxWidth = 30;

//     // Tooltip div
//     const tooltip = d3.select("body")
//       .append("div")
//       .style("position", "absolute")
//       .style("padding", "6px 10px")
//       .style("background", "white")
//       .style("border", "1px solid #ccc")
//       .style("border-radius", "4px")
//       .style("pointer-events", "none")
//       .style("font-size", "12px")
//       .style("visibility", "hidden");

//     categories.forEach(key => {
//       const values = dataMap[key].slice().sort(d3.ascending);
//       const q1 = d3.quantile(values, 0.25);
//       const median = d3.quantile(values, 0.5);
//       const q3 = d3.quantile(values, 0.75);
//       const localMin = d3.min(values);
//       const localMax = d3.max(values);
//       const center = xScale(key) + xScale.bandwidth() / 2;
//       const color = colorScale(key);

//       // Box
//       plotArea.append("rect")
//         .attr("x", center - boxWidth / 2)
//         .attr("y", yScale(q3))
//         .attr("height", yScale(q1) - yScale(q3))
//         .attr("width", boxWidth)
//         .attr("stroke", "black")
//         .attr("fill", color)
//         .on("mouseover", () => {
//           tooltip.style("visibility", "visible")
//             .html(`
//               <strong>${key}</strong><br/>
//               Min: ${localMin}<br/>
//               Q1: ${q1}<br/>
//               Median: ${median}<br/>
//               Q3: ${q3}<br/>
//               Max: ${localMax}
//             `);
//         })
//         .on("mousemove", (event) => {
//           tooltip.style("top", `${event.pageY - 10}px`)
//                  .style("left", `${event.pageX + 10}px`);
//         })
//         .on("mouseout", () => {
//           tooltip.style("visibility", "hidden");
//         });

//       // Median line
//       plotArea.append("line")
//         .attr("x1", center - boxWidth / 2)
//         .attr("x2", center + boxWidth / 2)
//         .attr("y1", yScale(median))
//         .attr("y2", yScale(median))
//         .attr("stroke", "black");

//       // Whiskers
//       plotArea.append("line")
//         .attr("x1", center)
//         .attr("x2", center)
//         .attr("y1", yScale(localMin))
//         .attr("y2", yScale(q1))
//         .attr("stroke", "black");

//       plotArea.append("line")
//         .attr("x1", center)
//         .attr("x2", center)
//         .attr("y1", yScale(q3))
//         .attr("y2", yScale(localMax))
//         .attr("stroke", "black");

//       // Whisker caps
//       plotArea.append("line")
//         .attr("x1", center - boxWidth / 4)
//         .attr("x2", center + boxWidth / 4)
//         .attr("y1", yScale(localMin))
//         .attr("y2", yScale(localMin))
//         .attr("stroke", "black");

//       plotArea.append("line")
//         .attr("x1", center - boxWidth / 4)
//         .attr("x2", center + boxWidth / 4)
//         .attr("y1", yScale(localMax))
//         .attr("y2", yScale(localMax))
//         .attr("stroke", "black");
//     });

//   }, [data, width, height]);

//   return <svg ref={svgRef}></svg>;
// }


export function Boxplot({ data, width = 900, height = 500 }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || data.length === 0) return;

    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height);
    svg.selectAll("*").remove();

    const margin = { top: 30, right: 30, bottom: 80, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // 🔹 Normaliza os dados
    let dataMap = {};
    if (Array.isArray(data)) {
      data.forEach((d) => {
        if (d.id && d.F0) dataMap[d.id] = d.F0;
      });
    } else {
      dataMap = data;
    }

    const categories = Object.keys(dataMap);
    const allValues = categories.flatMap((key) => dataMap[key]);
    const min = d3.min(allValues);
    const max = d3.max(allValues);

    const xScale = d3
      .scaleBand()
      .domain(categories)
      .range([0, innerWidth])
      .padding(0.4);

    const yScale = d3
      .scaleLinear()
      .domain([min, max])
      .nice()
      .range([innerHeight, 0]);

    const colorScale = d3
      .scaleOrdinal()
      .domain(categories)
      .range(d3.schemeCategory10);

    // Grid + Eixos
    const yAxisGrid = d3.axisLeft(yScale).tickSize(-innerWidth).tickFormat("");
    g.append("g")
      .attr("class", "grid")
      .call(yAxisGrid)
      .call((g) => g.selectAll(".tick line").attr("stroke", "#e0e0e0"))
      .call((g) => g.select(".domain").remove());

    const xAxis = g
      .append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale));

    const yAxis = g.append("g").call(d3.axisLeft(yScale));

    xAxis
      .append("text")
      .attr("x", innerWidth / 2)
      .attr("y", 45)
      .attr("fill", "black")
      .attr("text-anchor", "middle")
      .text("Passos");

    yAxis
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerHeight / 2)
      .attr("y", -40)
      .attr("fill", "black")
      .attr("text-anchor", "middle")
      .text("Valores");

    const boxWidth = Math.min(30, xScale.bandwidth() * 0.6);

    // Tooltip
    const tooltip = d3
      .select("body")
      .append("div")
      .attr("class", "boxplot-tooltip")
      .style("position", "absolute")
      .style("background", "#fff")
      .style("border", "1px solid #ccc")
      .style("border-radius", "6px")
      .style("padding", "8px")
      .style("font-size", "14px")
      .style("pointer-events", "none")
      .style("opacity", 0);

    const plotGroup = g.append("g").attr("class", "boxplot-group");

    categories.forEach((key) => {
      const values = dataMap[key].slice().sort(d3.ascending);
      const q1 = d3.quantile(values, 0.25);
      const median = d3.quantile(values, 0.5);
      const q3 = d3.quantile(values, 0.75);
      const localMin = d3.min(values);
      const localMax = d3.max(values);
      const center = xScale(key) + xScale.bandwidth() / 2;
      const color = colorScale(key);

      plotGroup
        .append("rect")
        .attr("x", center - boxWidth / 2)
        .attr("y", yScale(q3))
        .attr("width", boxWidth)
        .attr("height", yScale(q1) - yScale(q3))
        .attr("fill", color)
        .attr("stroke", "black")
        .attr("opacity", 0.8)
        .on("mouseover", (event) => {
          tooltip.transition().duration(150).style("opacity", 1);
          tooltip
            .html(
              `<strong>${key.replace(/_/g, " ")}</strong><br/>
              Min: ${localMin}<br/>
              Q1: ${q1}<br/>
              Median: ${median}<br/>
              Q3: ${q3}<br/>
              Max: ${localMax}`
            )
            .style("left", `${event.pageX + 10}px`)
            .style("top", `${event.pageY - 30}px`);
        })
        .on("mousemove", (event) => {
          tooltip
            .style("left", `${event.pageX + 10}px`)
            .style("top", `${event.pageY - 30}px`);
        })
        .on("mouseout", () =>
          tooltip.transition().duration(150).style("opacity", 0)
        );

      // Linha da mediana
      plotGroup
        .append("line")
        .attr("x1", center - boxWidth / 2)
        .attr("x2", center + boxWidth / 2)
        .attr("y1", yScale(median))
        .attr("y2", yScale(median))
        .attr("stroke", "black")
        .attr("stroke-width", 2);

      // Whiskers
      plotGroup
        .append("line")
        .attr("x1", center)
        .attr("x2", center)
        .attr("y1", yScale(localMin))
        .attr("y2", yScale(localMax))
        .attr("stroke", "black");

      // Caps
      [localMin, localMax].forEach((val) => {
        plotGroup
          .append("line")
          .attr("x1", center - boxWidth / 4)
          .attr("x2", center + boxWidth / 4)
          .attr("y1", yScale(val))
          .attr("y2", yScale(val))
          .attr("stroke", "black");
      });
    });

    // ✅ Legenda dinâmica abaixo do gráfico
    const legend = svg
      .append("g")
      .attr(
        "transform",
        `translate(${margin.left},${height - margin.bottom + 25})`
      );

    categories.forEach((key, i) => {
      const legendGroup = legend
        .append("g")
        .attr("transform", `translate(${i * 120}, 0)`);

      legendGroup
        .append("rect")
        .attr("width", 14)
        .attr("height", 14)
        .attr("fill", colorScale(key));

      legendGroup
        .append("text")
        .attr("x", 20)
        .attr("y", 12)
        .attr("fill", "#000")
        .style("font-size", "14px")
        .text(key);
    });

    return () => tooltip.remove();
  }, [data, width, height]);

  return <svg ref={svgRef} className="mx-auto block" />;
}



// F0 ao longo do tempo

// export function F0Chart ({ data, f0, startTimeMs = 0, timeStepMs = 5, maWindowMs = 200 }) {
//   const svgRef = useRef();

//   useEffect(() => {
//     if ((!data || data.length === 0) && (!f0 || f0.length === 0)) return;

//     // Se o usuário passou `data` no formato [{ id, F0: [...] }]
//     // usamos a primeira entrada (ou todas se no futuro quiser comparar várias).
//     const f0Array = f0 || (Array.isArray(data) ? data[0].F0 : []);
//     if (!f0Array || f0Array.length === 0) return;

//     const width = 800;
//     const height = 400;
//     const margin = { top: 40, right: 30, bottom: 50, left: 60 };

//     // Limpar SVG antes de redesenhar
//     d3.select(svgRef.current).selectAll("*").remove();

//     const svg = d3
//       .select(svgRef.current)
//       .attr("viewBox", `0 0 ${width} ${height}`)
//       .style("width", "100%")
//       .style("height", "auto");

//     // Criar dataset com tempo em segundos
//     const dataPoints = f0Array.map((val, i) => ({
//       time: (startTimeMs + i * timeStepMs) / 1000,
//       f0: val > 0 ? val : NaN, // tratamos não-vozeado como NaN
//     }));

//     const x = d3
//       .scaleLinear()
//       .domain(d3.extent(dataPoints, (d) => d.time))
//       .nice()
//       .range([margin.left, width - margin.right]);

//     const y = d3
//       .scaleLinear()
//       .domain([0, d3.max(dataPoints, (d) => d.f0) || 200])
//       .nice()
//       .range([height - margin.bottom, margin.top]);

//     // Eixos
//     const xAxis = (g) =>
//       g
//         .attr("transform", `translate(0,${height - margin.bottom})`)
//         .call(d3.axisBottom(x))
//         .call((g) => g.append("text")
//           .attr("x", width / 2)
//           .attr("y", 40)
//           .attr("fill", "currentColor")
//           .attr("text-anchor", "middle")
//           .text("Tempo (s)")
//         );

//     const yAxis = (g) =>
//       g
//         .attr("transform", `translate(${margin.left},0)`)
//         .call(d3.axisLeft(y))
//         .call((g) => g.append("text")
//           .attr("x", -margin.left + 10)
//           .attr("y", margin.top - 20)
//           .attr("fill", "currentColor")
//           .attr("text-anchor", "start")
//           .attr("font-weight", "bold")
//           .text("f0 (Hz)")
//         );

//     svg.append("g").call(xAxis);
//     svg.append("g").call(yAxis);

//     // Linha principal
//     const line = d3
//       .line()
//       .defined((d) => !isNaN(d.f0))
//       .x((d) => x(d.time))
//       .y((d) => y(d.f0));

//     svg
//       .append("path")
//       .datum(dataPoints)
//       .attr("fill", "none")
//       .attr("stroke", "#2563eb")
//       .attr("stroke-width", 2)
//       .attr("d", line);

//     // Média móvel
//     const windowSize = Math.max(1, Math.round(maWindowMs / timeStepMs));
//     const movingAverage = dataPoints.map((d, i) => {
//       const start = Math.max(0, i - Math.floor(windowSize / 2));
//       const end = Math.min(dataPoints.length, i + Math.floor(windowSize / 2));
//       const slice = dataPoints.slice(start, end).filter((p) => !isNaN(p.f0));
//       const mean = slice.length > 0 ? d3.mean(slice, (p) => p.f0) : NaN;
//       return { time: d.time, f0: mean };
//     });

//     const maLine = d3
//       .line()
//       .defined((d) => !isNaN(d.f0))
//       .x((d) => x(d.time))
//       .y((d) => y(d.f0));

//     svg
//       .append("path")
//       .datum(movingAverage)
//       .attr("fill", "none")
//       .attr("stroke", "orange")
//       .attr("stroke-width", 1.5)
//       .attr("stroke-dasharray", "4 2")
//       .attr("d", maLine);

//     // Tooltip
//     const tooltip = d3
//       .select("body")
//       .append("div")
//       .style("position", "absolute")
//       .style("background", "rgba(0,0,0,0.7)")
//       .style("color", "white")
//       .style("padding", "4px 8px")
//       .style("border-radius", "4px")
//       .style("font-size", "12px")
//       .style("pointer-events", "none")
//       .style("opacity", 0);

//     const focus = svg
//       .append("circle")
//       .attr("r", 4)
//       .attr("fill", "red")
//       .style("opacity", 0);

//     svg
//       .append("rect")
//       .attr("fill", "transparent")
//       .attr("pointer-events", "all")
//       .attr("x", margin.left)
//       .attr("y", margin.top)
//       .attr("width", width - margin.left - margin.right)
//       .attr("height", height - margin.top - margin.bottom)
//       .on("mousemove", function (event) {
//         const [mx] = d3.pointer(event);
//         const time = x.invert(mx);
//         const i = d3.bisector((d) => d.time).left(dataPoints, time);
//         const d = dataPoints[i];
//         if (!d || isNaN(d.f0)) {
//           tooltip.style("opacity", 0);
//           focus.style("opacity", 0);
//           return;
//         }
//         focus
//           .attr("cx", x(d.time))
//           .attr("cy", y(d.f0))
//           .style("opacity", 1);
//         tooltip
//           .style("opacity", 1)
//           .html(`<b>${d.time.toFixed(2)} s</b><br/>f₀: ${d.f0.toFixed(2)} Hz`)
//           .style("left", `${event.pageX + 10}px`)
//           .style("top", `${event.pageY - 20}px`);
//       })
//       .on("mouseleave", () => {
//         tooltip.style("opacity", 0);
//         focus.style("opacity", 0);
//       });

//     return () => tooltip.remove();
//   }, [data, f0, startTimeMs, timeStepMs, maWindowMs]);

//   return <svg ref={svgRef}></svg>;
// };


export function F0Chart({
  data,
  f0,
  startTimeMs = 0,
  timeStepMs = 5,
  maWindowMs = 200,
  width = 900,
  height = 450,
}) {
  const svgRef = useRef();

  useEffect(() => {
    if ((!data || data.length === 0) && (!f0 || f0.length === 0)) return;

    const f0Array = f0 || (Array.isArray(data) ? data[0].F0 : []);
    if (!f0Array || f0Array.length === 0) return;

    const margin = { top: 50, right: 40, bottom: 60, left: 70 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Limpar antes de redesenhar
    const svg = d3
      .select(svgRef.current)
      .attr("viewBox", `0 0 ${width} ${height}`)
      .style("width", "100%")
      .style("height", "auto")
      .style("background", "var(--chart-bg, #fafafa)")
      .style("border-radius", "12px")
      .style("box-shadow", "0 4px 12px rgba(0,0,0,0.1)");
    svg.selectAll("*").remove();

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Dataset
    const dataPoints = f0Array.map((val, i) => ({
      time: (startTimeMs + i * timeStepMs) / 1000,
      f0: val > 0 ? val : NaN,
    }));

    const x = d3
      .scaleLinear()
      .domain(d3.extent(dataPoints, (d) => d.time))
      .nice()
      .range([0, innerWidth]);

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(dataPoints, (d) => d.f0) || 200])
      .nice()
      .range([innerHeight, 0]);

    // Eixos com grid
    const xAxis = d3.axisBottom(x).ticks(10);
    const yAxis = d3.axisLeft(y).ticks(8);

    g.append("g")
      .attr("class", "grid grid-x")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(xAxis)
      .call((g) =>
        g
          .append("text")
          .attr("x", innerWidth / 2)
          .attr("y", 45)
          .attr("fill", "currentColor")
          .attr("text-anchor", "middle")
          .attr("font-weight", "bold")
          .text("Tempo (s)")
      );

    g.append("g")
      .call(yAxis)
      .call((g) =>
        g
          .append("text")
          .attr("x", -50)
          .attr("y", -15)
          .attr("fill", "currentColor")
          .attr("text-anchor", "start")
          .attr("font-weight", "bold")
          .text("F₀ (Hz)")
      );

    g.append("g")
      .attr("class", "grid-lines")
      .call(
        d3.axisLeft(y).tickSize(-innerWidth).tickFormat("")
      )
      .call((g) => g.selectAll(".tick line").attr("stroke", "#e0e0e0"));

    // Linhas
    const mainLine = d3
      .line()
      .defined((d) => !isNaN(d.f0))
      .x((d) => x(d.time))
      .y((d) => y(d.f0));

    const windowSize = Math.max(1, Math.round(maWindowMs / timeStepMs));
    const movingAverage = dataPoints.map((d, i) => {
      const start = Math.max(0, i - Math.floor(windowSize / 2));
      const end = Math.min(dataPoints.length, i + Math.floor(windowSize / 2));
      const slice = dataPoints.slice(start, end).filter((p) => !isNaN(p.f0));
      const mean = slice.length > 0 ? d3.mean(slice, (p) => p.f0) : NaN;
      return { time: d.time, f0: mean };
    });

    const maLine = d3
      .line()
      .defined((d) => !isNaN(d.f0))
      .x((d) => x(d.time))
      .y((d) => y(d.f0));

    // Desenha linha principal com animação
    g.append("path")
      .datum(dataPoints)
      .attr("fill", "none")
      .attr("stroke", "#2563eb")
      .attr("stroke-width", 2)
      .attr("stroke-linejoin", "round")
      .attr("stroke-linecap", "round")
      .attr("d", mainLine)
      .attr("stroke-dasharray", function () {
        const length = this.getTotalLength();
        return `${length} ${length}`;
      })
      .attr("stroke-dashoffset", function () {
        return this.getTotalLength();
      })
      .transition()
      .duration(1500)
      .ease(d3.easeCubicOut)
      .attr("stroke-dashoffset", 0);

    // Linha média móvel
    g.append("path")
      .datum(movingAverage)
      .attr("fill", "none")
      .attr("stroke", "orange")
      .attr("stroke-width", 1.8)
      .attr("stroke-dasharray", "6 3")
      .attr("d", maLine);

    // Tooltip + Focus
    const tooltip = d3
      .select("body")
      .append("div")
      .style("position", "absolute")
      .style("background", "rgba(0,0,0,0.75)")
      .style("color", "#fff")
      .style("padding", "6px 10px")
      .style("border-radius", "8px")
      .style("font-size", "13px")
      .style("pointer-events", "none")
      .style("opacity", 0);

    const focus = g
      .append("circle")
      .attr("r", 5)
      .attr("fill", "red")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .style("opacity", 0);

    g.append("rect")
      .attr("fill", "transparent")
      .attr("pointer-events", "all")
      .attr("width", innerWidth)
      .attr("height", innerHeight)
      .on("mousemove", function (event) {
        const [mx] = d3.pointer(event);
        const time = x.invert(mx);
        const i = d3.bisector((d) => d.time).left(dataPoints, time);
        const d = dataPoints[i];
        if (!d || isNaN(d.f0)) {
          tooltip.style("opacity", 0);
          focus.style("opacity", 0);
          return;
        }
        focus
          .attr("cx", x(d.time))
          .attr("cy", y(d.f0))
          .style("opacity", 1);
        tooltip
          .style("opacity", 1)
          .html(
            `<b>${d.time.toFixed(2)} s</b><br/>f₀: ${d.f0.toFixed(2)} Hz`
          )
          .style("left", `${event.pageX + 10}px`)
          .style("top", `${event.pageY - 20}px`);
      })
      .on("mouseleave", () => {
        tooltip.style("opacity", 0);
        focus.style("opacity", 0);
      });

    // Legenda
    const legend = g.append("g").attr(
      "transform",
      `translate(${innerWidth - 180}, -30)`
    );

    const items = [
      { color: "#2563eb", text: "F₀" },
      { color: "orange", text: "Média Móvel" },
    ];

    legend
      .selectAll("g")
      .data(items)
      .join("g")
      .attr("transform", (d, i) => `translate(${i * 100}, 0)`)
      .each(function (d) {
        const group = d3.select(this);
        group
          .append("rect")
          .attr("width", 16)
          .attr("height", 4)
          .attr("y", -8)
          .attr("rx", 2)
          .attr("fill", d.color);
        group
          .append("text")
          .attr("x", 20)
          .attr("y", -2)
          .attr("fill", "currentColor")
          .style("font-size", "14px")
          .text(d.text);
      });

    return () => tooltip.remove();
  }, [data, f0, startTimeMs, timeStepMs, maWindowMs, width, height]);

  return <svg ref={svgRef}></svg>;
}





// export function Boxplot({ data, width = 500, height = 300 }) {
//   const svgRef = useRef();
//   console.log("BoxF0: ", data)
//   useEffect(() => {
//     if (!data || Object.keys(data).length === 0) return;

//     d3.select(svgRef.current).selectAll("*").remove();

//     const margin = { top: 20, right: 30, bottom: 30, left: 40 };
//     const innerWidth = width - margin.left - margin.right;
//     const innerHeight = height - margin.top - margin.bottom;

//     const svg = d3
//       .select(svgRef.current)
//       .attr("width", width)
//       .attr("height", height);

//     const plotArea = svg
//       .append("g")
//       .attr("transform", `translate(${margin.left},${margin.top})`);

//     const categories = Object.keys(data);
//     const allValues = categories.flatMap(key => data[key]);
//     const min = d3.min(allValues);
//     const max = d3.max(allValues);

//     const xScale = d3.scaleBand()
//       .domain(categories)
//       .range([0, innerWidth])
//       .padding(0.4);

//     const yScale = d3.scaleLinear()
//       .domain([min, max])
//       .nice()
//       .range([innerHeight, 0]);

//     const colorScale = d3.scaleOrdinal()
//       .domain(categories)
//       .range(d3.schemeCategory10); // 10 distinct colors

//     // Grid lines
//     plotArea.append("g")
//       .call(d3.axisLeft(yScale)
//         .tickSize(-innerWidth)
//         .tickFormat(""))
//       .call(g => g.selectAll(".tick line").attr("stroke", "#e0e0e0"))
//       .call(g => g.select(".domain").remove());

//     // Y Axis
//     plotArea.append("g").call(d3.axisLeft(yScale));

//     // X Axis
//     plotArea.append("g")
//       .attr("transform", `translate(0,${innerHeight})`)
//       .call(d3.axisBottom(xScale));

//     const boxWidth = 30;

//     // Tooltip div
//     const tooltip = d3.select("body")
//       .append("div")
//       .style("position", "absolute")
//       .style("padding", "6px 10px")
//       .style("background", "white")
//       .style("border", "1px solid #ccc")
//       .style("border-radius", "4px")
//       .style("pointer-events", "none")
//       .style("font-size", "12px")
//       .style("visibility", "hidden");
    
//     categories.forEach(key => {
//       const values = data[key].slice().sort(d3.ascending);
//       const q1 = d3.quantile(values, 0.25);
//       const median = d3.quantile(values, 0.5);
//       const q3 = d3.quantile(values, 0.75);
//       const localMin = d3.min(values);
//       const localMax = d3.max(values);
//       const center = xScale(key) + xScale.bandwidth() / 2;
//       const color = colorScale(key);

//       // Box
//       plotArea.append("rect")
//         .attr("x", center - boxWidth / 2)
//         .attr("y", yScale(q3))
//         .attr("height", yScale(q1) - yScale(q3))
//         .attr("width", boxWidth)
//         .attr("stroke", "black")
//         .attr("fill", color)
//         .on("mouseover", () => {
//           tooltip.style("visibility", "visible")
//             .html(`
//               <strong>${key}</strong><br/>
//               Min: ${localMin}<br/>
//               Q1: ${q1}<br/>
//               Median: ${median}<br/>
//               Q3: ${q3}<br/>
//               Max: ${localMax}
//             `);
//         })
//         .on("mousemove", (event) => {
//           tooltip.style("top", `${event.pageY - 10}px`)
//                  .style("left", `${event.pageX + 10}px`);
//         })
//         .on("mouseout", () => {
//           tooltip.style("visibility", "hidden");
//         });

//       // Median line
//       plotArea.append("line")
//         .attr("x1", center - boxWidth / 2)
//         .attr("x2", center + boxWidth / 2)
//         .attr("y1", yScale(median))
//         .attr("y2", yScale(median))
//         .attr("stroke", "black");

//       // Whiskers
//       plotArea.append("line")
//         .attr("x1", center)
//         .attr("x2", center)
//         .attr("y1", yScale(localMin))
//         .attr("y2", yScale(q1))
//         .attr("stroke", "black");

//       plotArea.append("line")
//         .attr("x1", center)
//         .attr("x2", center)
//         .attr("y1", yScale(q3))
//         .attr("y2", yScale(localMax))
//         .attr("stroke", "black");

//       // Whisker caps
//       plotArea.append("line")
//         .attr("x1", center - boxWidth / 4)
//         .attr("x2", center + boxWidth / 4)
//         .attr("y1", yScale(localMin))
//         .attr("y2", yScale(localMin))
//         .attr("stroke", "black");

//       plotArea.append("line")
//         .attr("x1", center - boxWidth / 4)
//         .attr("x2", center + boxWidth / 4)
//         .attr("y1", yScale(localMax))
//         .attr("y2", yScale(localMax))
//         .attr("stroke", "black");
//     });

//   }, [data, width, height]);

//   return <svg ref={svgRef}></svg>;
// }



// export function PauseBoxplot({ data, parameterName, width = 500, height = 300 }) {
//   const svgRef = useRef();
//   console.log("BoxParam: ", data, parameterName)

//   useEffect(() => {
//     if (!data || !Array.isArray(data) || data.length === 0) return;

//     d3.select(svgRef.current).selectAll("*").remove();

//     const margin = { top: 40, right: 30, bottom: 50, left: 60 };
//     const innerWidth = width - margin.left - margin.right;
//     const innerHeight = height - margin.top - margin.bottom;

//     const svg = d3
//       .select(svgRef.current)
//       .attr("width", width)
//       .attr("height", height);

//     const plotArea = svg
//       .append("g")
//       .attr("transform", `translate(${margin.left},${margin.top})`);

//     // Ordenar os valores para calcular quartis
//     const values = data.slice().sort(d3.ascending);
//     const q1 = d3.quantile(values, 0.25);
//     const median = d3.quantile(values, 0.5);
//     const q3 = d3.quantile(values, 0.75);
//     const localMin = d3.min(values);
//     const localMax = d3.max(values);

//     const yScale = d3.scaleLinear()
//       .domain([localMin, localMax])
//       .nice()
//       .range([innerHeight, 0]);

//     // Como só há uma categoria, centramos o boxplot
//     const center = innerWidth / 2;
//     const boxWidth = 40;

//     // Grid
//     plotArea.append("g")
//       .call(d3.axisLeft(yScale).tickSize(-innerWidth).tickFormat(""))
//       .call(g => g.selectAll(".tick line").attr("stroke", "#e0e0e0"))
//       .call(g => g.select(".domain").remove());

//     // Eixo Y
//     plotArea.append("g").call(d3.axisLeft(yScale));

//     // Label eixo Y
//     plotArea.append("text")
//       .attr("transform", "rotate(-90)")
//       .attr("x", -innerHeight / 2)
//       .attr("y", -45)
//       .attr("text-anchor", "middle")
//       .style("fill", "#333")
//       .style("font-size", "14px")
//       .text(
//         parameterName === "pauseDurations" ? "Duração (s)" :
//         parameterName === "Jitter" ? "Jitter (%)" :
//         parameterName === "Shimmer" ? "Shimmer (%)" : "Valor"
//       );

//     // Eixo X (só uma categoria)
//     plotArea.append("g")
//       .attr("transform", `translate(0,${innerHeight})`)
//       .call(d3.axisBottom(d3.scaleBand().domain([parameterName]).range([center - boxWidth, center + boxWidth])))
//       .selectAll("text")
//       .style("text-anchor", "middle");

//     // Título
//     svg.append("text")
//       .attr("x", width / 2)
//       .attr("y", 20)
//       .attr("text-anchor", "middle")
//       .style("fill", "#111")
//       .style("font-size", "16px")
//       .style("font-weight", "bold")
//       .text(
//         parameterName === "pause"
//           ? "Distribuição das Durações de Pausa"
//           : parameterName === "Jitter"
//           ? "Distribuição do Jitter"
//           : parameterName === "Shimmer"
//           ? "Distribuição do Shimmer"
//           : "Distribuição"
//       );

//     // Tooltip
//     const tooltip = d3.select("body")
//       .append("div")
//       .style("position", "absolute")
//       .style("padding", "6px 10px")
//       .style("background", "#fff")
//       .style("border", "1px solid #ccc")
//       .style("border-radius", "6px")
//       .style("box-shadow", "0 2px 8px rgba(0,0,0,0.2)")
//       .style("pointer-events", "none")
//       .style("font-size", "12px")
//       .style("visibility", "hidden");

//     // Caixa
//     plotArea.append("rect")
//       .attr("x", center - boxWidth / 2)
//       .attr("y", yScale(q3))
//       .attr("height", yScale(q1) - yScale(q3))
//       .attr("width", boxWidth)
//       .attr("stroke", "black")
//       .attr("fill", "#69b3a2")
//       .on("mouseover", () => {
//         tooltip.style("visibility", "visible")
//           .html(`
//             <strong>${parameterName}</strong><br/>
//             Min: ${localMin.toFixed(3)}<br/>
//             Q1: ${q1.toFixed(3)}<br/>
//             Mediana: ${median.toFixed(3)}<br/>
//             Q3: ${q3.toFixed(3)}<br/>
//             Max: ${localMax.toFixed(3)}
//           `);
//       })
//       .on("mousemove", (event) => {
//         tooltip
//           .style("top", `${event.pageY - 40}px`)
//           .style("left", `${event.pageX + 20}px`);
//       })
//       .on("mouseout", () => tooltip.style("visibility", "hidden"));

//     // Mediana
//     plotArea.append("line")
//       .attr("x1", center - boxWidth / 2)
//       .attr("x2", center + boxWidth / 2)
//       .attr("y1", yScale(median))
//       .attr("y2", yScale(median))
//       .attr("stroke", "black");

//     // Whiskers
//     plotArea.append("line")
//       .attr("x1", center)
//       .attr("x2", center)
//       .attr("y1", yScale(localMin))
//       .attr("y2", yScale(q1))
//       .attr("stroke", "black");

//     plotArea.append("line")
//       .attr("x1", center)
//       .attr("x2", center)
//       .attr("y1", yScale(q3))
//       .attr("y2", yScale(localMax))
//       .attr("stroke", "black");

//     // Caps
//     plotArea.append("line")
//       .attr("x1", center - boxWidth / 4)
//       .attr("x2", center + boxWidth / 4)
//       .attr("y1", yScale(localMin))
//       .attr("y2", yScale(localMin))
//       .attr("stroke", "black");

//     plotArea.append("line")
//       .attr("x1", center - boxWidth / 4)
//       .attr("x2", center + boxWidth / 4)
//       .attr("y1", yScale(localMax))
//       .attr("y2", yScale(localMax))
//       .attr("stroke", "black");

//     return () => tooltip.remove();
//   }, [data, width, height, parameterName]);

//   return <svg ref={svgRef}></svg>;
// }


/**
 * PauseBoxplot
 * Renderiza um boxplot para um único parâmetro (p.ex. pauseDurations, Jitter, Shimmer).
 *
 * Props:
 *  - data: array numérico (ex: [0.12, 0.3, 0.05, ...]) OR array de objetos (valores serão extraídos)
 *  - parameterName: string usada para rótulos/legenda
 *  - width, height: tamanhos base (component é responsivo via viewBox)
 */
export function PauseBoxplot({
  data,
  parameterName = "pauseDurations",
  width = 640,
  height = 360,
}) {
  const svgRef = useRef();

  useEffect(() => {
    // validações iniciais
    if (!data) return;
    // suportar input em duas formas: lista direta de números, ou lista de objetos com valor
    let values = Array.isArray(data)
      ? data.map((d) => (typeof d === "number" ? d : d.value ?? d[parameterName] ?? NaN))
      : [];

    values = values.filter((v) => typeof v === "number" && !isNaN(v));
    if (values.length === 0) {
      // limpar svg e sair (manter markup acessível)
      d3.select(svgRef.current).selectAll("*").remove();
      const svg = d3.select(svgRef.current).attr("viewBox", `0 0 ${width} ${height}`);
      svg.append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "currentColor")
        .text("Sem dados suficientes");
      return;
    }

    // limpa e cria svg responsivo
    const margin = { top: 48, right: 28, bottom: 56, left: 72 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3
      .select(svgRef.current)
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .style("width", "100%")
      .style("height", "auto")
      .style("font-family", "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial");

    svg.selectAll("*").remove();

    // container
    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    // estatísticas
    values = values.slice().sort(d3.ascending);
    const q1 = d3.quantile(values, 0.25);
    const median = d3.quantile(values, 0.5);
    const q3 = d3.quantile(values, 0.75);
    const iqr = q3 - q1;
    const min = d3.min(values);
    const max = d3.max(values);

    // whisker tradicional (1.5 * IQR) — clamped ao min/max reais
    const whiskerLow = d3.max([min, q1 - 1.5 * iqr]);
    const whiskerHigh = d3.min([max, q3 + 1.5 * iqr]);

    // escala y
    const padding = (whiskerHigh - whiskerLow) * 0.08 || 1; // proteção caso variação 0
    const y = d3
      .scaleLinear()
      .domain([whiskerLow - padding, whiskerHigh + padding])
      .nice()
      .range([innerHeight, 0]);

    // centros (apenas 1 categoria)
    const center = innerWidth / 2;
    const boxWidth = Math.min(120, innerWidth * 0.18);

    // grade horizontal
    g.append("g")
      .attr("class", "grid")
      .call(d3.axisLeft(y).tickSize(-innerWidth).tickFormat(""))
      .call((g) => g.selectAll(".tick line").attr("stroke", "#e6e6e6"))
      .call((g) => g.select(".domain").remove());

    // eixo Y
    g.append("g")
      .attr("class", "y-axis")
      .call(d3.axisLeft(y).ticks(6))
      .selectAll("text")
      .attr("fill", "currentColor");

    // eixo X (categoria única) — estilizado leve
    const xBand = d3.scaleBand().domain([parameterName]).range([center - boxWidth, center + boxWidth]);
    g.append("g")
      .attr("transform", `translate(0, ${innerHeight + 8})`)
      .call(d3.axisBottom(xBand).tickSize(0))
      .selectAll("text")
      .style("font-weight", 600)
      .attr("fill", "currentColor");

    // título
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", margin.top / 2)
      .attr("text-anchor", "middle")
      .attr("fill", "currentColor")
      .style("font-size", "16px")
      .style("font-weight", 700)
      .text(
        parameterName === "pauseDurations"
          ? "Distribuição — Durações de Pausa"
          : parameterName === "Jitter"
          ? "Distribuição — Jitter"
          : parameterName === "Shimmer"
          ? "Distribuição — Shimmer"
          : `Distribuição — ${parameterName}`
      );

    // legenda do eixo Y
    svg
      .append("text")
      .attr("x", 14)
      .attr("y", margin.top + (innerHeight / 2))
      .attr("transform", `rotate(-90, 14, ${margin.top + innerHeight / 2})`)
      .attr("text-anchor", "middle")
      .attr("fill", "currentColor")
      .style("font-size", "12px")
      .text(
        parameterName === "pauseDurations"
          ? "Duração (s)"
          : parameterName === "Jitter"
          ? "Jitter (%)"
          : parameterName === "Shimmer"
          ? "Shimmer (%)"
          : "Valor"
      );

    // tooltip
    const tooltip = d3
      .select("body")
      .append("div")
      .attr("role", "tooltip")
      .style("position", "absolute")
      .style("pointer-events", "none")
      .style("background", "rgba(0,0,0,0.75)")
      .style("color", "white")
      .style("padding", "8px 10px")
      .style("border-radius", "6px")
      .style("font-size", "13px")
      .style("box-shadow", "0 6px 18px rgba(0,0,0,0.12)")
      .style("opacity", 0);

    // group para boxplot
    const boxGroup = g.append("g").attr("class", "boxplot-group");

    // whiskers (linha vertical)
    boxGroup
      .append("line")
      .attr("x1", center)
      .attr("x2", center)
      .attr("y1", y(whiskerLow))
      .attr("y2", y(whiskerHigh))
      .attr("stroke", "#333")
      .attr("stroke-width", 1.2)
      .attr("opacity", 0)
      .transition()
      .duration(600)
      .attr("opacity", 1);

    // caixa
    boxGroup
      .append("rect")
      .attr("x", center - boxWidth / 2)
      .attr("width", boxWidth)
      .attr("y", y(q3))
      .attr("height", Math.max(1, y(q1) - y(q3)))
      .attr("rx", 6)
      .attr("fill", "#4f46e5") // cor acessível (azul-violeta)
      .attr("fill-opacity", 0.14)
      .attr("stroke", "#4f46e5")
      .attr("stroke-width", 1.25)
      .on("mouseenter", (event) =>
        tooltip
          .style("opacity", 1)
          .html(
            `<strong>${parameterName}</strong><br/>
             Min: ${min.toFixed(3)}<br/>
             Q1: ${q1.toFixed(3)}<br/>
             Mediana: ${median.toFixed(3)}<br/>
             Q3: ${q3.toFixed(3)}<br/>
             Max: ${max.toFixed(3)}`
          )
      )
      .on("mousemove", (event) => {
        tooltip.style("left", `${event.pageX + 12}px`).style("top", `${event.pageY - 28}px`);
      })
      .on("mouseleave", () => tooltip.style("opacity", 0));

    // median line
    boxGroup
      .append("line")
      .attr("x1", center - boxWidth / 2)
      .attr("x2", center + boxWidth / 2)
      .attr("y1", y(median))
      .attr("y2", y(median))
      .attr("stroke", "#111827")
      .attr("stroke-width", 1.5)
      .attr("opacity", 0)
      .transition()
      .duration(500)
      .attr("opacity", 1);

    // whisker caps
    boxGroup
      .append("line")
      .attr("x1", center - boxWidth / 4)
      .attr("x2", center + boxWidth / 4)
      .attr("y1", y(whiskerLow))
      .attr("y2", y(whiskerLow))
      .attr("stroke", "#333")
      .attr("stroke-width", 1.1);

    boxGroup
      .append("line")
      .attr("x1", center - boxWidth / 4)
      .attr("x2", center + boxWidth / 4)
      .attr("y1", y(whiskerHigh))
      .attr("y2", y(whiskerHigh))
      .attr("stroke", "#333")
      .attr("stroke-width", 1.1);

    // outliers (pontos fora dos whiskers)
    const outliers = values.filter((v) => v < whiskerLow || v > whiskerHigh);
    boxGroup
      .selectAll(".outlier")
      .data(outliers)
      .join("circle")
      .attr("class", "outlier")
      .attr("cx", center)
      .attr("cy", (d) => y(d))
      .attr("r", 4)
      .attr("fill", "#ef4444")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1)
      .on("mouseenter", (event, d) =>
        tooltip
          .style("opacity", 1)
          .html(`<strong>Outlier</strong><br/>Valor: ${d.toFixed(3)}`)
      )
      .on("mousemove", (event) => {
        tooltip.style("left", `${event.pageX + 12}px`).style("top", `${event.pageY - 28}px`);
      })
      .on("mouseleave", () => tooltip.style("opacity", 0))
      .attr("opacity", 0)
      .transition()
      .duration(600)
      .attr("opacity", 1);

    // densidade suave (opcional) — ajuda visual para ver concentração
    try {
      const kde = kernelDensityEstimator(epanechnikovKernel( (y.domain()[1]-y.domain()[0]) / 40 ), y.ticks(40));
      const density = kde(values);

      const xDensity = d3
        .scaleLinear()
        .domain([0, d3.max(density, (d) => d[1])])
        .range([center + boxWidth / 2 + 8, center + boxWidth / 2 + Math.min(80, innerWidth * 0.15)]); // lateral direita

      const area = d3
        .area()
        .x0(center + boxWidth / 2 + 8)
        .x1((d) => xDensity(d[1]))
        .y((d) => y(d[0]))
        .curve(d3.curveBasis);

      boxGroup
        .append("path")
        .datum(density)
        .attr("d", area)
        .attr("fill", "#4f46e5")
        .attr("fill-opacity", 0.08)
        .attr("stroke", "none")
        .attr("transform", "translate(0,0)");
    } catch (err) {
      // se densidade falhar, não quebra componente
      // console.warn("Density failed", err);
    }

    // Cleanup
    return () => {
      tooltip.remove();
      d3.select(svgRef.current).selectAll("*").remove();
    };

    // small helpers (kernel density)
    function kernelDensityEstimator(kernel, X) {
      return function (V) {
        return X.map(function (x) {
          return [x, d3.mean(V, function (v) { return kernel(x - v); })];
        });
      };
    }
    function epanechnikovKernel(bandwidth) {
      return function (u) {
        u = u / bandwidth;
        return Math.abs(u) <= 1 ? 0.75 * (1 - u * u) / bandwidth : 0;
      };
    }
  }, [data, parameterName, width, height]);

  return (
    <figure aria-labelledby="boxplot-title" style={{ width: "100%" }}>
      <svg ref={svgRef} role="img" aria-label={`Boxplot ${parameterName}`} />
    </figure>
  );
}




export function ParameterBoxplot({ data, parameterName, width = 550, height = 350 }) {
  const svgRef = useRef();

  if (parameterName === "pausedurations") {
    // Configurações específicas para "pausedurations"
    width = 800;
    height = 500;
  }

  useEffect(() => {
    if (!data || Object.keys(data).length === 0) return;

    d3.select(svgRef.current).selectAll("*").remove();

    const margin = { top: 50, right: 30, bottom: 50, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    const plotArea = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // 🔑 Normaliza dados
    let normalized = {};
    if (Array.isArray(data)) {
      data.forEach(item => {
        const [key, values] = Object.entries(item)[0];
        const label = item.id || key;
        normalized[label] = Array.isArray(values) ? values : [values];
      });
    } else {
      Object.entries(data).forEach(([key, values]) => {
        normalized[key] = Array.isArray(values) ? values : [values];
      });
    }

    const categories = Object.keys(normalized);
    const allValues = categories.flatMap(key => normalized[key]);
    const min = d3.min(allValues);
    const max = d3.max(allValues);

    const xScale = d3.scaleBand()
      .domain(categories)
      .range([0, innerWidth])
      .padding(0.4);

    const yScale = d3.scaleLinear()
      .domain([min, max])
      .nice()
      .range([innerHeight, 0]);

    const colorScale = d3.scaleOrdinal()
      .domain(categories)
      .range(d3.schemeCategory10);

    // Grid lines
    plotArea.append("g")
      .call(d3.axisLeft(yScale).tickSize(-innerWidth).tickFormat(""))
      .call(g => g.selectAll(".tick line").attr("stroke", "#e0e0e0"))
      .call(g => g.select(".domain").remove());

    // Eixo Y
    plotArea.append("g").call(d3.axisLeft(yScale));

    // Label do eixo Y
    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .style("fill", "#333")
      .style("font-size", "14px")
      .text(
        parameterName === "pausedurations" ? "Duração (s)" :
        parameterName === "Jitter" ? "Jitter (%)" :
        parameterName === "Shimmer" ? "Shimmer (%)" : "Valor"
      );

    // Eixo X
    plotArea.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale));

    // Label do eixo X
    svg.append("text")
      .attr("x", margin.left + innerWidth / 2)
      .attr("y", height - 10)
      .attr("text-anchor", "middle")
      .style("fill", "#333")
      .style("font-size", "14px")
      .text(
        parameterName === "pausedurations" ? "Pausas" :
        parameterName === "Jitter" ? "Jitter" :
        parameterName === "Shimmer" ? "Shimmer" : "Parâmetro"
      );

    // Título do gráfico
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", 25)
      .attr("text-anchor", "middle")
      .style("fill", "#111")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text(
        parameterName === "pausedurations"
          ? "Distribuição das Durações de Pausa"
          : parameterName === "Jitter"
          ? "Distribuição do Jitter"
          : parameterName === "Shimmer"
          ? "Distribuição do Shimmer"
          : "Distribuição"
      );

    const tooltip = d3.select("body")
      .append("div")
      .style("position", "absolute")
      .style("padding", "6px 10px")
      .style("background", "white")
      .style("border", "1px solid #ccc")
      .style("border-radius", "4px")
      .style("pointer-events", "none")
      .style("font-size", "12px")
      .style("visibility", "hidden");

    // Boxplot
    const boxWidth = 30;
    categories.forEach(key => {
      const values = normalized[key].slice().sort(d3.ascending);
      const q1 = d3.quantile(values, 0.25);
      const median = d3.quantile(values, 0.5);
      const q3 = d3.quantile(values, 0.75);
      const localMin = d3.min(values);
      const localMax = d3.max(values);
      const center = xScale(key) + xScale.bandwidth() / 2;
      const color = colorScale(key);

      // Caixa
      plotArea.append("rect")
        .attr("x", center - boxWidth / 2)
        .attr("y", yScale(q3))
        .attr("height", yScale(q1) - yScale(q3))
        .attr("width", boxWidth)
        .attr("stroke", "black")
        .attr("fill", color)
        .on("mouseover", () => {
          tooltip.style("visibility", "visible")
            .html(`
              <strong>${key.replace(/_/g, " ")}</strong><br/>
              Min: ${localMin}<br/>
              Q1: ${q1}<br/>
              Median: ${median}<br/>
              Q3: ${q3}<br/>
              Max: ${localMax}
            `);
        })
        .on("mousemove", (event) => {
          tooltip.style("top", `${event.pageY - 10}px`)
                 .style("left", `${event.pageX + 10}px`);
        })
        .on("mouseout", () => tooltip.style("visibility", "hidden"));

      // Linha da mediana
      plotArea.append("line")
        .attr("x1", center - boxWidth / 2)
        .attr("x2", center + boxWidth / 2)
        .attr("y1", yScale(median))
        .attr("y2", yScale(median))
        .attr("stroke", "black");

      // Whiskers
      plotArea.append("line")
        .attr("x1", center)
        .attr("x2", center)
        .attr("y1", yScale(localMin))
        .attr("y2", yScale(q1))
        .attr("stroke", "black");

      plotArea.append("line")
        .attr("x1", center)
        .attr("x2", center)
        .attr("y1", yScale(q3))
        .attr("y2", yScale(localMax))
        .attr("stroke", "black");

      // Whisker caps
      plotArea.append("line")
        .attr("x1", center - boxWidth / 4)
        .attr("x2", center + boxWidth / 4)
        .attr("y1", yScale(localMin))
        .attr("y2", yScale(localMin))
        .attr("stroke", "black");

      plotArea.append("line")
        .attr("x1", center - boxWidth / 4)
        .attr("x2", center + boxWidth / 4)
        .attr("y1", yScale(localMax))
        .attr("y2", yScale(localMax))
        .attr("stroke", "black");
    });

  }, [data, parameterName, width, height]);

  return <svg ref={svgRef}></svg>;
}
/** * ParameterBoxplot
 * Renderiza um boxplot para múltiplas categorias de um parâmetro (p.ex. diferentes pausas).
 * Props:
 *  - data: objeto com arrays numéricos (ex: { pause1: [0.1, 0.2], pause2: [0.3, 0.4] }) OR array de objetos (valores serão extraídos)
 *  - parameterName: string usada para rótulos/legenda
 *  - width, height: tamanhos base (component é responsivo via viewBox)
 */

export function ParameterBoxplot1({ data, parameterName, width = 550, height = 350 }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || Object.keys(data).length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 50, right: 30, bottom: 50, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const plotArea = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // 🔑 Normaliza dados
    const normalized = Array.isArray(data)
      ? data.reduce((acc, item) => {
          const [key, values] = Object.entries(item)[0];
          const label = item.id || key;
          acc[label] = Array.isArray(values) ? values : [values];
          return acc;
        }, {})
      : Object.fromEntries(
          Object.entries(data).map(([k, v]) => [k, Array.isArray(v) ? v : [v]])
        );

    const categories = Object.keys(normalized);
    const allValues = categories.flatMap((key) => normalized[key]);
    const min = d3.min(allValues);
    const max = d3.max(allValues);

    const xScale = d3.scaleBand().domain(categories).range([0, innerWidth]).padding(0.4);
    const yScale = d3.scaleLinear().domain([min, max]).nice().range([innerHeight, 0]);
    const colorScale = d3.scaleOrdinal().domain(categories).range(d3.schemeTableau10);

    // Grade
    plotArea
      .append("g")
      .call(d3.axisLeft(yScale).tickSize(-innerWidth).tickFormat(""))
      .call((g) => g.selectAll(".tick line").attr("stroke", "#e5e7eb"))
      .call((g) => g.select(".domain").remove());

    // Eixos
    plotArea.append("g").call(d3.axisLeft(yScale));
    plotArea
      .append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale));

    // Labels
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .style("fill", "#333")
      .style("font-size", "14px")
      .text(
        parameterName === "pausedurations"
          ? "Duração (s)"
          : parameterName === "Jitter"
          ? "Jitter (%)"
          : parameterName === "Shimmer"
          ? "Shimmer (%)"
          : "Valor"
      );

    svg
      .append("text")
      .attr("x", margin.left + innerWidth / 2)
      .attr("y", height - 10)
      .attr("text-anchor", "middle")
      .style("fill", "#333")
      .style("font-size", "14px")
      .text(
        parameterName === "pausedurations"
          ? "Pausas"
          : parameterName === "Jitter"
          ? "Jitter"
          : parameterName === "Shimmer"
          ? "Shimmer"
          : "Parâmetro"
      );

    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", 25)
      .attr("text-anchor", "middle")
      .style("fill", "#111")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text(
        parameterName === "pausedurations"
          ? "Distribuição das Durações de Pausa"
          : parameterName === "Jitter"
          ? "Distribuição do Jitter"
          : parameterName === "Shimmer"
          ? "Distribuição do Shimmer"
          : "Distribuição"
      );

    // Tooltip
    const tooltip = d3
      .select(svgRef.current.parentNode)
      .append("div")
      .style("position", "absolute")
      .style("padding", "8px 10px")
      .style("background", "white")
      .style("border", "1px solid #ccc")
      .style("border-radius", "6px")
      .style("box-shadow", "0 2px 6px rgba(0,0,0,0.15)")
      .style("font-size", "13px")
      .style("pointer-events", "none")
      .style("visibility", "hidden");

    // Boxplots
    const boxWidth = xScale.bandwidth() * 0.6;
    categories.forEach((key) => {
      const values = normalized[key].slice().sort(d3.ascending);
      const q1 = d3.quantile(values, 0.25);
      const median = d3.quantile(values, 0.5);
      const q3 = d3.quantile(values, 0.75);
      const localMin = d3.min(values);
      const localMax = d3.max(values);
      const center = xScale(key) + xScale.bandwidth() / 2;
      const color = colorScale(key);

      // Caixa com transição
      plotArea
        .append("rect")
        .attr("x", center - boxWidth / 2)
        .attr("width", boxWidth)
        .attr("y", yScale(q3))
        .attr("height", 0)
        .attr("stroke", "#111")
        .attr("fill", color)
        .transition()
        .duration(600)
        .attr("height", yScale(q1) - yScale(q3));

      // Linha mediana
      plotArea
        .append("line")
        .attr("x1", center - boxWidth / 2)
        .attr("x2", center + boxWidth / 2)
        .attr("y1", yScale(median))
        .attr("y2", yScale(median))
        .attr("stroke", "#111");

      // Whiskers + caps
      plotArea.append("line").attr("x1", center).attr("x2", center).attr("y1", yScale(localMin)).attr("y2", yScale(q1)).attr("stroke", "#111");
      plotArea.append("line").attr("x1", center).attr("x2", center).attr("y1", yScale(q3)).attr("y2", yScale(localMax)).attr("stroke", "#111");

      plotArea.append("line").attr("x1", center - boxWidth / 4).attr("x2", center + boxWidth / 4).attr("y1", yScale(localMin)).attr("y2", yScale(localMin)).attr("stroke", "#111");
      plotArea.append("line").attr("x1", center - boxWidth / 4).attr("x2", center + boxWidth / 4).attr("y1", yScale(localMax)).attr("y2", yScale(localMax)).attr("stroke", "#111");

      // Hover interativo
      plotArea
        .append("rect")
        .attr("x", center - boxWidth / 2)
        .attr("width", boxWidth)
        .attr("y", yScale(localMax))
        .attr("height", yScale(localMin) - yScale(localMax))
        .attr("fill", "transparent")
        .on("mouseover", () => {
          tooltip
            .style("visibility", "visible")
            .html(
              `<strong>${key}</strong><br/>Min: ${localMin}<br/>Q1: ${q1}<br/>Mediana: ${median}<br/>Q3: ${q3}<br/>Max: ${localMax}`
            );
        })
        .on("mousemove", (event) => {
          tooltip.style("top", `${event.offsetY + 10}px`).style("left", `${event.offsetX + 20}px`);
        })
        .on("mouseout", () => tooltip.style("visibility", "hidden"));
    });
  }, [data, parameterName, width, height]);

  return <svg ref={svgRef}></svg>;
}



export function PauseBoxplot1({ data, width = 400, height = 300 }) {
  const svgRef = useRef();

  // console.log("PauseBox: ",data)

  useEffect(() => {
    if (!data || data.length === 0) return;

    d3.select(svgRef.current).selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 30, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const sorted = data.slice().sort(d3.ascending);
    const q1 = d3.quantile(sorted, 0.25);
    const median = d3.quantile(sorted, 0.5);
    const q3 = d3.quantile(sorted, 0.75);
    const min = d3.min(sorted);
    const max = d3.max(sorted);

    const yScale = d3.scaleLinear().domain([min, max]).nice().range([innerHeight, 0]);
    const xScale = d3.scaleBand().domain(["Pause"]).range([0, innerWidth]).padding(0.5);

    // Grid
    svg.append("g")
      .call(d3.axisLeft(yScale).tickSize(-innerWidth).tickFormat(""))
      .call(g => g.selectAll(".tick line").attr("stroke", "#e0e0e0"))
      .call(g => g.select(".domain").remove());

    // Y Axis
    svg.append("g").call(d3.axisLeft(yScale));

    // Box
    svg.append("rect")
      .attr("x", xScale("Pause"))
      .attr("y", yScale(q3))
      .attr("height", yScale(q1) - yScale(q3))
      .attr("width", xScale.bandwidth())
      .attr("stroke", "black")
      .attr("fill", "#69b3a2");

    // Median line
    svg.append("line")
      .attr("x1", xScale("Pause"))
      .attr("x2", xScale("Pause") + xScale.bandwidth())
      .attr("y1", yScale(median))
      .attr("y2", yScale(median))
      .attr("stroke", "black");

    // Whiskers
    svg.append("line")
      .attr("x1", xScale("Pause") + xScale.bandwidth() / 2)
      .attr("x2", xScale("Pause") + xScale.bandwidth() / 2)
      .attr("y1", yScale(min))
      .attr("y2", yScale(q1))
      .attr("stroke", "black");

    svg.append("line")
      .attr("x1", xScale("Pause") + xScale.bandwidth() / 2)
      .attr("x2", xScale("Pause") + xScale.bandwidth() / 2)
      .attr("y1", yScale(q3))
      .attr("y2", yScale(max))
      .attr("stroke", "black");

    // Whisker caps
    svg.append("line")
      .attr("x1", xScale("Pause") + xScale.bandwidth() / 4)
      .attr("x2", xScale("Pause") + (3 * xScale.bandwidth()) / 4)
      .attr("y1", yScale(min))
      .attr("y2", yScale(min))
      .attr("stroke", "black");

    svg.append("line")
      .attr("x1", xScale("Pause") + xScale.bandwidth() / 4)
      .attr("x2", xScale("Pause") + (3 * xScale.bandwidth()) / 4)
      .attr("y1", yScale(max))
      .attr("y2", yScale(max))
      .attr("stroke", "black");

  }, [data, width, height]);

  return <svg ref={svgRef}></svg>;
}


// export function IntensityChart({ data, width = 800, height = 300 }) {
//   const svgRef = useRef();
//   const [tooltip, setTooltip] = useState(null);
//   const [hoverData, setHoverData] = useState(null);

//   if (!data || data.length === 0) return null;

//   useEffect(() => {
//     const svg = d3.select(svgRef.current);
//     svg.selectAll("*").remove();

//     const margin = { top: 20, right: 30, bottom: 30, left: 40 };

//     svg.attr("width", width).attr("height", height);

//     const x = d3
//       .scaleLinear()
//       .domain(d3.extent(data, (d) => d.time))
//       .range([margin.left, width - margin.right]);

//     const y = d3
//       .scaleLinear()
//       .domain([d3.min(data, (d) => d.db) - 5, d3.max(data, (d) => d.db) + 5])
//       .range([height - margin.bottom, margin.top]);

//     const line = d3
//       .line()
//       .x((d) => x(d.time))
//       .y((d) => y(d.db));

//     const zoom = d3.zoom().scaleExtent([1, 10]).on("zoom", (event) => {
//       const transform = event.transform;
//       const newX = transform.rescaleX(x);
//       const newLine = d3
//         .line()
//         .x((d) => newX(d.time))
//         .y((d) => y(d.db));

//       svg.selectAll("path").attr("d", newLine(data));
//       svg.select(".x-axis").call(d3.axisBottom(newX));
//     });

//     svg.call(zoom);

//     svg
//       .append("path")
//       .datum(data)
//       .attr("fill", "none")
//       .attr("stroke", "orange")
//       .attr("stroke-width", 2)
//       .attr("d", line);

//     svg
//       .append("g")
//       .attr("transform", `translate(0,${height - margin.bottom})`)
//       .attr("class", "x-axis")
//       .call(d3.axisBottom(x));

//     svg
//       .append("g")
//       .attr("transform", `translate(${margin.left},0)`)
//       .call(d3.axisLeft(y));

//     // Hover interativo
//     svg
//       .append("rect")
//       .attr("width", width)
//       .attr("height", height)
//       .attr("fill", "transparent")
//       .on("mousemove", function (event) {
//         const [mx] = d3.pointer(event);
//         const time = x.invert(mx);
//         const pontoMaisProximo = data.reduce((a, b) =>
//           Math.abs(b.time - time) < Math.abs(a.time - time) ? b : a
//         );
//         setHoverData(pontoMaisProximo);
//       })
//       .on("mouseleave", () => setHoverData(null));

//     // Estatísticas
//     const valoresValidos = data.filter((d) => typeof d.db === "number" && !isNaN(d.db));

//     const mediaRaw = d3.mean(valoresValidos, (d) => d.db);
//     const maxRaw = d3.max(valoresValidos, (d) => d.db);
//     const minRaw = d3.min(valoresValidos, (d) => d.db);

//     const media = mediaRaw !== undefined ? mediaRaw.toFixed(2) : "N/A";
//     const max = maxRaw !== undefined ? maxRaw.toFixed(2) : "N/A";
//     const min = minRaw !== undefined ? minRaw.toFixed(2) : "N/A";

//     setTooltip({ media, max, min });
//   }, [data]);

//   return (
//     <div
//       style={{
//         display: "flex",
//         alignItems: "flex-start",
//         gap: "16px",
//       }}
//     >
//       {/* Container do gráfico + hover */}
//       <div style={{ position: "relative" }}>
//         <svg ref={svgRef}></svg>

//         {hoverData && (
//           <div
//             style={{
//               position: "absolute",
//               top: 10,
//               right: 10,
//               background: "#e0f7fa",
//               padding: "8px",
//               border: "1px solid #aaa",
//               borderRadius: "6px",
//               fontSize: "13px",
//             }}
//           >
//             {typeof hoverData.db === "number" && typeof hoverData.time === "number" && (
//               <div>
//                 <strong>🕒 {hoverData.time.toFixed(2)}s</strong>
//                 <br />
//                 Intensidade: {hoverData.db.toFixed(2)} dB
//               </div>
//             )}
//           </div>
//         )}
//       </div>

//       {/* Sidebar fixa à direita */}
//       {tooltip && (
//         <div
//           style={{
//             background: "#fff8dc",
//             padding: "12px",
//             border: "1px solid #ccc",
//             borderRadius: "8px",
//             fontSize: "14px",
//             boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
//             minWidth: "160px",
//             height: 150, // mesma altura do gráfico
//           }}
//         >
//           <strong>📊 Estatísticas:</strong>
//           <br />
//           Média: {tooltip.media} dB
//           <br />
//           Máximo: {tooltip.max} dB
//           <br />
//           Mínimo: {tooltip.min} dB
//         </div>
//       )}
//     </div>
//   );
// }

// export function IntensityChart({ data, width = 800, height = 300 }) {
//   const svgRef = useRef();
//   const [tooltip, setTooltip] = useState(null);
//   const [hoverData, setHoverData] = useState(null);

//   if (!data || data.length === 0) return null;

//   useEffect(() => {
//     const svg = d3.select(svgRef.current);
//     svg.selectAll("*").remove();

//     const margin = { top: 30, right: 30, bottom: 50, left: 60 };

//     svg.attr("width", width).attr("height", height);

//     const x = d3
//       .scaleLinear()
//       .domain(d3.extent(data, (d) => d.time))
//       .range([margin.left, width - margin.right]);

//     const y = d3
//       .scaleLinear()
//       .domain([d3.min(data, (d) => d.db) - 5, d3.max(data, (d) => d.db) + 5])
//       .range([height - margin.bottom, margin.top]);

//     const line = d3
//       .line()
//       .x((d) => x(d.time))
//       .y((d) => y(d.db));

//     const zoom = d3.zoom().scaleExtent([1, 10]).on("zoom", (event) => {
//       const transform = event.transform;
//       const newX = transform.rescaleX(x);
//       const newLine = d3
//         .line()
//         .x((d) => newX(d.time))
//         .y((d) => y(d.db));

//       svg.selectAll("path").attr("d", newLine(data));
//       svg.select(".x-axis").call(d3.axisBottom(newX));
//     });

//     svg.call(zoom);

//     svg
//       .append("path")
//       .datum(data)
//       .attr("fill", "none")
//       .attr("stroke", "orange")
//       .attr("stroke-width", 2)
//       .attr("d", line);

//     // Eixo X
//     svg
//       .append("g")
//       .attr("transform", `translate(0,${height - margin.bottom})`)
//       .attr("class", "x-axis")
//       .call(d3.axisBottom(x));

//     // Rótulo eixo X
//     svg
//       .append("text")
//       .attr("x", width / 2)
//       .attr("y", height - 10)
//       .attr("text-anchor", "middle")
//       .style("fill", "#333")
//       .style("font-size", "14px")
//       .text("Tempo (s)");

//     // Eixo Y
//     svg
//       .append("g")
//       .attr("transform", `translate(${margin.left},0)`)
//       .call(d3.axisLeft(y));

//     // Rótulo eixo Y
//     svg
//       .append("text")
//       .attr("transform", "rotate(-90)")
//       .attr("x", -height / 2)
//       .attr("y", 15)
//       .attr("text-anchor", "middle")
//       .style("fill", "#333")
//       .style("font-size", "14px")
//       .text("Intensidade (dB)");

//     // Título do gráfico
//     svg
//       .append("text")
//       .attr("x", width / 2)
//       .attr("y", margin.top - 10)
//       .attr("text-anchor", "middle")
//       .style("fill", "#111")
//       .style("font-size", "16px")
//       .style("font-weight", "bold")
//       .text("Intensidade da Voz ao Longo do Tempo");

//     // Hover interativo
//     svg
//       .append("rect")
//       .attr("width", width)
//       .attr("height", height)
//       .attr("fill", "transparent")
//       .on("mousemove", function (event) {
//         const [mx] = d3.pointer(event);
//         const time = x.invert(mx);
//         const pontoMaisProximo = data.reduce((a, b) =>
//           Math.abs(b.time - time) < Math.abs(a.time - time) ? b : a
//         );
//         setHoverData(pontoMaisProximo);
//       })
//       .on("mouseleave", () => setHoverData(null));

//     // Estatísticas
//     const valoresValidos = data.filter((d) => typeof d.db === "number" && !isNaN(d.db));

//     const mediaRaw = d3.mean(valoresValidos, (d) => d.db);
//     const maxRaw = d3.max(valoresValidos, (d) => d.db);
//     const minRaw = d3.min(valoresValidos, (d) => d.db);

//     const media = mediaRaw !== undefined ? mediaRaw.toFixed(2) : "N/A";
//     const max = maxRaw !== undefined ? maxRaw.toFixed(2) : "N/A";
//     const min = minRaw !== undefined ? minRaw.toFixed(2) : "N/A";

//     setTooltip({ media, max, min });
//   }, [data]);

//   return (
//     <div style={{ display: "flex", alignItems: "flex-start", gap: "16px" }}>
//       {/* Container do gráfico + hover */}
//       <div style={{ position: "relative" }}>
//         <svg ref={svgRef}></svg>

//         {hoverData && (
//           <div
//             style={{
//               position: "absolute",
//               top: 10,
//               right: 10,
//               background: "#e0f7fa",
//               padding: "8px",
//               border: "1px solid #aaa",
//               borderRadius: "6px",
//               fontSize: "13px",
//             }}
//           >
//             <strong>🕒 {hoverData.time.toFixed(2)}s</strong>
//             <br />
//             Intensidade: {hoverData.db.toFixed(2)} dB
//           </div>
//         )}
//       </div>

//       {/* Sidebar fixa à direita */}
//       {tooltip && (
//         <div
//           style={{
//             background: "#fff8dc",
//             padding: "12px",
//             border: "1px solid #ccc",
//             borderRadius: "8px",
//             fontSize: "14px",
//             boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
//             minWidth: "160px",
//             height: 150,
//           }}
//         >
//           <strong>📊 Estatísticas:</strong>
//           <br />
//           Média: {tooltip.media} dB
//           <br />
//           Máximo: {tooltip.max} dB
//           <br />
//           Mínimo: {tooltip.min} dB
//         </div>
//       )}
//     </div>
//   );
// }


export function IntensityChart({ data, width = 800, height = 300 }) {
  const svgRef = useRef();
  const [hoverData, setHoverData] = useState(null);
  const [stats, setStats] = useState(null);

  if (!data || data.length === 0) return null;

  useEffect(() => {
    const margin = { top: 40, right: 30, bottom: 50, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3
      .select(svgRef.current)
      .attr("viewBox", `0 0 ${width} ${height}`)
      .style("width", "100%")
      .style("height", "auto");

    svg.selectAll("*").remove();

    // Escalas
    const x = d3
      .scaleLinear()
      .domain(d3.extent(data, (d) => d.time))
      .range([margin.left, width - margin.right]);

    const y = d3
      .scaleLinear()
      .domain([d3.min(data, (d) => d.db) - 5, d3.max(data, (d) => d.db) + 5])
      .range([height - margin.bottom, margin.top]);

    // Linha principal
    const line = d3
      .line()
      .x((d) => x(d.time))
      .y((d) => y(d.db));

    const linePath = svg
      .append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "#f59e0b")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Eixos
    const xAxis = svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .attr("class", "x-axis")
      .call(d3.axisBottom(x));

    const yAxis = svg
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y));

    // Rótulos
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", height - 10)
      .attr("text-anchor", "middle")
      .style("fill", "#333")
      .style("font-size", "14px")
      .text("Tempo (s)");

    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", 15)
      .attr("text-anchor", "middle")
      .style("fill", "#333")
      .style("font-size", "14px")
      .text("Intensidade (dB)");

    // Título
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", margin.top - 15)
      .attr("text-anchor", "middle")
      .style("fill", "#111")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text("📈 Intensidade da Voz ao Longo do Tempo");

    // Hover: linha guia + círculo
    const hoverLine = svg
      .append("line")
      .attr("stroke", "#555")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "3 3")
      .style("opacity", 0);

    const hoverCircle = svg
      .append("circle")
      .attr("r", 4)
      .attr("fill", "#ef4444")
      .style("opacity", 0);

    // Área interativa
    svg
      .append("rect")
      .attr("x", margin.left)
      .attr("y", margin.top)
      .attr("width", innerWidth)
      .attr("height", innerHeight)
      .attr("fill", "transparent")
      .on("mousemove", (event) => {
        const [mx] = d3.pointer(event);
        const time = x.invert(mx);
        const closest = data.reduce((a, b) =>
          Math.abs(b.time - time) < Math.abs(a.time - time) ? b : a
        );
        setHoverData(closest);

        hoverLine
          .attr("x1", x(closest.time))
          .attr("x2", x(closest.time))
          .attr("y1", margin.top)
          .attr("y2", height - margin.bottom)
          .style("opacity", 0.5);

        hoverCircle
          .attr("cx", x(closest.time))
          .attr("cy", y(closest.db))
          .style("opacity", 1);
      })
      .on("mouseleave", () => {
        setHoverData(null);
        hoverLine.style("opacity", 0);
        hoverCircle.style("opacity", 0);
      });

    // Zoom & Pan
    const zoom = d3
      .zoom()
      .scaleExtent([1, 10])
      .translateExtent([
        [margin.left, margin.top],
        [width - margin.right, height - margin.bottom],
      ])
      .on("zoom", (event) => {
        const transform = event.transform;
        const newX = transform.rescaleX(x);
        xAxis.call(d3.axisBottom(newX));
        linePath.attr(
          "d",
          d3
            .line()
            .x((d) => newX(d.time))
            .y((d) => y(d.db))(data)
        );
      });

    svg.call(zoom).on("dblclick.zoom", null); // desativar zoom duplo padrão
    svg.on("dblclick", () => svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity));

    // Estatísticas
    const valoresValidos = data.filter(
      (d) => typeof d.db === "number" && !isNaN(d.db)
    );
    setStats({
      media: d3.mean(valoresValidos, (d) => d.db)?.toFixed(2) || "N/A",
      max: d3.max(valoresValidos, (d) => d.db)?.toFixed(2) || "N/A",
      min: d3.min(valoresValidos, (d) => d.db)?.toFixed(2) || "N/A",
    });
  }, [data, width, height]);

  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: "16px" }}>
      {/* Gráfico */}
      <div style={{ flexGrow: 1, position: "relative" }}>
        <svg ref={svgRef}></svg>

        {/* Tooltip flutuante */}
        {hoverData && (
          <div
            style={{
              position: "absolute",
              top: 10,
              right: 10,
              background: "rgba(255,255,255,0.9)",
              padding: "8px",
              border: "1px solid #ddd",
              borderRadius: "6px",
              fontSize: "13px",
              boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
            }}
          >
            <strong>🕒 {hoverData.time.toFixed(2)}s</strong>
            <br />
            Intensidade: <b>{hoverData.db.toFixed(2)} dB</b>
          </div>
        )}
      </div>

      {/* Estatísticas */}
      {stats && (
        <div
          style={{
            background: "#fefce8",
            padding: "12px",
            border: "1px solid #ddd",
            borderRadius: "8px",
            fontSize: "14px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
            minWidth: "170px",
          }}
        >
          <strong>📊 Estatísticas</strong>
          <br /> Média: {stats.media} dB
          <br /> Máximo: {stats.max} dB
          <br /> Mínimo: {stats.min} dB
          <br />
          <small style={{ color: "#666" }}>Duplo clique → Reset zoom</small>
        </div>
      )}
    </div>
  );
}



export function ComparacaoIntensidade  ({ audioA, audioB, nomeA = "Áudio A", nomeB = "Áudio B", width = 800, height = 350 }) {
  const svgRef = useRef();
  const [tooltip, setTooltip] = useState(null);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // const width = 800;
    // const height = 350;
    const margin = { top: 20, right: 30, bottom: 30, left: 40 };

    svg.attr("width", width).attr("height", height);

    const allData = [...audioA, ...audioB];

    const x = d3
      .scaleLinear()
      .domain(d3.extent(allData, (d) => d.time))
      .range([margin.left, width - margin.right]);

    const y = d3
      .scaleLinear()
      .domain([d3.min(allData, (d) => d.db) - 5, d3.max(allData, (d) => d.db) + 5])
      .range([height - margin.bottom, margin.top]);

    const lineA = d3
      .line()
      .x((d) => x(d.time))
      .y((d) => y(d.db));

    const lineB = d3
      .line()
      .x((d) => x(d.time))
      .y((d) => y(d.db));

    svg
      .append("path")
      .datum(audioA)
      .attr("fill", "none")
      .attr("stroke", "#42a5f5")
      .attr("stroke-width", 2)
      .attr("d", lineA);

    svg
      .append("path")
      .datum(audioB)
      .attr("fill", "none")
      .attr("stroke", "#ef5350")
      .attr("stroke-width", 2)
      .attr("d", lineB);

    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x));

    svg
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y));

    // Estatísticas
    const statsA = {
      média: d3.mean(audioA, (d) => d.db).toFixed(2),
      máximo: d3.max(audioA, (d) => d.db).toFixed(2),
      mínimo: d3.min(audioA, (d) => d.db).toFixed(2),
    };

    const statsB = {
      média: d3.mean(audioB, (d) => d.db).toFixed(2),
      máximo: d3.max(audioB, (d) => d.db).toFixed(2),
      mínimo: d3.min(audioB, (d) => d.db).toFixed(2),
    };

    setTooltip({ statsA, statsB });
  }, [audioA, audioB]);

  return (
    <div style={{ position: "relative" }}>
      <svg ref={svgRef}></svg>

      {tooltip && (
        <div
          style={{
            position: "absolute",
            top: 10,
            left: 10,
            background: "#f9fbe7",
            padding: "10px",
            border: "1px solid #ccc",
            borderRadius: "8px",
            fontSize: "14px",
            boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
          }}
        >
          <strong>📊 Estatísticas:</strong><br />
          <span style={{ color: "#42a5f5" }}>{nomeA}</span>: Média {tooltip.statsA.média} dB, Máx {tooltip.statsA.máximo}, Mín {tooltip.statsA.mínimo}<br />
          <span style={{ color: "#ef5350" }}>{nomeB}</span>: Média {tooltip.statsB.média} dB, Máx {tooltip.statsB.máximo}, Mín {tooltip.statsB.mínimo}
        </div>
      )}

      <div
        style={{
          position: "absolute",
          bottom: 10,
          left: 10,
          fontSize: "13px",
          background: "#fff",
          padding: "6px 10px",
          borderRadius: "6px",
          border: "1px solid #ddd",
        }}
      >
        <strong>Legenda:</strong><br />
        <span style={{ color: "#42a5f5" }}>● {nomeA}</span><br />
        <span style={{ color: "#ef5350" }}>● {nomeB}</span>
      </div>
    </div>
  );
};


// export  function HistogramChart({ values, label = "Valor" }) {
//   const svgRef = useRef();

//   useEffect(() => {
//     if (!values || values.length === 0) return;

//     const svg = d3.select(svgRef.current);
//     svg.selectAll("*").remove();

//     const width = 600;
//     const height = 350;
//     const margin = { top: 30, right: 30, bottom: 50, left: 50 };

//     const x = d3
//       .scaleLinear()
//       .domain([0, d3.max(values)])
//       .range([margin.left, width - margin.right]);

//     // ✅ Usando d3.bin() em vez de d3.histogram()
//     const bin = d3.bin()
//       .domain(x.domain())
//       .thresholds(20);

//     const bins = bin(values);

//     const y = d3
//       .scaleLinear()
//       .domain([0, d3.max(bins, (d) => d.length)])
//       .nice()
//       .range([height - margin.bottom, margin.top]);

//     // Tooltip
//     const tooltip = d3
//       .select("body")
//       .append("div")
//       .style("position", "absolute")
//       .style("background", "white")
//       .style("border", "1px solid #ccc")
//       .style("padding", "6px 10px")
//       .style("border-radius", "6px")
//       .style("box-shadow", "0px 2px 6px rgba(0,0,0,0.15)")
//       .style("pointer-events", "none")
//       .style("opacity", 0);

//     svg
//       .selectAll("rect")
//       .data(bins)
//       .enter()
//       .append("rect")
//       .attr("x", (d) => x(d.x0))
//       .attr("y", (d) => y(d.length))
//       .attr("width", (d) => Math.max(0, x(d.x1) - x(d.x0) - 1))
//       .attr("height", (d) => y(0) - y(d.length))
//       .attr("fill", "#3b82f6")
//       .attr("rx", 4)
//       .on("mouseover", function (event, d) {
//         tooltip
//           .style("opacity", 1)
//           .html(
//             `<strong>Intervalo:</strong> ${d.x0.toFixed(2)} - ${d.x1.toFixed(
//               2
//             )}<br/><strong>Frequência:</strong> ${d.length}`
//           );
//         d3.select(this).attr("fill", "#2563eb");
//       })
//       .on("mousemove", function (event) {
//         tooltip
//           .style("left", event.pageX + 10 + "px")
//           .style("top", event.pageY - 20 + "px");
//       })
//       .on("mouseout", function () {
//         tooltip.style("opacity", 0);
//         d3.select(this).attr("fill", "#3b82f6");
//       });

//     svg
//       .append("g")
//       .attr("transform", `translate(0,${height - margin.bottom})`)
//       .call(d3.axisBottom(x));

//     svg
//       .append("g")
//       .attr("transform", `translate(${margin.left},0)`)
//       .call(d3.axisLeft(y));

//     svg
//       .append("text")
//       .attr("x", width / 2)
//       .attr("y", height - 10)
//       .attr("text-anchor", "middle")
//       .attr("fill", "#333")
//       .style("font-size", "14px")
//       .text(`${label} (variabilidade)`);

//     svg
//       .append("text")
//       .attr("transform", "rotate(-90)")
//       .attr("x", -height / 2)
//       .attr("y", 15)
//       .attr("text-anchor", "middle")
//       .attr("fill", "#333")
//       .style("font-size", "14px")
//       .text("Frequência (nº de quadros)");

//     svg
//       .append("text")
//       .attr("x", width / 2)
//       .attr("y", margin.top - 10)
//       .attr("text-anchor", "middle")
//       .attr("fill", "#666")
//       .style("font-size", "12px")
//       .text("Cada valor corresponde a um quadro de 40 ms (deslocamento de 20 ms)");

//     return () => tooltip.remove();
//   }, [values, label]);

//   return <svg ref={svgRef} width={600} height={350}></svg>;
// }



export function HistogramChart({ values, label = "Valor", width = 600, height = 350 }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!values || values.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 40, right: 30, bottom: 60, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Escalas
    const xScale = d3.scaleLinear().domain([0, d3.max(values)]).range([0, innerWidth]);
    const binGenerator = d3.bin().domain(xScale.domain()).thresholds(20);
    const bins = binGenerator(values);
    const yScale = d3.scaleLinear().domain([0, d3.max(bins, (d) => d.length)]).nice().range([innerHeight, 0]);

    const chartArea = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Grid
    chartArea
      .append("g")
      .call(d3.axisLeft(yScale).tickSize(-innerWidth).tickFormat(""))
      .call((g) => g.selectAll(".tick line").attr("stroke", "#e5e7eb"))
      .call((g) => g.select(".domain").remove());

    // Tooltip no body (funciona em qualquer caso)
    const tooltip = d3.select("body")
      .append("div")
      .style("position", "absolute")
      .style("padding", "8px 12px")
      .style("background", "#ffffff")
      .style("border", "1px solid #ccc")
      .style("border-radius", "6px")
      .style("box-shadow", "0 2px 6px rgba(0,0,0,0.15)")
      .style("font-size", "13px")
      .style("pointer-events", "none")
      .style("visibility", "hidden");

    // Barras do histograma
    chartArea
      .selectAll("rect")
      .data(bins)
      .enter()
      .append("rect")
      .attr("x", (d) => xScale(d.x0))
      .attr("y", innerHeight)
      .attr("width", (d) => Math.max(0, xScale(d.x1) - xScale(d.x0) - 1))
      .attr("height", 0)
      .attr("fill", "#3b82f6")
      .attr("rx", 4)
      .on("mouseover", function (event, d) {
        tooltip.style("visibility", "visible")
          .html(
            `<strong>Intervalo:</strong> ${d.x0.toFixed(2)} - ${d.x1.toFixed(2)}<br/>
             <strong>Frequência:</strong> ${d.length}`
          );
        d3.select(this).attr("fill", "#2563eb");
      })
      .on("mousemove", function (event) {
        tooltip.style("top", `${event.pageY - 40}px`).style("left", `${event.pageX + 15}px`);
      })
      .on("mouseout", function () {
        tooltip.style("visibility", "hidden");
        d3.select(this).attr("fill", "#3b82f6");
      })
      .transition()
      .duration(600)
      .attr("y", (d) => yScale(d.length))
      .attr("height", (d) => innerHeight - yScale(d.length));

    // Eixos
    chartArea.append("g").call(d3.axisLeft(yScale));
    chartArea.append("g").attr("transform", `translate(0,${innerHeight})`).call(d3.axisBottom(xScale));

    // Labels
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", height - 10)
      .attr("text-anchor", "middle")
      .style("fill", "#333")
      .style("font-size", "14px")
      .text(`${label} (variabilidade)`);

    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", 15)
      .attr("text-anchor", "middle")
      .style("fill", "#333")
      .style("font-size", "14px")
      .text("Frequência (nº de quadros)");

    svg.append("text")
      .attr("x", width / 2)
      .attr("y", margin.top - 10)
      .attr("text-anchor", "middle")
      .style("fill", "#666")
      .style("font-size", "12px")
      .text("Cada valor corresponde a um quadro de 40 ms (deslocamento de 20 ms)");

    return () => tooltip.remove();
  }, [values, label, width, height]);

  return <svg ref={svgRef}></svg>;
}




// export function HistogramChart({ values, label = "Valor", width = 600, height = 350 }) {
//   const svgRef = useRef();

//   useEffect(() => {
//     if (!values || values.length === 0) return;

//     const svg = d3.select(svgRef.current);
//     svg.selectAll("*").remove();

//     const margin = { top: 40, right: 30, bottom: 60, left: 60 };
//     const innerWidth = width - margin.left - margin.right;
//     const innerHeight = height - margin.top - margin.bottom;

//     // Escalas
//     const xScale = d3.scaleLinear().domain([0, d3.max(values)]).range([0, innerWidth]);
//     const binGenerator = d3.bin().domain(xScale.domain()).thresholds(20);
//     const bins = binGenerator(values);
//     const yScale = d3.scaleLinear().domain([0, d3.max(bins, (d) => d.length)]).nice().range([innerHeight, 0]);

//     const chartArea = svg
//       .attr("width", width)
//       .attr("height", height)
//       .append("g")
//       .attr("transform", `translate(${margin.left},${margin.top})`);

//     // Grid
//     chartArea
//       .append("g")
//       .call(d3.axisLeft(yScale).tickSize(-innerWidth).tickFormat(""))
//       .call((g) => g.selectAll(".tick line").attr("stroke", "#e5e7eb"))
//       .call((g) => g.select(".domain").remove());

//     // Barras do histograma
//     chartArea
//       .selectAll("rect")
//       .data(bins)
//       .enter()
//       .append("rect")
//       .attr("x", (d) => xScale(d.x0))
//       .attr("y", innerHeight)
//       .attr("width", (d) => Math.max(0, xScale(d.x1) - xScale(d.x0) - 1))
//       .attr("height", 0)
//       .attr("fill", "#3b82f6")
//       .attr("rx", 4)
//       .on("mouseover", function (event, d) {
//         tooltip.style("visibility", "visible")
//           .html(
//             `<strong>Intervalo:</strong> ${d.x0.toFixed(2)} - ${d.x1.toFixed(2)}<br/>
//              <strong>Frequência:</strong> ${d.length}`
//           );
//         d3.select(this).attr("fill", "#2563eb");
//       })
//       .on("mousemove", function (event) {
//         tooltip.style("top", `${event.offsetY - 40}px`).style("left", `${event.offsetX + 20}px`);
//       })
//       .on("mouseout", function () {
//         tooltip.style("visibility", "hidden");
//         d3.select(this).attr("fill", "#3b82f6");
//       })
//       .transition()
//       .duration(600)
//       .attr("y", (d) => yScale(d.length))
//       .attr("height", (d) => innerHeight - yScale(d.length));

//     // Eixos
//     chartArea.append("g").call(d3.axisLeft(yScale));
//     chartArea.append("g").attr("transform", `translate(0,${innerHeight})`).call(d3.axisBottom(xScale));

//     // Labels
//     svg.append("text")
//       .attr("x", width / 2)
//       .attr("y", height - 10)
//       .attr("text-anchor", "middle")
//       .style("fill", "#333")
//       .style("font-size", "14px")
//       .text(`${label} (variabilidade)`);

//     svg.append("text")
//       .attr("transform", "rotate(-90)")
//       .attr("x", -height / 2)
//       .attr("y", 15)
//       .attr("text-anchor", "middle")
//       .style("fill", "#333")
//       .style("font-size", "14px")
//       .text("Frequência (nº de quadros)");

//     svg.append("text")
//       .attr("x", width / 2)
//       .attr("y", margin.top - 10)
//       .attr("text-anchor", "middle")
//       .style("fill", "#666")
//       .style("font-size", "12px")
//       .text("Cada valor corresponde a um quadro de 40 ms (deslocamento de 20 ms)");

//     // Tooltip dentro do container
//     const tooltip = d3.select(svgRef.current.parentNode)
//       .append("div")
//       .style("position", "absolute")
//       .style("padding", "8px 12px")
//       .style("background", "#ffffff")
//       .style("border", "1px solid #ccc")
//       .style("border-radius", "6px")
//       .style("box-shadow", "0 2px 6px rgba(0,0,0,0.15)")
//       .style("font-size", "13px")
//       .style("pointer-events", "none")
//       .style("visibility", "hidden");

//     return () => tooltip.remove();
//   }, [values, label, width, height]);

//   return <svg ref={svgRef}></svg>;
// }
