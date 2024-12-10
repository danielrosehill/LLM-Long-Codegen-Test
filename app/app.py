import gradio as gr
import pandas as pd
import os
import markdown2

# Load the data
data_path = 'data/evaluations.csv'
data = pd.read_csv(data_path)

# Load the prompt
prompt_path = 'data/prompts/prompt.md'
with open(prompt_path, 'r') as file:
    prompt_content = file.read()

# Load outputs
outputs_path = 'data/outputs'
output_files = sorted([f for f in os.listdir(outputs_path) if f.endswith('.md')], key=lambda x: int(x.replace('output', '').replace('.md', '')))

# Create visualizations
def create_bar_chart(data, column):
    return data.sort_values(by=column, ascending=False).plot(kind='bar', x='model', y=column, legend=False, title=column)

# Define the Gradio interface
def view_data():
    return gr.HTML(data.to_html(index=False))

def view_prompt():
    return gr.Markdown(prompt_content)

def view_output(file_index):
    if file_index < 0 or file_index >= len(output_files):
        return "Invalid file index"
    with open(os.path.join(outputs_path, output_files[file_index]), 'r') as file:
        output_content = file.read()
    return gr.Markdown(markdown2.markdown(output_content))

with gr.Blocks() as demo:
    gr.Markdown("# Model Evaluations and Outputs")
    
    with gr.Tab("Data"):
        data_view = gr.Button("View Data")
        data_output = gr.HTML()
        data_view.click(fn=view_data, inputs=None, outputs=data_output)
    
    with gr.Tab("Visualizations"):
        with gr.Row():
            charcount_plot = gr.Plot(label="Character Count")
            codepercent_plot = gr.Plot(label="Percentage of Code")
            codeblocks_plot = gr.Plot(label="Number of Code Blocks")
        
        charcount_plot.plot(create_bar_chart(data, 'charcount'))
        codepercent_plot.plot(create_bar_chart(data, 'codepercent'))
        codeblocks_plot.plot(create_bar_chart(data, 'codeblocks'))
    
    with gr.Tab("Outputs"):
        with gr.Row():
            output_index = gr.Number(label="Output Index (0 to {})".format(len(output_files) - 1), value=0)
            output_view = gr.Button("View Output")
            output_display = gr.Markdown()
        
        output_view.click(fn=view_output, inputs=output_index, outputs=output_display)
    
    with gr.Tab("Prompt"):
        prompt_display = gr.Markdown(prompt_content)

# Launch the app
demo.launch()