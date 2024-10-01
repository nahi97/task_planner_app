import streamlit as st
import openai
import pandas as pd
from datetime import datetime
from io import StringIO

# Set your OpenAI API key
openai.api_key = 'Enter your API Key'  # Replace with your actual API key

# Streamlit App Title
st.title("AI-Assisted Task Planner")

st.markdown("""
This application helps you organize your day efficiently by generating an optimized schedule based on your tasks and preferences.
""")

# Sidebar for User Inputs
st.sidebar.header("Enter Your Tasks")

# Function to collect multiple tasks
def get_tasks():
    tasks = []
    num_tasks = st.sidebar.number_input("Number of tasks", min_value=1, max_value=20, value=3, step=1)
    
    for i in range(int(num_tasks)):
        st.sidebar.subheader(f"Task {i+1}")
        task_name = st.sidebar.text_input(f"Task {i+1} Name", key=f"name_{i}")
        duration = st.sidebar.number_input(f"Duration (minutes) for Task {i+1}", min_value=1, max_value=1440, value=60, step=1, key=f"duration_{i}")
        priority = st.sidebar.selectbox(f"Priority for Task {i+1}", options=["High", "Medium", "Low"], key=f"priority_{i}")
        
        if task_name:
            tasks.append({
                "Task": task_name,
                "Duration (min)": duration,
                "Priority": priority
            })
    return tasks

tasks = get_tasks()

# Time Inputs
st.sidebar.header("Daily Schedule")
start_time = st.sidebar.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M").time())
end_time = st.sidebar.time_input("End Time", value=datetime.strptime("17:00", "%H:%M").time())

# Function to generate the prompt
def generate_prompt(tasks, start_time, end_time):
    task_descriptions = ""
    for task in tasks:
        task_descriptions += f"- {task['Task']} ({task['Duration (min)']} minutes, priority: {task['Priority'].lower()})\n"
    
    # Calculate available minutes
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    available_minutes = int((end_dt - start_dt).total_seconds() / 60)
    
    prompt = f"""
I have the following tasks to complete today:
{task_descriptions}

My available time is from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}, which gives me {available_minutes} minutes.
Please generate an optimal schedule for me that prioritizes higher-priority tasks first but balances the workload.
Include breaks if necessary, and ensure no two high-priority tasks are scheduled back-to-back.
Format the schedule with start and end times for each task.
"""
    return prompt

# Button to generate schedule
if st.button("Generate Schedule"):
    if not tasks:
        st.error("Please enter at least one task.")
    else:
        with st.spinner("Generating your schedule..."):
            prompt = generate_prompt(tasks, start_time, end_time)
            
            try:
                response = openai.Completion.create(
                    engine="gpt-4o",
                    prompt=prompt,
                    max_tokens=500,
                    temperature=0.7,
                    n=1,
                    stop=None
                )
                schedule = response.choices[0].text.strip()
                st.success("Schedule Generated Successfully!")
                st.markdown("---")
                st.subheader("Your AI-Generated Task Schedule")
                st.text(schedule)
                
                # Option to download the schedule
                def convert_to_txt(text):
                    return StringIO(text)
                
                schedule_io = convert_to_txt(schedule)
                st.download_button(
                    label="Download Schedule as Text",
                    data=schedule_io,
                    file_name='task_schedule.txt',
                    mime='text/plain'
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Display entered tasks for reference
if tasks:
    st.markdown("---")
    st.subheader("Your Entered Tasks")
    df_tasks = pd.DataFrame(tasks)
    st.table(df_tasks)
