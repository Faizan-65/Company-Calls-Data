import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")
st.title('Job Application Analysis')
effective_min_diff = 9

def time_difference_adjustment(x):
    if pd.isna(x):
        return pd.NaT
    elif x <= pd.Timedelta(minutes=effective_min_diff):
        return x
    else:
        return pd.Timedelta(minutes=2)

# Upload CSV file
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    df['Applied At'] = pd.to_datetime(df['Applied At'])
    df['Applied At Date'] = df['Applied At'].dt.strftime('%Y-%m-%d')
    min_df_date = pd.to_datetime(df['Applied At Date'].min())
    max_df_date = pd.to_datetime(df['Applied At Date'].max())
    # Date and time picker widgets
    start_date = st.sidebar.date_input("Start Date", value=min_df_date)
    start_time = st.sidebar.time_input("Start Time", value=datetime.strptime("05:00", "%H:%M").time())
    end_date = st.sidebar.date_input("End Date", value=max_df_date)
    end_time = st.sidebar.time_input("End Time", value=datetime.strptime("15:00", "%H:%M").time())

    # Combine date and time into datetime objects
    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(end_date, end_time)
    start_time = pd.to_datetime(start_datetime)
    end_time = pd.to_datetime(end_datetime)

    applier_options = df['Job Applied By'].unique().tolist()
    selected_applier = st.multiselect('Select an Applier:', applier_options)
    st.header('Effective Working in Hours By Applier')

    matches = df['Job Applied By'].isin(selected_applier)
    df_filtered = df[matches]

    df_filtered = df_filtered[(df_filtered['Applied At'] >= start_time) & (df_filtered['Applied At'] <= end_time)]
    df_filtered.sort_values(by=['Job Applied By', 'Applied At'], inplace=True)
    # TODO: Make average applying adjustment feature. 
    df_filtered['Time Difference'] = df_filtered.groupby('Job Applied By')['Applied At'].diff().apply(time_difference_adjustment)
    # df_filtered['Time Difference'] = df_filtered['Time Difference'].apply(time_difference_adjustment)
    # df_filtered['Time Difference'] = df_filtered['Time Difference'].apply(
    #     lambda x: min(x, pd.Timedelta(minutes=4))
    # )
    effective_times = df_filtered.groupby(['Applied At Date', 'Job Applied By'])['Time Difference'].sum()
    # effective_times = df_filtered[df_filtered['Time Difference'] <= pd.Timedelta(minutes=effective_min_diff)].groupby(['Applied At Date', 'Job Applied By'])['Time Difference'].sum()

    effective_times_df = effective_times.reset_index().pivot(index='Job Applied By', columns='Applied At Date', values='Time Difference')
    effective_times_df = effective_times_df.astype(str)
    effective_times_df = effective_times_df.applymap(lambda x: x.replace('0 days ', '') if isinstance(x, str) else x)

    st.write(effective_times_df)

#==================================

    appliers = df['Job Applied By'].unique()
    df_filtered = df[matches]
    data_filtered = df_filtered.groupby(['Applied At Date', 'Job Applied By']).count()
    data_filtered = data_filtered.reset_index().pivot(index='Job Applied By', columns="Applied At Date", values='Job ID')
    st.header('Applying Count By Date')
    st.write(data_filtered)
    
#==================================
    
    appliers = df['Job Applied By'].unique()
    df_filtered = df[matches]

    # Plot hourly work done by each applier
    unique_dates = df_filtered['Applied At Date'].unique()

    # Add a date selector in Streamlit
    selected_date = st.selectbox('Select a date to plot:', unique_dates)
    # Filter the DataFrame based on the selected date
    df_selected = df_filtered[df_filtered['Applied At Date'] == selected_date]

    # Extract hour from 'Applied At' column
    df_selected['Hour'] = df_selected['Applied At'].dt.hour

    # Group by 'Job Applied By' and 'Hour' and count the number of applications
    hourly_counts = df_selected.groupby(['Job Applied By', 'Hour']).size().reset_index(name='Count')

    # Plot the data
    st.header('Hourly Work Done by Each Applier')
    fig = px.line(hourly_counts, x='Hour', y='Count', color='Job Applied By', markers=True,
                title=f'Hourly Work Done by Each Applier on {selected_date}',
                labels={'Hour': 'Hour of the Day', 'Count': 'Number of Applications', 'Job Applied By': 'Applier'})
    fig.update_traces(mode='lines+markers')
    st.plotly_chart(fig)

#==================================


    # st.header('Hourly Work Done by Each Applier')
    # # Unique dates in the DataFrame
    # df_filtered = df[matches]
    # unique_dates = df_filtered['Applied At Date'].unique()
    # unique_dates.sort()

    # # Initialize the session state for selected date
    # if 'selected_date' not in st.session_state:
    #     st.session_state.selected_date = unique_dates[0]

    # # Define navigation buttons
    # col1, col2, col3 = st.columns(3)

    # if col1.button('Previous Date'):
    #     current_index = list(unique_dates).index(st.session_state.selected_date)
    #     if current_index > 0:
    #         st.session_state.selected_date = unique_dates[current_index - 1]

    # if col3.button('Next Date'):
    #     current_index = list(unique_dates).index(st.session_state.selected_date)
    #     if current_index < len(unique_dates) - 1:
    #         st.session_state.selected_date = unique_dates[current_index + 1]

    # # Display the selected date
    # col2.write(f"Selected Date: {st.session_state.selected_date}")

    # # Filter the DataFrame based on the selected date
    # df_filtered = df_filtered[df_filtered['Applied At Date'] == st.session_state.selected_date]

    # # Extract hour from 'Applied At' column
    # df_filtered['Hour'] = df_filtered['Applied At'].dt.hour

    # # Group by 'Job Applied By' and 'Hour' and count the number of applications
    # hourly_counts = df_filtered.groupby(['Job Applied By', 'Hour']).size().reset_index(name='Count')

    # # Create two columns
    # col1, col2 = st.columns(2)

    # # Plot the first chart in the first column
    # with col1:
    #     # st.header('Hourly Work Done by Each Applier')
    #     fig = px.line(hourly_counts, x='Hour', y='Count', color='Job Applied By', markers=True,
    #                 title=f'Hourly Work Done by Each Applier on {st.session_state.selected_date}',
    #                 labels={'Hour': 'Hour of the Day', 'Count': 'Number of Applications', 'Job Applied By': 'Applier'})
    #     fig.update_traces(mode='lines+markers')
    #     st.plotly_chart(fig)

    # # Plot the second chart in the second column
    # with col2:
    #     # st.header('Hourly Work Done by Each Applier (Bar Plot)')
    #     fig_bar = px.bar(hourly_counts, x='Hour', y='Count', color='Job Applied By', barmode='group',
    #                     title=f'Hourly Work Done by Each Applier on {st.session_state.selected_date}',
    #                     labels={'Hour': 'Hour of the Day', 'Count': 'Number of Applications', 'Job Applied By': 'Applier'})
    #     fig_bar.update_layout(
    #         xaxis=dict(
    #             tickmode='linear',
    #             tick0=0,
    #             dtick=1  # This will set a tick every hour
    #         )
    #     )
    #     st.plotly_chart(fig_bar)



#==================================

    applier_job_titles = df.groupby('Job Applied By')['Job Title'].apply(list).reset_index()

    # Display a searchable dropdown to select an applier
    st.header('Job Titles Applied By Applier')
    applier_options = df['Job Applied By'].unique().tolist()
    selected_applier = st.selectbox('Select an Applier:', applier_options)

    # Filter the DataFrame based on the selected applier
    selected_jobs = df[df['Job Applied By'] == selected_applier]

    # Display the job titles and applied times in a table
    if not selected_jobs.empty:
        st.write(f"**{selected_applier}**")
        st.write(selected_jobs[['Job Title', 'Applied At']].reset_index())
    else:
        st.write("No job titles found for the selected applier.")
