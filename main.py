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
    st.header(f"Skill Development Plan for {top_career}")

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


def main():
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    st.title("MindCareer: AI-Powered Mental Health and Career Assistant")

    # Initialize session state variables
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Main content area
    user_input = st.text_area(
        "How are you feeling today? What are your career goals?", height=150
    )
    skills = st.text_area("List your current skills:")

    if st.button("Analyze"):
        with st.spinner("Analyzing your input..."):
            assistant = MindCareerAssistant()
            analysis_results = asyncio.run(run_analysis(assistant, user_input, skills))
            st.session_state.update(analysis_results)
            st.session_state.analysis_complete = True

    # Sidebar chat (always visible, but only functional after analysis)
    with st.sidebar:
        st.subheader("Follow-up Chat")

        if not st.session_state.analysis_complete:
            st.info("Please complete the analysis to enable the chat feature.")

        # Chat input at the top of the sidebar
        prompt = st.text_input(
            "Ask a follow-up question:", disabled=not st.session_state.analysis_complete
        )
        if st.button("Send", disabled=not st.session_state.analysis_complete):
            if prompt:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})

                # Get AI response
                with st.spinner("Processing your question..."):
                    context = "\n".join(
                        [
                            f"{key}: {value}"
                            for key, value in st.session_state.items()
                            if key not in ["messages", "analysis_complete"]
                        ]
                    )
                    response = asyncio.run(follow_up_chat(prompt, context))

                # Add AI response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Display analysis results
    if st.session_state.analysis_complete:
        st.header("Mood Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sentiment", st.session_state.mood_analysis["sentiment"])
        with col2:
            st.progress(
                float(st.session_state.mood_analysis["score"] + 1) / 2,
                text=f"Score: {st.session_state.mood_analysis['score']:.2f}",
            )

        with st.expander("Detailed Mood Analysis"):
            st.write(f"Analysis: {st.session_state.mood_analysis['analysis']}")
            st.write(
                f"Career Impact: {st.session_state.mood_analysis['career_impact']}"
            )

        st.header("Job Market Alignment")
        alignments = sorted(
            st.session_state.job_insights["alignments"],
            key=lambda x: x["score"],
            reverse=True,
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

        st.header("Career Path Analysis")
        for key, value in st.session_state.career_path_analysis.items():
            with st.expander(key.replace("_", " ").title()):
                st.write(value)

        st.header(
            f"Skill Development Plan for {st.session_state.skill_plan['core_skills'].split(', ')[0]}"
        )
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("Core Skills"):
                st.write(st.session_state.skill_plan["core_skills"])
        with col2:
            with st.expander("Skill Gaps"):
                st.write(st.session_state.skill_plan["skill_gaps"])

        with st.expander("Learning Resources"):
            st.write(st.session_state.skill_plan["learning_resources"])

        with st.expander("Timeline"):
            st.write(st.session_state.skill_plan["timeline"])

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
        for tab, (key, value) in zip(tabs, st.session_state.industry_forecast.items()):
            with tab:
                st.write(value)

        st.header("Job Market Overview")
        fig = px.scatter(
            pd.DataFrame(st.session_state.job_insights["alignments"]),
            x="job_title",
            y="score",
            size="score",
            hover_name="job_title",
            title="Job Growth Rates",
            labels={"score": "Growth Rate", "job_title": "Job Title"},
        )
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()
