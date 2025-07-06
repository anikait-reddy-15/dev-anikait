PROMPT = """
You have access to structured tables containing nested fields such as CompanyInfo, CompanyDataCenter, CompanyDealMaster, CompanyFacebookDetail, CompanyFocusAreaDetail, CompanyHiringDetail, 
CompanyInstagramDetail, CompanyITPartnerDetail, CompanyLeadershipExcerpt, CompanyManagementDetail, CompanyTechStack, CompanyTwitterDetail, CompanyVendorProductDetail, 
CompanyVendorTechDetail, CompanyYoutubeDetail, IndustryBusinessTrend, IndustryITTrend, LookUpValue, PageInfo, PersonaFaceBook, PersonaInstagramProfile, PersonaLinkedinActivity, 
PersonaLinkedinPost, PersonaLinkedInProfile, PersonaMisc, PersonaTwitterProfile, PersonaTwitterTweets, PersonaUser, PersonaYoutubeProfile, SectionData, SectionInfo, 
SectionTitle, SocialMediaInfo, PersonaTitle.

Each record contains rich, specific detail on individuals, companies, technologies, or business activities.

Your Task:
Generate 100 **highly specific, contextual, SQL-answerable business and IT strategy questions** from these records. These questions should help users:

- Identify Data Scientists, their responsibilities, and how they influence business or technology decisions.
- Understand company-wide IT priorities, technology investments, leadership viewpoints, and strategic areas of focus.
- Discover competitive positioning via deals, technology stack shifts, and industry benchmarks.
- Correlate organizational behavior (e.g., hiring, leadership changes, social media posts) with technology strategy.
- Use nested fields where available (e.g., Speaks.Topic, Deals.Vendor, PersonaLinkedinPost.PostContent, etc.)

Rules:

1. Every question must use **1 to 5 tables randomly** — vary the combinations across questions.
2. No two questions should rely mainly on the same table — spread usage across the schema.
3. Questions must be **natural-language**, **clear**, and **directly answerable by SQL** — no creative writing prompts.
4. Use real, specific schema fields: companies, personas, technologies, deals, budgets, org changes, social activity.
5. Always reference **nested fields** wherever relevant (e.g., PersonaLinkedinPost.PostContent, CompanyLeadershipExcerpt.Speaks.Topic).
6. Always blend tables where meaningful – e.g., PersonaLinkedinPost + CompanyTechStack + CompanyFocusAreaDetail.
7. End every question with the tables used in this format: (Tables: Table1, Table2, Table3).

Example Questions:

1. Which companies have mentioned adopting Snowflake in their tech stack in the past 3 months? (Tables: CompanyTechStack, CompanyInfo)

2. Who are the data science leaders at companies that have increased their IT partner count in the last 6 months? (Tables: PersonaUser, PersonaTitle, CompanyITPartnerDetail)

3. Which companies in the financial sector signed analytics vendor deals after major leadership changes? (Tables: CompanyDealMaster, CompanyVendorTechDetail, CompanyLeadershipExcerpt)

4. What are the most common technologies used by companies that recently posted job openings for data engineering roles? (Tables: CompanyHiringDetail, CompanyTechStack)

5. Which personas mentioned AI or machine learning in their LinkedIn posts and are associated with companies investing in GPU infrastructure? (Tables: PersonaLinkedinPost, PersonaUser, CompanyTechStack)

6. What companies had both an increase in Twitter engagement and a shift in their focus to digital transformation this quarter? (Tables: CompanyTwitterDetail, CompanyFocusAreaDetail)

7. Which vendors are supplying cybersecurity solutions to healthcare companies with a recent rise in IT hiring? (Tables: CompanyVendorTechDetail, CompanyInfo, CompanyHiringDetail)

8. What technologies are commonly adopted by companies that recently promoted a new CTO or Head of Engineering? (Tables: CompanyManagementDetail, CompanyTechStack)

9. Which companies published YouTube content about cloud migration and also updated their data center footprint in the last year? (Tables: CompanyYoutubeDetail, CompanyDataCenter)

10. Which personas with “Director of Data Science” titles have engaged with competitor posts on Twitter in the last 30 days? (Tables: PersonaTwitterProfile, PersonaTitle, PersonaTwitterTweets)
"""
