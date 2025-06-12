PROMPT = """
## Context:
You have access to structured tables containing nested fields like Personas, Org Hierarchies, Technology Investments, Business Priorities, Events, Articles, Speeches, Pitches, Deals, Tech Stacks, IT Budgets, and Communication guidelines.
Each record can have detailed information on individuals, organizations, technologies, or business activities.

## Table Names:
{table_names}

## Column Names:
{column_names}

## For each question:
    * Mention in brackets at the end: (Tables: Table1, Table2, Table3, etc.)

## Task:
Generate 6-8, contextual business and IT strategy questions that blend context across 2-4 tables randomly, wherever meaningful, no sub questions and no questions should be similar to each other.
Generate highly specific, contextual business and IT strategy questions from the table records. These questions should help the user to:
- Identify Data Scientists, their responsibilities, and how they influence technology or business decisions within companies.
    * Sound simple, natural, and human — avoid robotic or overly formal phrasing.
    * Understand company-wide IT priorities, technology investments, leadership views, and strategic focus areas.
    * Draft communication strategies such as email pitches or meeting scripts aligned with persona behaviors and org priorities.
    * Discover competition landscape from deals, tech triggers, vendor ecosystems.
    * Always drill into nested fields like Speaks.Topic, Communication.Call, Event.News, Deals.Vendor if available.
    * Include 1-2 actionable prompts — like drafting an email, a memo, a write-up, or a slide deck based on the company's IT priorities or leadership changes.

## Rules:
    * Always use actual company names, personas, technologies, deals, budgets, or priorities from the records.
    * Always refer to persona names, designations, and company names exactly as recorded in the data.
    * When needed, drill into nested fields like Speaks.Professional.Topic, Communication.Call, Event.News, Deals.Vendor.
    * Form questions that directly mention technologies, personas, IT priorities, investments, events, or competitor information.
    * Avoid generic, template questions. Make each question deeply contextual to the available data.
    * Always use actual company names, personas, technologies, deals, budgets, or priorities from the records.
    * Focus questions around leadership moves, tech adoption, IT budgets, strategic events, social media activity, and partnerships.
    * Drill down into nested fields like Speaks.Topic, Communication.Call, Deals.Vendor if available.
    * Do NOT generate generic templates. Keep every question tightly bound to the provided data.
    * If possible, blend multiple signals (like leadership + tech investment) into a single insightful question.

## Example:
1. Which companies are investing in <Technology name-Cloud>?
2. Who is responsible for <Technology name - cloud> in <Company Name>?
3. What are the strategic IT priorities of <Company Name>?
4. Can you draft an email pitch for the <CEO> of <Company Name> which aligns with their strategic business and IT priorities?
5. Who are <my-Company Name> key competitors in <target account/prospect - Company Name>?
6. What is the <Company Name> budget on <Analytics>?
7. Give me a list of IT projects or investments or initiatives or partnerships of the <Company Name> in the last 2 months?
8. Has the <Company Name> mentioned <competitor name> on its social media handle?
9. What are the events that the <Company Name> attends?
10. Which companies have seen an <Business Trigger - Org Change/M&A> in the last 3 months?
"""