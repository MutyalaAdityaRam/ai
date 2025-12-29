"""
Resume Generation & Tailoring Agent
Generates structured resumes with STRICT JSON schema for HTML→PDF generation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_client import llm
from typing import Dict, List, Any, Optional
import json


class ResumeAgent:
    """
    Professional Resume Content Generation Agent
    
    Responsibilities:
    1. Generate resume CONTENT ONLY following STRICT JSON schema
    2. Analyze job role / job description
    3. Select ONLY relevant skills and projects from user profile
    4. Create ATS-friendly, recruiter-ready content
    5. Use strong action verbs and measurable impact
    """
    
    # STRICT SYSTEM PROMPT
    SYSTEM_PROMPT = """You are a professional resume content generation agent.

Your task is to generate resume CONTENT ONLY.
You MUST follow all rules strictly.

======================
CRITICAL RULES
======================
1. Output ONLY valid JSON
2. Follow the EXACT JSON schema provided
3. Do NOT add, remove, or rename any fields
4. Do NOT include formatting, styling, layout, colors, icons, or alignment instructions
5. Do NOT invent skills or projects
6. Use ONLY skills and projects provided in the user profile
7. Select ONLY skills and projects that are RELEVANT to the given job role or job description
8. Exclude unrelated or weakly relevant skills and projects
9. Bullet points must be concise, professional, and achievement-oriented
10. Use strong action verbs and measurable impact where possible
11. Keep the resume professional, ATS-friendly, and recruiter-ready

======================
RESUME JSON SCHEMA (STRICT - DO NOT DEVIATE)
======================
{
  "header": {"name": "", "title": ""},
  "contact": {"phone": "", "email": "", "address": "", "website": "", "linkedin": ""},
  "summary": "",
  "skills": [{"name": "", "level": 0}],
  "projects": [{"title": "", "tech_stack": [], "points": []}],
  "experience": [{"role": "", "company": "", "location": "", "duration": "", "points": []}],
  "education": [{"degree": "", "institution": "", "year": "", "details": ""}]
}

======================
OUTPUT REQUIREMENTS
======================
- Skills level must be 0-100 integer
- Select ONLY skills relevant to the job role
- Select ONLY projects that demonstrate required competencies
- Do NOT repeat content across sections
- If experience is limited, emphasize projects strongly"""
    
    def __init__(self):
        self.name = "ResumeAgent"
    
    def generate_structured_resume(
        self, 
        user_profile: Dict,
        skills: List[Dict],
        experience: List[Dict],
        education: List[Dict],
        target_role: str,
        job_description: Optional[str] = None,
        projects: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured resume data following STRICT JSON schema
        
        Args:
            user_profile: User's profile information
            skills: List of user skills with proficiency
            experience: Work experience list
            education: Education history
            target_role: Target job role
            job_description: Optional JD for tailoring
            projects: User's projects list
        
        Returns:
            Structured resume JSON following strict schema
        """
        # Format skills for prompt
        skills_list = []
        for skill in (skills or []):
            skills_list.append({
                'name': skill.get('skill_name', skill.get('name', '')),
                'level': skill.get('level', 50),
                'category': skill.get('category', 'general')
            })
        
        # Format projects for prompt
        projects_list = []
        if projects:
            for proj in projects:
                projects_list.append({
                    'title': proj.get('title', proj.get('name', '')),
                    'description': proj.get('description', ''),
                    'technologies': proj.get('technologies', proj.get('tech_stack', [])),
                    'highlights': proj.get('highlights', proj.get('points', []))
                })
        
        # Format experience for prompt
        experience_list = []
        for exp in (experience or []):
            experience_list.append({
                'role': exp.get('role', exp.get('title', '')),
                'company': exp.get('company', ''),
                'location': exp.get('location', ''),
                'duration': exp.get('duration', ''),
                'points': exp.get('points', exp.get('achievements', []))
            })
        
        # Format education for prompt
        education_list = []
        for edu in (education or []):
            education_list.append({
                'degree': edu.get('degree', ''),
                'institution': edu.get('institution', ''),
                'year': str(edu.get('year', edu.get('graduation_year', ''))),
                'details': edu.get('details', edu.get('gpa', ''))
            })
        
        prompt = f"""Generate a professional resume following the STRICT JSON schema.

======================
INPUT DATA
======================

## Target Role
{target_role}

## Job Description
{job_description if job_description else 'Not provided - tailor to target role'}

## User Profile
- Full Name: {user_profile.get('name', user_profile.get('full_name', 'Unknown'))}
- Email: {user_profile.get('email', '')}
- Phone: {user_profile.get('phone', '')}
- Location/Address: {user_profile.get('location', user_profile.get('address', ''))}
- Website: {user_profile.get('website', user_profile.get('portfolio', ''))}
- LinkedIn: {user_profile.get('linkedin', '')}
- Career Goal: {user_profile.get('career_goal', target_role)}

## Available Skills (SELECT ONLY RELEVANT ONES)
{json.dumps(skills_list, indent=2)}

## Available Projects (SELECT ONLY RELEVANT ONES)
{json.dumps(projects_list, indent=2) if projects_list else '[]'}

## Experience History
{json.dumps(experience_list, indent=2) if experience_list else '[]'}

## Education
{json.dumps(education_list, indent=2) if education_list else '[]'}

======================
INSTRUCTIONS
======================
1. Set header.name to the user's full name
2. Set header.title to the target role: "{target_role}"
3. Write a compelling 2-3 sentence professional summary
4. Select ONLY skills relevant to {target_role} (include level as 0-100 integer)
5. Select ONLY projects that demonstrate {target_role} competencies
6. Rewrite experience bullet points with strong action verbs
7. Output ONLY the JSON following the STRICT schema

Generate the resume JSON now:"""
        
        result = llm.call_json(prompt, self.SYSTEM_PROMPT, temperature=0.3)
        
        if result:
            # Validate and clean the result
            cleaned_result = self._validate_and_clean(result, user_profile)
            
            return {
                "agent": self.name,
                "status": "success",
                "resume_data": cleaned_result,
                "target_role": target_role,
                "generated_at": None
            }
        else:
            return {
                "agent": self.name,
                "status": "error",
                "message": "Failed to generate resume content",
                "resume_data": None
            }
    
    def _validate_and_clean(self, data: Dict, user_profile: Dict) -> Dict:
        """
        Validate and clean the LLM output to ensure strict schema compliance
        """
        # Ensure required structure
        cleaned = {
            "header": {
                "name": data.get('header', {}).get('name', user_profile.get('name', '')),
                "title": data.get('header', {}).get('title', '')
            },
            "contact": {
                "phone": data.get('contact', {}).get('phone', user_profile.get('phone', '')),
                "email": data.get('contact', {}).get('email', user_profile.get('email', '')),
                "address": data.get('contact', {}).get('address', user_profile.get('location', '')),
                "website": data.get('contact', {}).get('website', user_profile.get('website', '')),
                "linkedin": data.get('contact', {}).get('linkedin', user_profile.get('linkedin', ''))
            },
            "summary": data.get('summary', ''),
            "skills": [],
            "projects": [],
            "experience": [],
            "education": []
        }
        
        # Clean skills
        for skill in data.get('skills', []):
            if isinstance(skill, dict):
                cleaned['skills'].append({
                    "name": skill.get('name', ''),
                    "level": int(skill.get('level', 50))
                })
            elif isinstance(skill, str):
                cleaned['skills'].append({"name": skill, "level": 70})
        
        # Clean projects
        for proj in data.get('projects', []):
            if isinstance(proj, dict):
                cleaned['projects'].append({
                    "title": proj.get('title', proj.get('name', '')),
                    "tech_stack": proj.get('tech_stack', proj.get('technologies', [])),
                    "points": proj.get('points', proj.get('highlights', []))
                })
        
        # Clean experience
        for exp in data.get('experience', []):
            if isinstance(exp, dict):
                cleaned['experience'].append({
                    "role": exp.get('role', exp.get('title', '')),
                    "company": exp.get('company', ''),
                    "location": exp.get('location', ''),
                    "duration": exp.get('duration', ''),
                    "points": exp.get('points', exp.get('achievements', []))
                })
        
        # Clean education
        for edu in data.get('education', []):
            if isinstance(edu, dict):
                cleaned['education'].append({
                    "degree": edu.get('degree', ''),
                    "institution": edu.get('institution', ''),
                    "year": str(edu.get('year', '')),
                    "details": edu.get('details', '')
                })
        
        return cleaned
    
    def tailor_to_job_description(
        self,
        existing_resume: Dict,
        job_description: str,
        target_role: str,
        target_company: str = ""
    ) -> Dict[str, Any]:
        """
        Tailor an existing resume to a specific job description
        
        Args:
            existing_resume: Current resume JSON data
            job_description: Target job description
            target_role: Target role title
            target_company: Target company name
        
        Returns:
            Tailored resume following strict schema
        """
        prompt = f"""Tailor this existing resume to the job description below.

======================
CURRENT RESUME
======================
{json.dumps(existing_resume, indent=2)}

======================
TARGET JOB
======================
Role: {target_role}
Company: {target_company if target_company else 'Not specified'}
Description: {job_description}

======================
INSTRUCTIONS
======================
1. Keep the same contact information
2. Update header.title to match the target role
3. Rewrite summary to emphasize relevant experience for this specific role
4. Reorder and emphasize skills that match the JD (keep level as 0-100)
5. Rewrite experience bullet points to highlight relevant achievements
6. Prioritize projects that demonstrate required competencies
7. Remove or de-emphasize irrelevant content
8. Output ONLY the JSON, following the STRICT schema

Generate the tailored resume JSON:"""
        
        result = llm.call_json(prompt, self.SYSTEM_PROMPT, temperature=0.3)
        
        if result:
            cleaned = self._validate_and_clean(result, {})
            return {
                "agent": self.name,
                "status": "success",
                "resume_data": cleaned,
                "target_role": target_role,
                "target_company": target_company,
                "tailored": True
            }
        else:
            return {
                "agent": self.name,
                "status": "error",
                "message": "Failed to tailor resume",
                "resume_data": None
            }
    
    def analyze_resume_match(
        self,
        resume_data: Dict,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Analyze how well a resume matches a job description
        
        Args:
            resume_data: Resume JSON data
            job_description: Job description to match against
        
        Returns:
            Match analysis with score and recommendations
        """
        prompt = f"""Analyze how well this resume matches the job description.

## Resume
{json.dumps(resume_data, indent=2)}

## Job Description
{job_description}

Provide analysis in this JSON format:
{{
    "match_score": <0-100>,
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "matching_experience": ["relevant experience 1", "relevant experience 2"],
    "gaps": ["gap 1", "gap 2"],
    "recommendations": [
        "specific recommendation 1",
        "specific recommendation 2"
    ],
    "keywords_present": ["keyword1", "keyword2"],
    "keywords_missing": ["keyword1", "keyword2"],
    "overall_assessment": "brief assessment"
}}"""
        
        result = llm.call_json(prompt, self.SYSTEM_PROMPT, temperature=0.2)
        
        if result:
            return {
                "agent": self.name,
                "status": "success",
                "analysis": result
            }
        else:
            return {
                "agent": self.name,
                "status": "error",
                "message": "Failed to analyze resume match"
            }
    
    def suggest_resume_improvements(
        self,
        resume_data: Dict,
        target_role: str = "",
        feedback_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Suggest improvements to make the resume more effective
        
        Args:
            resume_data: Current resume JSON
            target_role: Target role
            feedback_history: Past rejection feedback
        
        Returns:
            List of improvement suggestions
        """
        feedback_text = ""
        if feedback_history:
            feedback_text = "\n".join([
                f"- {fb.get('company', 'Unknown')}: {fb.get('message', fb.get('feedback', ''))}"
                for fb in feedback_history[:5]
            ])
        
        prompt = f"""Review this resume for a {target_role if target_role else 'professional'} position and suggest improvements.

## Resume
{json.dumps(resume_data, indent=2)}

{f'## Past Rejection Feedback\\n{feedback_text}' if feedback_text else ''}

Provide suggestions in this JSON format:
{{
    "summary_improvements": ["suggestion 1", "suggestion 2"],
    "skills_to_add": ["skill 1", "skill 2"],
    "skills_to_remove": ["skill that's not relevant"],
    "experience_improvements": [
        {{
            "current": "current bullet point",
            "improved": "improved bullet point with metrics"
        }}
    ],
    "project_improvements": ["suggestion 1"],
    "formatting_tips": ["tip 1", "tip 2"],
    "keywords_to_add": ["keyword 1", "keyword 2"],
    "overall_score": <0-100>,
    "priority_actions": ["action 1", "action 2", "action 3"]
}}"""
        
        result = llm.call_json(prompt, self.SYSTEM_PROMPT, temperature=0.3)
        
        if result:
            return {
                "agent": self.name,
                "status": "success",
                "suggestions": result
            }
        else:
            return {
                "agent": self.name,
                "status": "error",
                "message": "Failed to generate improvement suggestions"
            }


# Create singleton instance
resume_agent = ResumeAgent()
