import os
os.environ["CREWAI_USE_MEMORY"] = "false"  # Prevents ChromaDB errors
import streamlit as st
import pypdf
import os
from crewai import Crew, Process, Agent, Task
from pyairtable import Table

# Airtable API setup
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

# Streamlit UI
st.title("📄 AI-Powered PDF Extractor & Airtable Uploader")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    with st.spinner("Extracting text from PDF..."):

        # Read PDF
        pdf_reader = pypdf.PdfReader(uploaded_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"

        st.subheader("📜 Extracted Text")
        st.text_area("Extracted Content", extracted_text, height=200)

        if st.button("Send to Airtable"):
            with st.spinner("Uploading to Airtable..."):

                # Define AI Agents
                extractor_agent = Agent(
                    role="Data Extractor",
                    goal="Extract key information from the PDF",
                    backstory="A skilled AI venture capital investment analyst designed to extract valuable insights from startup pitch decks.",
                    verbose=True
                )

                uploader_agent = Agent(
                    role="Airtable Uploader",
                    goal="Upload extracted data to Airtable",
                    backstory="An AI agent specialized in organizing and storing structured data.",
                    verbose=True
                )

                # Define Tasks
                extraction_task = Task(
                    description="Identify important insights about the startup from the extracted text.",
                    expected_output="A summary of the key points from the document.",
                    agent=extractor_agent
                )

                upload_task = Task(
                    description="Send extracted insights to Airtable for storage.",
                    expected_output="A successful entry in Airtable.",
                    agent=uploader_agent
                )

                # Run CrewAI Agents
                crew = Crew(
                    agents=[extractor_agent, uploader_agent],
                    tasks=[extraction_task, upload_task],
                    process=Process.sequential
                )

                insights = crew.kickoff()

                # Upload to Airtable
                table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
                table.create({"Extracted Insights": insights})

                st.success("✅ Data successfully uploaded to Airtable!")
