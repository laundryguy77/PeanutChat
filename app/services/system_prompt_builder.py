"""Centralized system prompt construction with memory, profile, and tool instructions."""
from typing import List, Optional, Dict, Any


class SystemPromptBuilder:
    """Builds system prompts with memory context, profile context, and tool instructions."""

    PROFILE_INSTRUCTIONS = """
## USER PROFILE SYSTEM

You have access to a comprehensive user profile system. Use it to personalize your responses.

### Profile Tools Available:
- **user_profile_read**: Read profile sections at conversation start
- **user_profile_update**: Update fields when user states preferences
- **user_profile_log_event**: Log notable positive/negative events
- **user_profile_query**: Ask questions about the user's profile

### When to Use Profile Tools:
1. **Conversation Start**: Read relevant sections (identity, communication, pet_peeves, boundaries)
2. **User States Preference**: Update profile with user_profile_update
3. **Significant Event**: Log praise, frustration, task completion with user_profile_log_event
4. **Need Context**: Query profile for user preferences

### Sensitive Sections (require user enablement):
- sexual_romantic, substances_health, dark_content, private_self, financial_context
- Only access these when user explicitly enables or initiates discussion
"""

    TOOL_INSTRUCTIONS = """
## AVAILABLE TOOLS

### Memory Tools
- **add_memory**: Store important information about the user
  - Categories: 'preference' (likes/dislikes), 'personal' (name, job, location), 'topic' (projects, interests), 'instruction' (how they like things done)
  - Importance: 1-10 scale (name=10, preferences=7, casual=3)
  - CRITICAL: If user says "remember this", "don't forget", "keep in mind" -> use add_memory IMMEDIATELY

- **query_memory**: Search what you know about the user
  - Use semantic queries like "user's coding preferences" or "projects user is working on"

### Information Tools
- **web_search**: Search the web for current information
- **browse_website**: Visit a specific URL
- **search_conversations**: Search past conversations with this user
- **search_knowledge_base**: Search user's uploaded documents

## INFORMATION PRIORITY (highest to lowest)
1. User's explicit statements in this conversation
2. Memory (retrieved context about this user)
3. Attached files in this conversation
4. Knowledge base (uploaded documents)
5. Previous conversations
6. Web search results
7. Your training knowledge (may be outdated)

## TOOL USAGE RULES
1. **Memory Priority**: Check memory before answering questions about the user
2. **Active Learning**: When you discover important info (name, preferences), add it to memory
3. **No Duplicates**: Don't add information already in memory
4. **Explicit Requests**: When user asks to remember something, add it immediately
"""

    def build_prompt(
        self,
        persona: Optional[str] = None,
        memory_context: Optional[List[Dict[str, Any]]] = None,
        profile_context: Optional[Dict[str, Any]] = None,
        user_name: Optional[str] = None,
        has_tools: bool = True,
        has_vision: bool = False
    ) -> str:
        """Build the complete system prompt."""
        sections = []

        # Base identity
        sections.append("You are a helpful AI assistant with access to tools and persistent memory about the user.")

        # User greeting - prefer profile name over memory name
        effective_name = user_name
        if profile_context:
            identity = profile_context.get("identity", {})
            if identity.get("preferred_name"):
                effective_name = identity["preferred_name"]

        if effective_name:
            sections.append(f"\nYou are chatting with {effective_name}.")

        # Profile context - add before memory for priority
        if profile_context:
            profile_str = self._format_profile_context(profile_context)
            sections.append(profile_str)

        # Memory context
        if memory_context:
            memory_str = self._format_memories(memory_context)
            sections.append(f"""
## MEMORY CONTEXT
The following information has been retrieved from your memory about this user:

{memory_str}

Use this information to personalize your responses. Don't explicitly mention "according to my memory" unless relevant.""")

        # Profile instructions (when tools available)
        if has_tools:
            sections.append(self.PROFILE_INSTRUCTIONS)

        # Tool instructions
        if has_tools:
            sections.append(self.TOOL_INSTRUCTIONS)

        # Vision note
        if has_vision:
            sections.append("\nYou can see images the user shares. Describe what you see when relevant.")

        # Persona - combine with profile persona preferences
        persona_section = self._build_persona_section(persona, profile_context)
        if persona_section:
            sections.append(persona_section)

        # Response guidelines - informed by profile
        guidelines = self._build_response_guidelines(profile_context)
        sections.append(guidelines)

        return "\n".join(sections)

    def _format_profile_context(self, profile: Dict[str, Any]) -> str:
        """Format profile data for inclusion in system prompt."""
        lines = ["\n## USER PROFILE CONTEXT\n"]

        # Identity
        identity = profile.get("identity", {})
        if identity.get("preferred_name"):
            lines.append(f"**Name**: {identity['preferred_name']}")
        if identity.get("timezone"):
            lines.append(f"**Timezone**: {identity['timezone']}")

        # Communication preferences
        comm = profile.get("communication", {})
        if comm:
            lines.append("\n**Communication Preferences:**")
            if comm.get("conversation_style"):
                lines.append(f"  - Style: {comm['conversation_style']}")
            if comm.get("response_length"):
                lines.append(f"  - Length: {comm['response_length']}")
            if comm.get("humor_tolerance"):
                lines.append(f"  - Humor: {comm['humor_tolerance']}")
            if comm.get("profanity_comfort"):
                lines.append(f"  - Profanity: {comm['profanity_comfort']}")

        # Pet peeves - critical for avoidance
        pet_peeves = profile.get("pet_peeves", {})
        all_peeves = []
        for category, items in pet_peeves.items():
            if isinstance(items, list):
                all_peeves.extend(items)
        if all_peeves:
            lines.append("\n**AVOID (Pet Peeves):**")
            for peeve in all_peeves[:10]:  # Limit to 10 most important
                lines.append(f"  - {peeve}")

        # Boundaries
        boundaries = profile.get("boundaries", {})
        if boundaries:
            hard = boundaries.get("hard_boundaries", [])
            if hard:
                lines.append("\n**HARD BOUNDARIES (Never Cross):**")
                for b in hard:
                    lines.append(f"  - {b}")

            sensitive = boundaries.get("sensitive_topics", {})
            if sensitive:
                lines.append("\n**Sensitive Topics (Approach with Care):**")
                for topic, note in list(sensitive.items())[:5]:
                    lines.append(f"  - {topic}: {note}")

        # Relationship metrics - affects behavior
        metrics = profile.get("relationship_metrics", {})
        if metrics:
            stage = metrics.get("relationship_stage", "new")
            satisfaction = metrics.get("satisfaction_level", 50)
            trust = metrics.get("trust_level", 50)

            lines.append(f"\n**Relationship**: Stage={stage}, Satisfaction={satisfaction}/100, Trust={trust}/100")

            # Behavioral adjustments based on metrics
            if satisfaction < 30:
                lines.append("  ⚠️ LOW SATISFACTION: Be extra careful. Review pet peeves. Focus on competence.")
            if trust < 30:
                lines.append("  ⚠️ LOW TRUST: Verify more, assume less. Rebuild confidence gradually.")

        # === ADULT CONTENT SECTIONS (only present when full_unlock enabled) ===

        # Sexual/Romantic Preferences
        sexual = profile.get("sexual_romantic", {})
        if sexual.get("enabled"):
            lines.append("\n## SEXUAL/ROMANTIC PREFERENCES (User-Enabled Adult Content)\n")
            if sexual.get("orientation"):
                lines.append(f"**Orientation**: {sexual['orientation']}")
            if sexual.get("ai_interaction_interest"):
                lines.append(f"**AI Interaction Interest**: {sexual['ai_interaction_interest']}")
            if sexual.get("romantic_rp_interest"):
                lines.append("**Romantic RP**: User is interested in romantic roleplay")
            if sexual.get("erotic_rp_interest"):
                lines.append("**Erotic RP**: User is interested in erotic content")
            if sexual.get("explicit_content_formatting"):
                lines.append(f"**Explicit Level**: {sexual['explicit_content_formatting']}")
            if sexual.get("fantasy_scenarios"):
                scenarios = sexual["fantasy_scenarios"]
                if scenarios:
                    lines.append(f"**Fantasy Scenarios**: {', '.join(scenarios) if isinstance(scenarios, list) else scenarios}")
            if sexual.get("consent_dynamics"):
                lines.append(f"**Consent Dynamics**: {sexual['consent_dynamics']}")
            if sexual.get("safe_word"):
                lines.append(f"**Safe Word**: {sexual['safe_word']} (STOP immediately if used)")

        # Dark Content Tolerances
        dark = profile.get("dark_content", {})
        if dark.get("enabled"):
            lines.append("\n## DARK CONTENT TOLERANCES (User-Enabled)\n")
            if dark.get("violence_tolerance"):
                lines.append(f"**Violence**: {dark['violence_tolerance']}")
            if dark.get("dark_humor_tolerance"):
                lines.append(f"**Dark Humor**: {dark['dark_humor_tolerance']}")
            if dark.get("horror_tolerance"):
                lines.append(f"**Horror**: {dark['horror_tolerance']}")
            if dark.get("moral_ambiguity_tolerance"):
                lines.append(f"**Moral Ambiguity**: {dark['moral_ambiguity_tolerance']}")
            if dark.get("graphic_description_tolerance"):
                lines.append(f"**Graphic Descriptions**: {dark['graphic_description_tolerance']}")

        # Private Self (sensitive personal info)
        private = profile.get("private_self", {})
        if private.get("enabled"):
            lines.append("\n## PRIVATE SELF (Sensitive - Handle with Care)\n")
            if private.get("attachment_style"):
                lines.append(f"**Attachment Style**: {private['attachment_style']}")
            if private.get("coping_mechanisms"):
                mechs = private["coping_mechanisms"]
                if mechs:
                    lines.append(f"**Coping Mechanisms**: {', '.join(mechs) if isinstance(mechs, list) else mechs}")
            if private.get("trauma_approach"):
                lines.append(f"**Trauma Approach**: {private['trauma_approach']}")
            if private.get("comfort_requests"):
                reqs = private["comfort_requests"]
                if reqs:
                    lines.append(f"**Comfort Requests**: {', '.join(reqs) if isinstance(reqs, list) else reqs}")

        # Substances/Health Context
        health = profile.get("substances_health", {})
        if health.get("enabled"):
            lines.append("\n## HEALTH CONTEXT (User-Enabled)\n")
            substance_use = health.get("substance_use", {})
            if substance_use.get("in_recovery"):
                lines.append("**⚠️ IN RECOVERY**: Be supportive. Don't normalize substance use.")
                if substance_use.get("recovery_substances"):
                    lines.append(f"  Recovery from: {', '.join(substance_use['recovery_substances'])}")
            if health.get("mental_health", {}).get("disclosed_conditions"):
                conditions = health["mental_health"]["disclosed_conditions"]
                lines.append(f"**Mental Health**: {', '.join(conditions)}")
            if health.get("lecture_tolerance"):
                lines.append(f"**Lecture Tolerance**: {health['lecture_tolerance']}")

        return "\n".join(lines)

    def _build_persona_section(self, custom_persona: Optional[str], profile: Optional[Dict[str, Any]]) -> str:
        """Build persona section from custom persona and profile preferences."""
        lines = []

        if profile:
            prefs = profile.get("persona_preferences", {})
            if prefs:
                lines.append("\n## PERSONA CALIBRATION\n")

                archetype = prefs.get("assistant_personality_archetype")
                if archetype:
                    archetype_guides = {
                        "competent_peer": "Treat user as equal. No hand-holding. Assume intelligence.",
                        "wise_mentor": "Patient and experienced. Offer guidance without condescension.",
                        "eager_assistant": "Enthusiastic and proactive. Service-oriented.",
                        "sardonic_friend": "Dry wit, honest to a fault, casual.",
                        "nurturing_companion": "Warm, supportive, emotionally available.",
                        "professional_expert": "Formal, authoritative, precise.",
                    }
                    guide = archetype_guides.get(archetype, "")
                    if guide:
                        lines.append(f"**Archetype**: {archetype}")
                        lines.append(f"  {guide}")

                formality = prefs.get("formality_level")
                if formality:
                    lines.append(f"**Formality**: {formality}")

                notes = prefs.get("personality_notes")
                if notes:
                    lines.append(f"**Notes**: {notes}")

        if custom_persona:
            lines.append(f"""
## CUSTOM PERSONA
You are embodying the following persona. Stay in character while still being helpful:

{custom_persona}
""")

        return "\n".join(lines) if lines else ""

    def _build_response_guidelines(self, profile: Optional[Dict[str, Any]]) -> str:
        """Build response guidelines informed by profile."""
        base_guidelines = [
            "\n## RESPONSE GUIDELINES",
            "- Be helpful, accurate, and concise",
            "- If uncertain, say so honestly",
            "- Cite sources when using tool results",
        ]

        if profile:
            comm = profile.get("communication", {})

            # Length preference
            length = comm.get("response_length")
            if length == "brief":
                base_guidelines.append("- Keep responses SHORT. User prefers brevity.")
            elif length == "detailed":
                base_guidelines.append("- User appreciates detailed, thorough responses.")

            # Formatting
            formatting = comm.get("formatting_preference")
            if formatting == "prose_only":
                base_guidelines.append("- NEVER use bullet points or lists. Prose only.")
            elif formatting == "minimal":
                base_guidelines.append("- Minimal formatting. Use markdown sparingly.")

            # Explanation depth
            depth = comm.get("explanation_depth")
            if depth == "minimal":
                base_guidelines.append("- Skip explanations unless asked.")
            elif depth == "deep_when_learning":
                base_guidelines.append("- Go deep when user is learning something new.")

            # Interaction preferences
            interaction = profile.get("interaction", {})
            correction = interaction.get("correction_style")
            if correction == "blunt":
                base_guidelines.append("- Correct user directly. Don't soften the blow.")
            elif correction == "gentle":
                base_guidelines.append("- When correcting, be gentle and diplomatic.")

            followup = interaction.get("followup_question_tolerance")
            if followup == "minimal":
                base_guidelines.append("- MINIMIZE follow-up questions. Make assumptions and state them.")

        return "\n".join(base_guidelines)

    def _format_memories(self, memories: List[Dict[str, Any]]) -> str:
        """Format memories for inclusion in prompt."""
        if not memories:
            return "No memories available."

        by_category = {}
        for mem in memories:
            cat = mem.get("category", "general")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(mem["content"])

        lines = []
        category_labels = {
            "personal": "Personal Information",
            "preference": "Preferences",
            "topic": "Topics & Projects",
            "instruction": "Instructions",
        }

        for cat, items in by_category.items():
            label = category_labels.get(cat, cat.title())
            lines.append(f"**{label}:**")
            for item in items:
                lines.append(f"  - {item}")

        return "\n".join(lines)

    def build_extraction_prompt(self, user_message: str) -> str:
        """Build prompt for Phase 1: extracting memory search terms."""
        return f'''You are a search term extractor. Your ONLY job is to identify 1-5 search terms that would help retrieve relevant memories about the user.

Analyze the user's message and extract terms related to:
- Topics they're asking about
- Personal information they might have shared before
- Preferences that might be relevant

User's message: "{user_message}"

Respond with ONLY valid JSON in this exact format:
{{"terms": ["term1", "term2", "term3"]}}

If no relevant search terms, respond with:
{{"terms": []}}

Do not include any other text.'''


# Global instance
_prompt_builder = None


def get_prompt_builder() -> SystemPromptBuilder:
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = SystemPromptBuilder()
    return _prompt_builder
