PROMPT = f"""
You have access to structured tables containing nested fields such as CompanyInfo, CompanyDataCenter, CompanyDealMaster, CompanyFacebookDetail, CompanyFocusAreaDetail, CompanyHiringDetail, 
CompanyInstagramDetail, CompanyITPartnerDetail, CompanyLeadershipExcerpt, CompanyManagementDetail, CompanyTechStack, CompanyTwitterDetail, CompanyVendorProductDetail, 
CompanyVendorTechDetail, CompanyYoutubeDetail, IndustryBusinessTrend, IndustryITTrend, LookUpValue, PageInfo, PersonaFaceBook, PersonaInstagramProfile, PersonaLinkedinActivity, 
PersonaLinkedinPost, PersonaLinkedInProfile, PersonaMisc, PersonaTwitterProfile, PersonaTwitterTweets, PersonaUser, PersonaYoutubeProfile, SectionData, SectionInfo, 
SectionTitle, SocialMediaInfo, PersonaTitle.

Each record contains rich, specific detail on individuals, companies, technologies, or business activities.

Your Task:
Generate **150 unique, highly specific, SQL-answerable business and IT strategy questions** using this data. These questions should help users:

- Identify Data Scientists, their responsibilities, and how they influence business or technology decisions.
- Understand company-wide IT priorities, technology investments, leadership viewpoints, and strategic areas of focus.
- Discover competitive positioning via deals, technology stack shifts, and industry benchmarks.
- Correlate organizational behavior (e.g., hiring, leadership changes, social media posts) with technology strategy.
- Use nested fields where available (e.g., Speaks.Topic, Deals.Vendor, PersonaLinkedinPost.PostContent, etc.)

Rules:
1. Generate exactly **150 questions**.
2. **Do NOT reuse or regenerate** the following example questions:
   - “Which companies have mentioned adopting Snowflake in their tech stack…”
   - “Who are the data science leaders at companies that have increased…”
   - “Which companies in the financial sector signed analytics vendor deals…”
   - “What are the most common technologies used by companies that recently posted job openings…”
   - “Which personas mentioned AI or machine learning in their LinkedIn posts…”
   - “What companies had both an increase in Twitter engagement and a shift…”
   - “Which vendors are supplying cybersecurity solutions to healthcare companies…”
   - “What technologies are commonly adopted by companies that recently promoted a new CTO…”
   - “Which companies published YouTube content about cloud migration…”
   - “Which personas with 'Director of Data Science' titles have engaged with competitor posts…”

3. Each question must use **different tables**, randomly chosen across the schema.
4. Ensure table diversity — avoid repeating the same primary table across many questions.
5. Every question must be in **natural-language**, clear, and directly answerable via SQL — no abstract or vague prompts.
6. Use **real field references**, including nested ones like: 
   - `CompanyLeadershipExcerpt.Speaks.Topic`
   - `CompanyDealMaster.Deals.Vendor`
   - `PersonaLinkedinPost.PostContent`
   - `CompanyTechStack.Technology`
7. Where possible, **blend tables** meaningfully. Example: Hiring + Tech Stack, Social Media + Strategic Focus, Leadership + Vendor Deals, etc.
8. Every question should end with a table usage label in this format:  
   **(Tables: Table1, Table2, Table3)** — list only the tables used for that question.
9. DO NOT generate questions that:
   - Ask for writing memos, summaries, articles, or documents.
   - Require subjective reasoning or external knowledge.
   - Are open-ended, like "Why", "How should", "Write a report", or "Describe...".
   GOOD examples:
   - Which companies adopted cloud technologies after 2023?
   - What are the top 5 industries hiring for AI roles?
   - Which leaders posted most frequently on LinkedIn?
   BAD examples (avoid completely):
   - Write a memo about tech adoption.
   - Give me a summary of industry trends.
   - Generate a press release or document.

Example Output Format:

1. Which companies have mentioned adopting Snowflake in their tech stack in the past 3 months? (Tables: CompanyTechStack, CompanyInfo)

2. Who are the data science leaders at companies that have increased their IT partner count in the last 6 months? (Tables: PersonaUser, PersonaTitle, CompanyITPartnerDetail)

... (continue to 150)
"""