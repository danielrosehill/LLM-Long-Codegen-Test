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
    st.dataframe(data)

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
tab = st.sidebar.radio("Navigate", ["Data", "Visualizations", "Outputs", "Prompt"])

# Data Tab
if tab == "Data":
    st.header("Data Table")
    view_data()

# Visualizations Tab
elif tab == "Visualizations":
    st.header("Visualizations")
    charcount_plot, codepercent_plot, codeblocks_plot = create_plots()
    
    st.image(charcount_plot, caption="Character Count")
    st.image(codepercent_plot, caption="Code Percentage")
    st.image(codeblocks_plot, caption="Code Blocks")

# Outputs Tab
elif tab == "Outputs":
    st.header("Outputs")
    output_index = st.number_input("Output Index (0 to {})".format(len(output_files) - 1), min_value=0, max_value=len(output_files) - 1, value=0, step=1)
    view_output(output_index)

# Prompt Tab
elif tab == "Prompt":
    st.header("Prompt")
    view_prompt()