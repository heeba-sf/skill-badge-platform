# Competency: SQL Injection

## Level 1 — Identification
The submission identifies that a SQL injection vulnerability exists in the target application (e.g., correctly points out the injectable parameter or input field).

## Level 2 — Exploitation
The submission demonstrates a working exploit: a payload or tool usage (e.g., sqlmap, manual UNION-based injection) that successfully extracts or manipulates data.

## Level 3 — Impact & Remediation
The submission explains the real-world impact of the vulnerability (e.g., data exposure, authentication bypass) AND proposes a valid remediation (e.g., parameterized queries, input sanitization, least-privilege DB accounts).

## Scoring rule
- If the submission does not meet Level 1 criteria, mastery level = "Not Demonstrated"
- Award the highest level fully satisfied by the submission
- A submission can reference multiple levels but must clearly satisfy all criteria of a level to be scored at that level

# Competency: Information Gathering / Enumeration

## Level 1 — Basic Recon
The submission shows basic reconnaissance was performed (e.g., identifying open ports, running a scan with nmap, listing visible services or technologies on the target).

## Level 2 — Directed Enumeration
The submission goes further: enumerating specific details from the recon results (e.g., using gobuster/dirb to find hidden directories, identifying software versions, discovering user accounts or subdomains).

## Level 3 — Actionable Findings
The submission connects the enumeration results to a potential attack path or risk (e.g., "this outdated service version has a known CVE" or "this hidden directory exposes an admin panel"), even without fully exploiting it.

## Scoring rule
- If the submission does not meet Level 1 criteria, mastery level = "Not Demonstrated"
- Award the highest level fully satisfied by the submission

# Competency: Python Fundamentals

## Level 1 — Basic Syntax
The submission demonstrates correct use of basic Python syntax (variables, conditionals, loops) to solve a simple problem.

## Level 2 — Functions & Logic
The submission organizes code into functions, handles edge cases (e.g., empty input, invalid values), and shows clear logical structure.

## Level 3 — Best Practices
The submission follows good coding practices (meaningful variable names, comments/docstrings, efficient logic) and may include basic error handling (try/except).

## Scoring rule
- If the submission does not meet Level 1 criteria, mastery level = "Not Demonstrated"
- Award the highest level fully satisfied by the submission