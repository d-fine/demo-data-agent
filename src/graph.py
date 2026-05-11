from pydantic_graph import Graph

from agents import ChartSummarizerNode, ExecutorNode, PlannerNode, SynthesizerNode, VisualizerNode, WebResearchNode

graph = Graph(nodes=[PlannerNode, ExecutorNode, WebResearchNode, VisualizerNode, ChartSummarizerNode, SynthesizerNode])
