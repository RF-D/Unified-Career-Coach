import streamlit as st
import pandas as pd
from unified import UnifiedApis
import asyncio
import re
import plotly.express as px


# Initialize the UnifiedApis clients once at the module level
openai_client = UnifiedApis(
    provider="openai", model="gpt-4o", use_async=True, json_mode=True
)

claude_client = UnifiedApis(
    provider="anthropic", model="claude-3-5-sonnet-20240620", use_async=True
)

gemini_client = UnifiedApis(
    provider="openrouter", model="google/gemini-pro-1.5", use_async=True
)


class MindCareerAssistant:
    def __init__(self):
        self.job_market_data = pd.DataFrame(
            {
                "job_title": [
                    "Data Scientist",
                    "Software Engineer",
                    "Product Manager",
                    "UX Designer",
                ],
                "growth_rate": [0.3, 0.25, 0.2, 0.22],
            }
        )

    async def update_job_categories(self, query):
        response = await openai_client.chat_async(
            f"""Based on the following text, suggest at least 5 relevant job categories and their estimated growth rates. 
        If the text suggests fewer than 5 categories, add related or complementary job categories to reach a total of 5.
        Return the result as a JSON object where keys are job titles and values are growth rates (as decimals, e.g., 0.25 for 25% growth).
        Text: '{query}'"""
        )

        if isinstance(response, dict) and len(response) >= 5:
            new_job_data = [
                {"job_title": title, "growth_rate": rate}
                for title, rate in response.items()
            ]
        else:
            print(
                f"Unexpected response format or insufficient job categories: {response}"
            )
            # Fallback to ensure at least 5 job categories
            default_categories = [
                "Data Scientist",
                "Software Engineer",
                "Product Manager",
                "UX Designer",
                "Marketing Specialist",
            ]
            new_job_data = [
                {"job_title": title, "growth_rate": 0.2} for title in default_categories
            ]

        self.job_market_data = pd.DataFrame(new_job_data)

        # Ensure we have exactly 5 categories
        if len(self.job_market_data) > 5:
            self.job_market_data = self.job_market_data.nlargest(5, "growth_rate")
        elif len(self.job_market_data) < 5:
            additional_categories = [
                {"job_title": f"Additional Category {i}", "growth_rate": 0.1}
                for i in range(5 - len(self.job_market_data))
            ]
            self.job_market_data = pd.concat(
                [self.job_market_data, pd.DataFrame(additional_categories)]
            )

    async def analyze_mood(self, text):
        return await openai_client.chat_async(
            f"""Analyze the sentiment of the following text. Return the result in the following JSON format:
        {{
            "sentiment": "Brief description of the sentiment",
            "score": A number between -1 (very negative) and 1 (very positive),
            "analysis": "Detailed analysis of the person's mood and emotional state",
            "career_impact": "How this emotional state might affect career decisions or performance"
        }}
        Text: {text}"""
        )

    async def analyze_job_market_alignment(self, user_input):
        job_categories = ", ".join(self.job_market_data["job_title"].tolist())
        response = await openai_client.chat_async(
            f"""Analyze how well the given text aligns with these job categories: {job_categories}. Return the result in the following JSON format:
        {{
            "alignments": [
                {{
                    "job_title": "Job title",
                    "score": A number between 0 and 1 indicating alignment,
                    "reason": "Brief explanation of the alignment score"
                }},
                ...
            ]
        }}
        Text to analyze: '{user_input}'"""
        )

        # Add error handling and logging
        if not isinstance(response, dict) or "alignments" not in response:
            print(f"Unexpected response format: {response}")
            return {"alignments": []}

        return response

    async def generate_career_path_analysis(self, user_input, skills):
        response = await claude_client.chat_async(
            f"""Based on the following user input and skills, provide a detailed career path analysis. Consider both short-term and long-term career prospects, potential challenges, and areas for growth.

        User Input: {user_input}
        Skills: {skills}

        Respond in the following format:
        <short_term_prospects>Analysis of immediate career opportunities</short_term_prospects>
        <long_term_prospects>Potential career trajectory over the next 5-10 years</long_term_prospects>
        <challenges>Potential obstacles or challenges in this career path</challenges>
        <growth_areas>Key areas for skill development and personal growth</growth_areas>
        """
        )
        return response

    async def create_skill_development_plan(self, career_goal, current_skills):
        response = await claude_client.chat_async(
            f"""Create a personalized skill development plan for someone aiming to become a {career_goal}. Consider their current skills and suggest a roadmap for acquiring new skills or improving existing ones.

        Current Skills: {current_skills}

        Provide your response in the following format:
        <core_skills>List of essential skills for this career path</core_skills>
        <skill_gaps>Identification of skills the person needs to develop</skill_gaps>
        <learning_resources>Suggested courses, books, or online resources for skill development</learning_resources>
        <timeline>Proposed timeline for skill acquisition (e.g., 3 months, 6 months, 1 year goals)</timeline>
        """
        )
        return response

    async def forecast_industry_trends(self, user_input, job_categories):
        response = await claude_client.chat_async(
            f"""Based on the following user input and job categories, forecast key trends and developments in the relevant industries over the next 5 years. Consider technological advancements, market shifts, and potential disruptions.

        User Input: {user_input}
        Job Categories: {job_categories}

        Provide your response in the following format:
        <industries>List the main industries relevant to the user's input and job categories</industries>
        <technological_trends>Key technological advancements expected in these industries</technological_trends>
        <market_shifts>Predicted changes in market dynamics or consumer behavior</market_shifts>
        <potential_disruptions>Possible disruptive forces or game-changing innovations</potential_disruptions>
        <career_implications>How these trends might affect career opportunities in the identified industries</career_implications>
        """
        )
        return response


def parse_claude_response(response, tags):
    parsed = {}
    for tag in tags:
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            parsed[tag] = match.group(1).strip()
    return parsed


async def follow_up_chat(question, context):
    response = await gemini_client.chat_async(
        f"""Based on the following context, please answer the user's question:

        Context: {context}

        User's question: {question}

        Provide a concise and relevant answer."""
    )
    return response


async def run_analysis(assistant, user_input, skills):
    await assistant.update_job_categories(user_input)

    # Mood Analysis
    mood_analysis = await assistant.analyze_mood(user_input)
    st.header("Mood Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sentiment", mood_analysis["sentiment"])
    with col2:
        st.progress(
            float(mood_analysis["score"] + 1) / 2,
            text=f"Score: {mood_analysis['score']:.2f}",
        )

    with st.expander("Detailed Mood Analysis"):
        st.write(f"Analysis: {mood_analysis['analysis']}")
        st.write(f"Career Impact: {mood_analysis['career_impact']}")

    # Job Market Alignment
    job_insights = await assistant.analyze_job_market_alignment(user_input)
    st.header("Job Market Alignment")

    # Create a bar chart for job alignments
    alignments = sorted(
        job_insights["alignments"], key=lambda x: x["score"], reverse=True
    )
    top_5_alignments = alignments[:5]

    if not top_5_alignments:
        st.write("No job alignments found.")
    else:
        fig = px.bar(
            x=[a["job_title"] for a in top_5_alignments],
            y=[a["score"] for a in top_5_alignments],
            labels={"x": "Job Title", "y": "Alignment Score"},
            title=f"Top {len(top_5_alignments)} Job Category Alignments",
        )
        st.plotly_chart(fig)

    with st.expander("Alignment Details"):
        for alignment in top_5_alignments:
            st.write(f"- {alignment['job_title']}: {alignment['score']:.2f}")
            st.write(f"  Reason: {alignment['reason']}")

    # Career Path Analysis
    career_path_analysis = await assistant.generate_career_path_analysis(
        user_input, skills
    )
    parsed_career_analysis = parse_claude_response(
        career_path_analysis,
        ["short_term_prospects", "long_term_prospects", "challenges", "growth_areas"],
    )
    st.header("Career Path Analysis")

    for key, value in parsed_career_analysis.items():
        with st.expander(key.replace("_", " ").title()):
            st.write(value)

    # Skill Development Plan
    top_career = assistant.job_market_data.iloc[0]["job_title"]
    skill_plan = await assistant.create_skill_development_plan(top_career, skills)
    parsed_skill_plan = parse_claude_response(
        skill_plan, ["core_skills", "skill_gaps", "learning_resources", "timeline"]
    )
    st.header("Skill Development Plan")

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("Core Skills"):
            st.write(parsed_skill_plan["core_skills"])
    with col2:
        with st.expander("Skill Gaps"):
            st.write(parsed_skill_plan["skill_gaps"])

    with st.expander("Learning Resources"):
        st.write(parsed_skill_plan["learning_resources"])

    with st.expander("Timeline"):
        st.write(parsed_skill_plan["timeline"])

    # Industry Forecast
    job_categories = ", ".join(assistant.job_market_data["job_title"].tolist())
    industry_forecast = await assistant.forecast_industry_trends(
        user_input, job_categories
    )
    parsed_forecast = parse_claude_response(
        industry_forecast,
        [
            "industries",
            "technological_trends",
            "market_shifts",
            "potential_disruptions",
            "career_implications",
        ],
    )
    st.header("Industry Forecast")

    tabs = st.tabs(
        [
            "Relevant Industries",
            "Technological Trends",
            "Market Shifts",
            "Potential Disruptions",
            "Career Implications",
        ]
    )
    for tab, (key, value) in zip(tabs, parsed_forecast.items()):
        with tab:
            st.write(value)

    # Job Market Data Visualization
    st.header("Job Market Overview")
    fig = px.scatter(
        assistant.job_market_data,
        x="job_title",
        y="growth_rate",
        size="growth_rate",
        hover_name="job_title",
        title="Job Growth Rates",
        labels={"growth_rate": "Growth Rate", "job_title": "Job Title"},
    )
    st.plotly_chart(fig)

    # Return analysis results for follow-up chat
    return {
        "mood_analysis": mood_analysis,
        "job_insights": job_insights,
        "career_path_analysis": parsed_career_analysis,
        "skill_plan": parsed_skill_plan,
        "industry_forecast": parsed_forecast,
    }


def update_session_state():
    st.session_state.user_input = st.session_state.user_input_widget
    st.session_state.skills = st.session_state.skills_widget


def main():
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    st.title("Unified Coach: AI-Powered Career Assistant 🚀")
    # Add custom CSS
    st.markdown(
        """
        <style>
        .stTextArea [data-baseweb="textarea"] {
            margin-top: -1rem;
        }
        .stTextArea {
            margin-bottom: auto;
        }
        
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Initialize session state variables
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "skills" not in st.session_state:
        st.session_state.skills = ""
    if "assistant" not in st.session_state:
        st.session_state.assistant = MindCareerAssistant()

    # Main content area
    if not st.session_state.analysis_complete:
        display_input_form()
    else:
        results_container = st.container()
        with results_container:
            st.markdown('<div class="fixed-height">', unsafe_allow_html=True)
            display_analysis_results(st.session_state.analysis_results)
            st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 3])
        if col1.button("Start Over"):
            reset_session_state()
            st.rerun()
        col2.info("You can ask follow-up questions in the sidebar chat!")

    # Sidebar chat
    with st.sidebar:
        st.subheader("Follow-up Chat")

        if not st.session_state.analysis_complete:
            st.info("Please complete the analysis to enable the chat feature.")
        else:
            # Chat input and send button (moved to the top)
            prompt = st.text_input("Ask a follow-up question:", key="chat_input")
            if st.button("Send"):
                if prompt:
                    st.session_state.messages.append(
                        {"role": "user", "content": prompt}
                    )
                    with st.spinner("Processing your question..."):
                        context = str(st.session_state.analysis_results)
                        response = asyncio.run(follow_up_chat(prompt, context))
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                    st.rerun()

            # Chat display (moved to the bottom)
            chat_container = st.container()
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])


def display_input_form():
    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("Explore", "Career Options", "🔍")
        col2.metric("Analyze", "Your Skills", "📊")
        col3.metric("Get", "Personalized Insights", "🌟")

    with st.form(key="input_form"):
        st.markdown("### **How are you feeling today? What are your career goals?**")
        user_input = st.text_area(
            label="",
            height=100,
            placeholder="E.g., I'm feeling excited about new opportunities in tech. My goal is to transition into a data science role within the next year.",
            key="user_input_widget",
        )

        st.markdown("### **List your current skills:**")
        skills = st.text_area(
            label="",
            height=100,
            placeholder="E.g., Python programming, data analysis, machine learning basics, SQL, communication skills",
            key="skills_widget",
        )

        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        st.session_state.user_input = user_input
        st.session_state.skills = skills
        with st.spinner("Analyzing your input..."):
            analysis_results = asyncio.run(
                run_analysis(
                    st.session_state.assistant,
                    st.session_state.user_input,
                    st.session_state.skills,
                )
            )
            st.session_state.analysis_results = analysis_results
            st.session_state.analysis_complete = True
        st.rerun()


def reset_session_state():
    st.session_state.analysis_complete = False
    st.session_state.analysis_results = None
    st.session_state.messages = []
    st.session_state.user_input = ""
    st.session_state.skills = ""
    st.session_state.assistant = MindCareerAssistant()


def display_analysis_results(results):
    # Mood Analysis
    st.header("Mood Analysis")
    mood_analysis = results["mood_analysis"]
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sentiment", mood_analysis["sentiment"])
    with col2:
        st.progress(
            float(mood_analysis["score"] + 1) / 2,
            text=f"Score: {mood_analysis['score']:.2f}",
        )

    with st.expander("Detailed Mood Analysis", expanded=True):
        st.write(f"Analysis: {mood_analysis['analysis']}")
        st.write(f"Career Impact: {mood_analysis['career_impact']}")

    # Job Market Alignment
    st.header("Job Market Alignment")
    job_insights = results["job_insights"]

    # Create a bar chart for job alignments
    alignments = sorted(
        job_insights["alignments"], key=lambda x: x["score"], reverse=True
    )
    top_5_alignments = alignments[:5]

    if not top_5_alignments:
        st.write("No job alignments found.")
    else:
        fig = px.bar(
            x=[a["job_title"] for a in top_5_alignments],
            y=[a["score"] for a in top_5_alignments],
            labels={"x": "Job Title", "y": "Alignment Score"},
            title=f"Top {len(top_5_alignments)} Job Category Alignments",
        )
        st.plotly_chart(fig)

    with st.expander("Alignment Details", expanded=True):
        for alignment in top_5_alignments:
            st.write(f"- {alignment['job_title']}: {alignment['score']:.2f}")
            st.write(f"  Reason: {alignment['reason']}")

    # Career Path Analysis
    st.header("Career Path Analysis")
    career_path_analysis = results["career_path_analysis"]

    for key, value in career_path_analysis.items():
        with st.expander(key.replace("_", " ").title(), expanded=True):
            st.write(value)

    # Skill Development Plan
    st.header("Skill Development Plan")
    skill_plan = results["skill_plan"]

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("Core Skills", expanded=True):
            st.write(skill_plan["core_skills"])
    with col2:
        with st.expander("Skill Gaps", expanded=True):
            st.write(skill_plan["skill_gaps"])

    with st.expander("Learning Resources", expanded=True):
        st.write(skill_plan["learning_resources"])

    with st.expander("Timeline", expanded=True):
        st.write(skill_plan["timeline"])

    # Industry Forecast
    st.header("Industry Forecast")
    industry_forecast = results["industry_forecast"]

    tabs = st.tabs(
        [
            "Relevant Industries",
            "Technological Trends",
            "Market Shifts",
            "Potential Disruptions",
            "Career Implications",
        ]
    )
    for tab, (key, value) in zip(tabs, industry_forecast.items()):
        with tab:
            st.write(value)

    # Job Market Data Visualization
    st.header("Job Market Overview")
    job_market_data = pd.DataFrame(results["job_insights"]["alignments"])
    fig = px.scatter(
        job_market_data,
        x="job_title",
        y="score",
        size="score",
        hover_name="job_title",
        title="Job Alignment Scores",
        labels={"score": "Alignment Score", "job_title": "Job Title"},
    )
    st.plotly_chart(fig)


if __name__ == "__main__":
    main()
