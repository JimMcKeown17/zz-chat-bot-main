from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import os
import asyncio
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
import gradio as gr
from prompts import *
from tools import *
from tools_2023_2024 import *

load_dotenv(override=True)

# Create a single event loop for the application
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

zazi_2023_agent = Agent(
        name="Zazi 2023 Agent",
        instructions=instructions_2023,
        model="gpt-4o-mini",
        tools=[
        get_benchmark_performance_2023,
        calculate_improvement_2023,
        get_performance_breakdown_2023,
        identify_students_needing_support_2023,
        get_summary_statistics_2023,
        analyze_program_effectiveness_2023,
        school_comparison_report_2023,
        get_data_info_2023
    ]
)

zazi_2024_agent = Agent(
        name="Zazi 2024 Agent",
        instructions=instructions_2024,
        model="gpt-4o-mini",
        tools=[
        get_benchmark_performance_2024,
        calculate_improvement_2024,
        get_performance_breakdown_2024,
        identify_students_needing_support_2024,
        get_summary_statistics_2024,
        analyze_program_effectiveness_2024,
        school_comparison_report_2024,
        get_data_info_2024
    ]
)

zazi_2025_agent = Agent(
        name="Zazi 2025 Agent",
        instructions=instructions_2025,
        model="gpt-4o-mini",
        tools=[get_2025_number_of_children]
)

tool_2023 = zazi_2023_agent.as_tool(tool_name="2023_researcher", tool_description="Provides information, data, and statistics about the Zazi iZandi 2023 programme.")
tool_2024 = zazi_2024_agent.as_tool(tool_name="2024_researcher", tool_description="Provides information, data, and statistics about the Zazi iZandi 2024 programme.")
tool_2025 = zazi_2025_agent.as_tool(tool_name="2025_researcher", tool_description="Provides information, data, and statistics about the Zazi iZandi 2025 programme.")

zazi_supervisor = Agent(
        name="Zazi Supervisor",
        instructions=instructions_supervisor,
        model="gpt-4o",
        tools=[tool_2023, tool_2024, tool_2025]
)

async def chat_async(message, history):
    # You could also parse history if needed
    result = await Runner.run(zazi_supervisor, message)
    return str(result.final_output)

def chat(message, history):
    # Use the persistent event loop instead of creating a new one
    return loop.run_until_complete(chat_async(message, history))

if __name__ == "__main__":
        gr.ChatInterface(
        fn=chat,
        title="Zazi iZandi Bot",
        description="Ask anything about the 2023, 2024, or 2025 literacy programme data.",
        examples=[
            "What type of impact has the programme had?",
            "How did the children perform in 2024?", 
            "Why does teaching letter sounds matter?",
            "What are the reading benchmarks in South Africa?",
            "What percentage of Grade 1 children can read at grade level?",
            "How does Zazi iZandi compare to national reading performance?",
            "How can I get in touch and learn more about the programme?"
        ],
        ).launch()