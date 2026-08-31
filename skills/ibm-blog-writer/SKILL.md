---
name: ibm-blog-writer
description: Write IBM leadership blog entries from meeting transcripts, interviews, or notes. Use when asked to write, draft, or create a blog post, thought leadership article, or leadership perspective piece for IBM. Produces compelling 1000-word blog entries in IBM's standard format with proper author bios. Follows IBM style guidelines including British English spelling.
---

# IBM Blog Writing Skill

Transform meeting transcripts, interviews, or notes into compelling IBM leadership blog entries.

## Inputs Required

Before writing, collect:
- **Meeting transcript or source material**: The content to distil into a blog
- **Author(s)**: Names and roles of the blog authors
- **Author bios**: Brief professional backgrounds (2-3 sentences each)
- **Style**: STANDARD (default) or specify alternative

## Context Management

ALWAYS write output to `./tmp/ibm-blog-writer.md` immediately after generation. This prevents context saturation when chaining with other skills. Only copy final deliverables to `./outputs` at completion.

## Blog Structure

### 1. Opening Hook (1-2 paragraphs)

Set the scene and establish relevance:
- Start with a compelling statement about the topic's importance
- Introduce the authors and their perspective
- Preview the key themes

### 2. Pull Quote (optional)

Include a notable quote from a relevant authority figure:
- Format in italics or as a block quote
- Include attribution with title

### 3. Body Sections (3-5 sections)

Each section should:
- Have a clear, descriptive heading
- Focus on one key theme or argument
- Progress logically from the previous section
- Include specific examples, data, or case studies where available

**Typical section flow:**
1. Problem/Challenge identification
2. Analysis of the situation
3. Lessons or insights
4. Technology/solution perspective
5. IBM's role and capabilities
6. Call to action or forward look

### 4. Conclusion

- Summarise the key message
- End with a forward-looking statement or call to action
- Include any relevant event links or next steps

### 5. Author Bios

For each author:
```
About the authors
[Name] is [Role] at IBM [Division/Region]. [2-3 sentences on background and expertise].
```

## Writing Guidelines

### Tone and Voice
- Confident and authoritative, not salesy
- Thoughtful and analytical
- Accessible to business and technical audiences
- British English throughout

### Language Standards

**Always use:**
- British English spelling (realise, colour, programme, defence)
- Active voice
- Contractions for conversational tone
- Specific examples over generalisations

**Avoid:**
- Americanisms
- Jargon without explanation
- Overused phrases: "cutting-edge", "game-changing", "best-in-class"
- First person plural ("we") unless directly quoting
- Non-inclusive language (see style guide for details on avoiding bias)

**For IBM style details:**
- Quick reference: `references/ibm-style-guide.md` (condensed essentials)
- Comprehensive guide: `references/ibm-style-documentation.md` (full IBM Style documentation for detailed lookups)

### Formatting

- **Headings**: Sentence-style capitalisation
- **Numbers**: Use numerals (not words)
- **Dates**: International format (19 December 2022)
- **Dashes**: Em dash for pauses (no spaces), en dash for ranges
- **Commas**: No Oxford comma unless needed for clarity

## Quality Checklist

Before finalising:
- [ ] Approximately 1000 words (900-1100 acceptable)
- [ ] Clear opening hook that establishes relevance
- [ ] 3-5 well-structured body sections with headings
- [ ] Logical flow from problem to analysis to solution
- [ ] Specific examples, data, or case studies included
- [ ] IBM's perspective and capabilities positioned naturally (not as hard sell)
- [ ] British English spelling throughout
- [ ] Author bios included at the end
- [ ] Call to action or forward-looking conclusion
- [ ] Follows IBM style guide conventions

## Example Output Structure

```
[Opening hook - 1-2 paragraphs establishing context and authors]

[Optional pull quote from authority figure]

[Section heading 1]
[2-3 paragraphs on first theme]

[Section heading 2]
[2-3 paragraphs on second theme]

[Section heading 3]
[2-3 paragraphs on third theme]

[Section heading 4 - IBM perspective]
[2-3 paragraphs on how IBM/technology addresses the challenge]

[Concluding section - forward look or call to action]

About the authors
[Author 1 name] is [role]. [Background and expertise].
[Author 2 name] is [role]. [Background and expertise].
```

## Section Heading Examples

Good headings are descriptive and engaging:
- "Replacing process with urgency"
- "Lessons from Ukraine"
- "Changing a mindset"
- "Technology in action"
- "Meeting of minds"
- "Fragmentation and Financial Constraints"
- "How IBM Supports the Government's Digital Ambitions"
- "Transforming Government Together"

## Integration with Other Skills

This skill can work with:
- **ibm-bid-strategy-and-capabilities-2026**: Reference IBM capabilities when positioning IBM's role in addressing challenges
- **ibm-bid-customer-stories**: Include relevant case studies or customer examples as proof points
