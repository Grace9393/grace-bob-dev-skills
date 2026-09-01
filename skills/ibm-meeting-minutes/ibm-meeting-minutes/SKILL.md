---
name: ibm-meeting-minutes
description: Convert meeting transcripts or rough notes into professional, structured meeting minutes. Use this skill when users provide raw meeting transcripts, audio/video transcriptions, rough notes, or unstructured meeting content and ask to create formal meeting minutes, organize meeting notes, capture action items from a meeting, or format meeting documentation. Also triggers when users mention "meeting minutes", "meeting notes template", "action items from meeting", or ask to "clean up meeting notes".
---

# Meeting Minutes Creator

Convert raw meeting transcripts or rough notes into professional, well-structured meeting minutes.

## Process Overview

1. **Analyze the input** - Identify meeting metadata, participants, topics, decisions, and action items
2. **Load the template** - Use the standardized template from `assets/meeting_minutes_template.md`
3. **Populate the template** - Extract and organize information into appropriate sections
4. **Create the final document** - Generate a clean, professional meeting minutes document

## Step-by-Step Instructions

### Step 1: Analyze the Input

Read through the transcript or rough notes and identify:

- **Meeting metadata**: date, time, duration, location/platform
- **Participants**: who attended, who was absent, any guests
- **Agenda topics**: main discussion points
- **Key decisions**: what was decided and by whom
- **Action items**: tasks, owners, deadlines
- **Open questions**: unresolved items or parking lot topics
- **Note taker**: who recorded the meeting (if mentioned)

### Step 2: Load the Template

Copy the template from `assets/meeting_minutes_template.md` as your starting point. This provides the standard structure that should be used for all meeting minutes.

### Step 3: Populate the Template

Fill in each section based on your analysis:

**Meeting Information Section:**
- Extract or infer date, time, duration
- Note the meeting type (team sync, project review, etc.)
- List location or video platform used

**Attendees Section:**
- List all participants with roles/titles if available
- Separate into Present, Absent/Apologies, and Guests
- If roles aren't provided in the input, omit them rather than guessing

**Key Decisions & Action Items:**
- **Decisions**: Extract any explicit decisions made, along with context and who approved
- **Action Items Table**: Format as a table with Action | Owner | Deadline | Status columns
- Be specific about tasks - avoid vague language
- If deadlines aren't mentioned, note "TBD" rather than omitting

**Discussion Summary:**
- Organize by agenda topics or themes
- For each topic, capture:
  - Who led/presented
  - 3-5 key points discussed (not verbatim, but substance)
  - Different perspectives raised
  - Outcome or next steps
- Focus on substance, not transcription

**Parking Lot:**
- List items that need follow-up but weren't resolved
- Questions that need more information
- Topics deferred to future meetings

**Next Meeting & Additional Notes:**
- Fill in if this information is discussed
- Otherwise, mark as "TBD" or remove the section

### Step 4: Create the Document

Save the completed minutes as a markdown file with a descriptive filename like `meeting_minutes_YYYY-MM-DD.md` or `[meeting_type]_minutes_YYYY-MM-DD.md`.

Place the file in `./tmp/user-data/outputs/` so the user can download it.

## Quality Standards

**Clarity over completeness:** Better to have concise, clear notes than verbatim transcription.

**Action items must be specific:** "John to follow up" is too vague. "John to email vendor quotes by Friday 2/2" is specific.

**Professional tone:** Remove filler words, informal language, and off-topic tangents. Keep the professional substance.

**Attribution:** When important, note who said what, who made decisions, who raised concerns.

**Consistent formatting:** Follow the template structure consistently.

## Handling Edge Cases

**If information is missing:**
- Use [TBD] or [Not specified] in brackets
- Don't invent information
- If a section has no content, keep the header but note "None" or remove the section entirely

**If the input is very rough:**
- Do your best to extract the key points
- Focus on decisions and action items - these are most critical
- Let the user know if the input was incomplete and offer to refine with more information

**If asked to modify existing minutes:**
- Read the existing minutes file
- Make the requested changes while maintaining format consistency
- Preserve all other content unchanged

## Output Format

Always output as a markdown (.md) file for easy editing and compatibility. If the user specifically requests Word format (.docx), use the docx skill to convert the markdown to a formatted Word document.
