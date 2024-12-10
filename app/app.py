import streamlit as st
import pandas as pd
import os
import markdown2
import matplotlib.pyplot as plt
from PIL import Image
import io

# Load the data
data_path = 'data/evaluations.csv'
if not os.path.exists(data_path):
    st.error(f"Data file not found: {data_path}")
    st.stop()
data = pd.read_csv(data_path)

# Rename columns for better readability
data.rename(columns={
    'model': 'Model',
    'accessUI': 'Access UI',
    'codepercent': 'Code Percentage',
    'codechars': 'Code Characters',
    'charcount': 'Character Count',
    'codeblocks': 'Code Blocks',
    'output_number': 'Output Number'
}, inplace=True)

# Load the prompt
prompt_path = 'data/prompts/prompt.md'
if not os.path.exists(prompt_path):
    st.error(f"Prompt file not found: {prompt_path}")
    st.stop()
with open(prompt_path, 'r') as file:
    prompt_content = file.read()

# Load outputs
outputs_path = 'data/outputs'
if not os.path.exists(outputs_path):
    st.error(f"Outputs directory not found: {outputs_path}")
    st.stop()
output_files = sorted([f for f in os.listdir(outputs_path) if f.endswith('.md')], key=lambda x: int(x.replace('output', '').replace('.md', '')))

# Create visualizations
def create_bar_chart(data, column):
    plt.figure(figsize=(10, 6))
    data_sorted = data.sort_values(by=column, ascending=False)
    plt.bar(data_sorted['Model'], data_sorted[column])
    plt.xlabel('Model')
    plt.ylabel(column)
    plt.title(column)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Convert plot to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image = Image.open(buf)
    return image

# Define the Streamlit interface
def view_data():
    st.dataframe(data, height=600)  # Increase height to avoid scrolling

def view_prompt():
    st.markdown(prompt_content)

def view_output(file_index):
    if file_index < 0 or file_index >= len(output_files):
        st.error("Invalid file index")
        return
    with open(os.path.join(outputs_path, output_files[file_index]), 'r') as file:
        output_content = file.read()
    st.markdown(output_content)

def create_plots():
    charcount_plot = create_bar_chart(data, 'Character Count')
    codepercent_plot = create_bar_chart(data, 'Code Percentage')
    codeblocks_plot = create_bar_chart(data, 'Code Blocks')
    return charcount_plot, codepercent_plot, codeblocks_plot

# Streamlit app
st.title("LLM Large Long Output Evaluation")

# Sidebar navigation
st.sidebar.title("Navigation")
data_tab = st.sidebar.button("Data", use_container_width=True)
visualizations_tab = st.sidebar.button("Visualizations", use_container_width=True)
outputs_tab = st.sidebar.button("Outputs", use_container_width=True)
prompt_tab = st.sidebar.button("Prompt", use_container_width=True)
report_tab = st.sidebar.button("Report", use_container_width=True)

# GitHub repository button
st.sidebar.markdown(
    "[![GitHub](https://img.shields.io/badge/GitHub-danielrosehill%2FLLM--Long--Codegen--Test-blue?logo=github)](https://github.com/danielrosehill/LLM-Long-Codegen-Test)"
)

# About section
st.sidebar.markdown("""
### About
This experiment was conducted on the 10th of December 2024 by Daniel Rosehill.  
The purpose of this experiment was to compare different large language models' ability to generate a long continuous output in response to a large and demanding prompt.
""")

# Main content based on button clicks
if data_tab:
    st.header("Data Table")
    view_data()
elif visualizations_tab:
    st.header("Visualizations")
    charcount_plot, codepercent_plot, codeblocks_plot = create_plots()
    
    st.image(charcount_plot, caption="Character Count")
    st.image(codepercent_plot, caption="Code Percentage")
    st.image(codeblocks_plot, caption="Code Blocks")
elif outputs_tab:
    st.header("Outputs")
    output_index = st.number_input("Output Index (0 to {})".format(len(output_files) - 1), min_value=0, max_value=len(output_files) - 1, value=0, step=1)
    view_output(output_index)
elif prompt_tab:
    st.header("Prompt")
    view_prompt()
elif report_tab:
    st.header("Thoughts")
    report_content = """
The purpose of this experiment was to compare and evaluate the capability of different code generation large language models to generate a single long continuous output.

The prompt used as well as all the outputs are recorded in the data folder. The demanding prompt requested that the LLM assist in the generation of a Open AI Whisper Speech to text transcription GUI for Linux.

Various large language models were tested across different platforms, including models deployed on Hugging Face, those available via Open Router, and those hosted locally on LM Studio.

The outputs were recorded in their original form in the outputs folder and a script was used to calculate the character count as well as the percentage of code in the outputs, which was calculated by computing the character count within code fences and comparing that to the total character count in the output.

Additionally, the number of code blocks within each single output was computed by calculating the number of code blocks in the output.

### Longest Generation: Qwen 2.5 Coder

Qwen 2.5 Coder generated the longest single output at 13,950 characters, almost 90% of which constituted code spread across five different code blocks.

Discrepancies between runs on the same platform, and when comparing the same model's output across different access interfaces, were overall quite small. Quen 2.5 when accessed via Open Router via its API yielded an output of 13,159 characters with a code percentage of 82%. This works out to a difference in output length of 5.7 %.

Qwen's larger 72B parameter instruction model generated an output that was almost as long as that of its smaller code specific sibling, 2.5 Coder (12,921 characters, 84% within codefences).

The lengthiest response among the "Western" models was the one generated by OpenAI's o-1 Preview, accessed via API, which generated 13,622 characters (82% within codefences) and the largest number of unique code blocks at 10.
    """
    st.markdown(report_content)
else:
    st.header("Data Table")
    view_data()