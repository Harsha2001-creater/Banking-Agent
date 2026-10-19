# 🏦 NexusBank AI: Autonomous Cloud-Connected Banking Agent

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-orange.svg?style=for-the-badge&logo=langchain)
![PostgreSQL](https://img.shields.io/badge/AWS_RDS-PostgreSQL-336791.svg?style=for-the-badge&logo=postgresql)
![AWS S3](https://img.shields.io/badge/AWS_S3-Data_Lake-569A31.svg?style=for-the-badge&logo=amazons3)
![Streamlit](https://img.shields.io/badge/Streamlit-Claude_UI-FF4B4B.svg?style=for-the-badge&logo=streamlit)
![Status](https://img.shields.io/badge/Status-Phase_8_Active-brightgreen.svg?style=for-the-badge)

An enterprise-grade, stateful AI banking assistant built with **LangGraph**, **Python**, and **AWS Cloud Infrastructure**. Moving beyond standard stateless chatbots, this agent couples structured SQL lookups against live AWS RDS ledgers with unstructured Agentic RAG against an S3 regulatory data lake. 

The system features **persistent database checkpointing** (`PostgresSaver`) so session memory survives server restarts and browser reloads, an Anthropic Claude-inspired web interface, real-time streaming tool execution status widgets, and strict Human-in-the-Loop (HITL) dispute protocols.