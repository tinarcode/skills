# ISO / IT Course Eligibility Assessment Pattern

Use this when the user asks whether a course certificate satisfies a job/application requirement such as "具 ISO20000，資訊科技範疇相關的培訓證書".

## Workflow

1. Extract the exact course page first (`web_extract` for the provided URL).
2. Search/cross-check the named standards with MiniMax MCP + Brave + Tavily.
3. Compare the *exact requirement wording* against the course title/content/certificate.
4. Separate three cases clearly:
   - **Exact standard required**: e.g. "具 ISO20000 培訓證書" → ISO 27001 course does **not** satisfy ISO20000 specifically.
   - **Alternative wording**: e.g. "ISO20000 或資訊科技範疇相關培訓證書" → ISO 27001 information security/ISMS course likely satisfies the broader IT-related certificate part.
   - **Broad IT-related certificate only** → ISO 27001 course generally qualifies as IT/cybersecurity/information-security related.
5. Provide safe wording for the user to write on forms; avoid overstating.

## Session Example: [training provider] ISO/IEC 27001:2022 Workshop

[training provider] course page extracted:
- Course: `推行 ISO/IEC 27001:2022工作坊`
- Code: `MG17.1-06-2026-C`
- Hours: `21小時 / 6節`
- Certificate: `生產力中心發出的修業證書` (requires 80% attendance + exercises/assessment pass)
- Topics: ISMS, ISO 27000 series, ISO 27001 clauses and Annex A, information security risk management, SOA, certification arrangements.

ISO official cross-check:
- ISO/IEC 20000-1 is **Information technology — Service management — Service management system requirements**. It concerns Service Management System (SMS), service planning/design/transition/delivery/improvement.
- ISO/IEC 27001 is **Information security management systems (ISMS)**. It concerns information security risk management and controls.

Conclusion pattern:
- Do **not** say "具 ISO20000 證書" for an ISO 27001 workshop.
- If the requirement allows "資訊科技範疇相關培訓證書", ISO 27001 is likely relevant because it is information security / cybersecurity / IT governance related.

Safe wording:
> 完成a regional productivity and technology transfer centre《推行 ISO/IEC 27001:2022 工作坊》修業證書，內容涵蓋資訊安全管理體系 ISMS、風險評估及 ISO 27001 控制措施。
