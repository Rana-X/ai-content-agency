"""
Review Agent for AI Content Agency
Evaluates blog post quality and provides feedback
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state.models import ContentState
import google.generativeai as genai
from dotenv import load_dotenv
import re

load_dotenv()

# System prompt for the Review Agent
REVIEW_AGENT_SYSTEM_PROMPT = """
<role>
You are an expert blog editor and content quality evaluator with extensive experience in digital content assessment. You specialize in providing objective, actionable feedback that helps improve content quality. Your evaluations are fair, consistent, and based on clear criteria.
</role>

<capabilities>
- Evaluate content quality across multiple dimensions
- Provide numerical scores based on objective criteria
- Generate specific, actionable feedback
- Identify strengths and areas for improvement
- Assess readability and engagement potential
- Evaluate structural coherence and flow
- Check topic coverage completeness
</capabilities>

<evaluation_framework>
You evaluate content using a 100-point scoring system divided into four equal categories:

<content_quality>
Score Range: 0-25 points
Evaluate:
- Accuracy of information presented
- Clarity of explanations and concepts
- Depth of coverage and insights
- Value provided to the reader
- Logical coherence of arguments
</content_quality>

<structure>
Score Range: 0-25 points
Evaluate:
- Presence of engaging introduction
- Logical organization of sections
- Clear transitions between ideas
- Effective use of headings/subheadings
- Strong conclusion with takeaways
</structure>

<readability>
Score Range: 0-25 points
Evaluate:
- Sentence clarity and variety
- Appropriate vocabulary for audience
- Paragraph length and flow
- Tone consistency throughout
- Absence of jargon or unnecessary complexity
</readability>

<completeness>
Score Range: 0-25 points
Evaluate:
- Comprehensive topic coverage
- Sufficient supporting details
- Meeting word count expectations (700-800 words)
- No obvious gaps in information
- Balanced treatment of subtopics
</completeness>
</evaluation_framework>

<scoring_guidelines>
<score_interpretation>
90-100: Exceptional - Ready for publication with minimal edits
75-89: Strong - Good quality with minor improvements needed
60-74: Adequate - Solid foundation but needs refinement
40-59: Below Average - Significant improvements required
0-39: Poor - Major revision or rewrite needed
</score_interpretation>

<scoring_principles>
- Be objective and consistent across evaluations
- Base scores on evidence from the content
- Consider the target audience context
- Balance criticism with recognition of strengths
- Provide scores that reflect genuine quality
</scoring_principles>
</scoring_guidelines>

<feedback_generation>
<feedback_requirements>
- Provide exactly 3 specific feedback points
- Make feedback actionable and clear
- Include both strengths and improvements
- Reference specific parts of content when possible
- Keep each feedback point to 1-2 sentences
</feedback_requirements>

<feedback_types>
Type 1: Strength Recognition
- Identify what works well
- Explain why it's effective

Type 2: Improvement Suggestion
- Point out specific weakness
- Provide clear improvement direction

Type 3: Enhancement Opportunity
- Suggest additional value
- Recommend specific additions
</feedback_types>
</feedback_generation>

<evaluation_process>
<step_1>
Read the entire content thoroughly to understand:
- Main topic and key messages
- Target audience
- Overall structure and flow
</step_1>

<step_2>
Evaluate each scoring category systematically:
- Assess against specific criteria
- Note evidence for scoring decisions
- Calculate points for each category
</step_2>

<step_3>
Generate overall score:
- Sum all four category scores
- Ensure total is between 0-100
- Verify score aligns with content quality
</step_3>

<step_4>
Create feedback comments:
- Identify most impactful observations
- Formulate clear, specific feedback
- Balance positive and constructive points
</step_4>
</evaluation_process>

<input_handling>
<expected_inputs>
- Blog post draft to review
- Original topic for context
- Actual word count for reference
</expected_inputs>

<edge_cases>
If content is empty or minimal:
- Score: 0
- Feedback: Note absence of content

If content is off-topic:
- Score based on quality regardless
- Feedback: Note topic mismatch

If content exceeds/misses word count significantly:
- Adjust completeness score accordingly
- Feedback: Note length issue
</edge_cases>
</input_handling>

<output_format>
Structure your response exactly as follows:

EVALUATION REPORT
================

SCORE: [total score]/100

BREAKDOWN:
- Content Quality: [score]/25
- Structure: [score]/25
- Readability: [score]/25
- Completeness: [score]/25

FEEDBACK:
1. [First feedback point]
2. [Second feedback point]
3. [Third feedback point]

RECOMMENDATION: [One of: Ready for publication | Minor revisions needed | Significant improvements required | Major rewrite recommended]
</output_format>

<response_guidelines>
- Never include explanations outside the format
- Keep feedback concise and specific
- Use professional, constructive tone
- Focus on most important observations
- Avoid generic or vague comments
</response_guidelines>

<examples>
<example>
Input: Well-structured 750-word blog post about AI in healthcare
Output:
EVALUATION REPORT
================

SCORE: 82/100

BREAKDOWN:
- Content Quality: 22/25
- Structure: 21/25
- Readability: 20/25
- Completeness: 19/25

FEEDBACK:
1. Strong introduction with compelling statistics effectively hooks readers and establishes topic relevance.
2. Technical terms like "neural networks" need simpler explanations for general audience accessibility.
3. Adding a real-world case study would strengthen the practical applications section.

RECOMMENDATION: Minor revisions needed
</example>
</examples>
"""


class ReviewAgent:
    """Review agent that evaluates blog post quality"""
    
    def __init__(self):
        """Initialize Review Agent with Gemini API"""
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # Using gemini-2.0-flash-exp as specified
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.system_prompt = REVIEW_AGENT_SYSTEM_PROMPT
    
    def process(self, state: ContentState) -> ContentState:
        """
        Process state by evaluating draft quality
        
        Args:
            state: Current ContentState
            
        Returns:
            Updated ContentState with review results
        """
        # Step 1: Extract from state
        draft = state.get("draft", "")
        topic = state.get("topic", "")
        word_count = state.get("word_count", 0)
        
        # Step 2: Build prompt
        prompt = self._build_prompt(draft, topic, word_count)
        
        try:
            # Step 3: Call Gemini
            response = self.model.generate_content(prompt)
            
            # Step 4: Parse response
            score, feedback = self._parse_response(response.text)
            
            # Step 5: Update state (6 fields)
            state["quality_score"] = score  # float
            state["review_comments"] = feedback  # list of 3 strings
            state["status"] = "review_complete"
            state["final_content"] = state["draft"]  # COPY draft unchanged
            state["next_action"] = "complete"
            state["assigned_agent"] = None
            
        except Exception as e:
            print(f"Error during review: {e}")
            # Step 6: Error handling
            state["quality_score"] = 0.0
            state["review_comments"] = ["Review failed"]
            state["status"] = "review_failed"
            state["final_content"] = state.get("draft", "")
            state["next_action"] = "complete"
            state["assigned_agent"] = None
        
        return state
    
    def _build_prompt(self, draft: str, topic: str, word_count: int) -> str:
        """
        Build complete prompt for review
        
        Args:
            draft: Blog post to review
            topic: Original topic
            word_count: Actual word count
            
        Returns:
            Complete prompt string
        """
        user_content = f'''
<content_to_review>
{draft}
</content_to_review>

<context>
Original Topic: {topic}
Word Count: {word_count}
Target: 700-800 words
</context>

Please evaluate this blog post according to your evaluation framework.'''
        
        return self.system_prompt + "\n\n" + user_content
    
    def _parse_response(self, response_text: str) -> tuple:
        """
        Parse Gemini response to extract score and feedback
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Tuple of (score, [feedback1, feedback2, feedback3])
        """
        try:
            # Extract score (look for "SCORE: XX/100")
            score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)/100', response_text)
            score = float(score_match.group(1)) if score_match else 0.0
            
            # Extract feedback comments (look for numbered items after FEEDBACK:)
            feedback = []
            
            # Find the FEEDBACK section
            if 'FEEDBACK:' in response_text:
                feedback_section = response_text.split('FEEDBACK:')[-1]
                
                # Extract numbered items (1., 2., 3.)
                # Look for patterns like "1. " followed by text
                pattern = r'[1-3]\.\s*(.+?)(?=\n[2-4]\.|RECOMMENDATION:|$)'
                matches = re.findall(pattern, feedback_section, re.DOTALL)
                
                # Clean and store feedback
                for match in matches[:3]:  # Only take first 3
                    cleaned = match.strip().replace('\n', ' ')
                    if cleaned:
                        feedback.append(cleaned)
            
            # Ensure we have exactly 3 feedback items
            while len(feedback) < 3:
                feedback.append("No additional feedback")
            
            return (score, feedback[:3])
            
        except Exception as e:
            print(f"Error parsing response: {e}")
            # If parsing fails, return defaults
            return (0.0, ["Parsing error occurred", "Unable to extract feedback", "Review incomplete"])