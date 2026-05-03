// chartConfig.jsx
import { RadarChart, BarChart, ParameterBoxplot, LineChart, AcousticSpaceD3, AcousticSpaceD3V2, Boxplot, PauseBoxplot,IntensityChart } from "../../../../component/chart.jsx";

export const chartConfig = {
  radar: {
    // match: /^avg ([a-zA-Z]+)_/,
    match: /^(avg|max|min|std)[_\s\-]?([a-zA-Z0-9.\-]+)/i,
    labelPrefix: "Média",
    chartComponent: RadarChart,
  },

  line: {
    match: /^(.+)$/,
    labelPrefix: "",
    chartComponent: LineChart,
  },

  acousticSpace: {
    match: /^(avg) (F1|F2)$/,
    labelPrefix: "Média",
    chartComponent: AcousticSpaceD3,
  },

  acousticSpaceGrouped: {
    match: /^(avg) (F1|F2)$/,
    labelPrefix: "Média",
    chartComponent: AcousticSpaceD3V2,
  },

  acousticSpaceCompared: {
    match: /^(avg) (F1|F2)$/,
    labelPrefix: "Média",
    chartComponent: AcousticSpaceD3,
  },

  F0Boxplot: {
    match: /^(F0)$/,
    labelPrefix: "",
    chartComponent: Boxplot,
  },

  Boxplot: {
    match: /^(pauseDurations|Jitter|Shimmer)$/,
    labelPrefix: "",
    chartComponent: ParameterBoxplot,
  },

  Intensityplot: {
    match: /^(intensidade)$/,
    labelPrefix: "",
    chartComponent: IntensityChart,
  }

};