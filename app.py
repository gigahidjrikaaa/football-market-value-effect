import streamlit as st
import pandas as pd
import numpy as np
import datetime
from PIL import Image
from streamlit.proto.RootContainer_pb2 import SIDEBAR
import matplotlib.pyplot as plt

# Hero image
image = Image.open('images/pl-hero.png')
st.image(image, use_column_width=True)

# Sidebar
st.sidebar.header("Navigation")
st.sidebar.subheader("Go to")
app_mode = st.sidebar.selectbox("", ["Home", "Data", "Model", "About"])
if app_mode == "Home":
    st.header("Home")
    st.write("Welcome to the Plant Leaf Disease Detection App!")
    st.write("This app is designed to help farmers and gardeners to detect diseases in their plants.")
    st.write("Please select a page in the sidebar to get started.")
elif app_mode == "Data":
    st.header("Data")
    st.write("This app uses a dataset of plant leaf images from Kaggle.")
elif app_mode == "Model":
    st.header("Model")
    st.write("This app uses a pretrained convolutional neural network to detect plant leaf diseases.")
elif app_mode == "About":
    st.header("About")
    st.write("This app was created by [Izzat Arroyan](https://www.linkedin.com/in/izzatarroyan/), [Giga Hidjrika Aura Adkhy](https://www.linkedin.com/in/gigahidjrikaaa/), and [Daffa Kamal](https://www.linkedin.com/in/daffakamal/).")

# Title
st.title("Hello World")
st.write("This is my first Streamlit app!")

st.write("Here's our first attempt at using data to create a table:")
st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))

button = st.button("Say hello")
if button:
    st.write("Why hello there")
else:
    st.write("Goodbye")

agree = st.checkbox("I agree")
if agree:
    st.write("Great!")
else:
    st.write("Nothing for you")

genre = st.radio(
    "What's your favorite movie genre",
    ('Comedy', 'Drama', 'Documentary')
)
if genre == 'Comedy':
    st.write("You selected comedy.")
else:
    st.write("You didn't select comedy.")

option = st.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)
st.write('You selected:', option)

options = st.multiselect(
    'What are your favorite colors',
    ['Green', 'Yellow', 'Red', 'Blue'],
    ['Yellow', 'Red']
)
st.write('You selected:', options)

age = st.slider('How old are you?', 0, 130, 25)
st.write("I'm ", age, 'years old')

values = st.slider(
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0)
)
st.write('Values:', values)

title = st.text_input('Movie title', 'Life of Brian')
st.write('The current movie title is', title)

number = st.number_input('Insert a number')
st.write('The current number is ', number)

txt = st.text_area('Text to analyze', '''
    It was the best of times, it was the worst of times, it was
    the age of wisdom, it was the age of foolishness, it was
    the epoch of belief, it was the epoch of incredulity, it
    was the season of Light, it was the season of Darkness, it
    was the spring of hope, it was the winter of despair, (...)
''')
st.write('Sentiment:', txt)

d = st.date_input(
    "When's your birthday",
    datetime.date(2019, 7, 6)
)
st.write('Your birthday is:', d)

t = st.time_input('Set an alarm for', datetime.time(8, 45))
st.write('Alarm is set for', t)

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write(data)

color = st.color_picker('Pick A Color', '#00f900')
st.write('The current color is', color)