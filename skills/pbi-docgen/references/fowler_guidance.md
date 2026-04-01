# Fowler's Modern English Usage - Prompt Rules

These rules are embedded in every section generation prompt to enforce clear, direct English prose.

## Rules

1. **Prefer active voice.** "The report filters data" not "Data is filtered by the report."
2. **No nominalization padding.** "Using" not "the utilization of." "Analyzing" not "the analysis of."
3. **No corporate filler.** Never use: leverage, synergy, optimize, utilize, facilitate, streamline, robust, scalable, holistic, best-in-class, cutting-edge, world-class.
4. **Keep sentences under 25 words.** Split long sentences into two.
5. **Be direct.** State what something does, not what it "aims to" or "seeks to" do.
6. **Prefer concrete nouns over abstract ones.** "The table stores customer records" not "The data storage mechanism maintains entity information."
7. **Use plain connectives.** "because" not "due to the fact that." "so" not "as a consequence of."

## Application

Include these rules verbatim (or the Jinja2 include of fowler_rules.j2) at the top of every section generation prompt. The LLM must treat them as hard constraints, not suggestions.
