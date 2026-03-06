# Scenario: Home Energy Audit

## Question

"I live in a 1960s ranch house in Colorado. My energy bills are $350/month. What should I prioritize to cut costs — insulation, windows, heat pump, solar, or something else? I have about $15k to spend."

## Type

Practical/technical recommendation (constrained budget)

## Expected Role Categories

- Technical/building science
- Financial/ROI analysis
- Possibly: local context (Colorado climate, utility incentives)
- Possibly: contractor/implementation perspective

## What This Tests

- Do agents work with the actual constraints ($15k budget, 1960s ranch, Colorado)?
- Does someone prioritize by ROI rather than listing everything?
- Is the financial analysis specific (estimated savings, payback period) or hand-wavy?
- Does the team produce a ranked recommendation, not just an info dump?

## Role Rubric Overrides

- Financial roles: must include estimated numbers (even ranges). "This will save money" without quantification is a Fail on Specificity.
- Technical roles: must account for the 1960s construction and Colorado climate specifically.
