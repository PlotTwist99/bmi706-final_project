# streamlit app code file
import streamlit
from multiapp import MultiApp
from apps import streamlit_task1, streamlit_task2_4
#from apps import streamlit_task1, streamlit_task2_4, streamlit_task3


app = MultiApp()

app.add_app("Task 1", streamlit_task1.app)
app.add_app("Task 2 & 4", streamlit_task2_4.app)
#app.add_app("Task 3", streamlit_task3.app)
# The main app
app.run()
