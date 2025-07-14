from typing import List

class StructuredPrompt:
    def __init__(self, system_prompt: str, history: List[str] = None, memories: List[str] = None, current_prompt: str = ""):
        self.system_prompt = system_prompt
        self.history = history or []
        self.memories = memories or []
        self.current_prompt = current_prompt
    
    def to_string(self) -> str:
        """Convert structured prompt to final string for LLM"""
        parts = [self.system_prompt]
        
        if self.memories:
            memory_section = "\nRelevant memories:" + "".join(f"- {memory}" for memory in self.memories)
            parts.append(memory_section)
        
        if self.history:
            history_section = "\nConversation history:\n" + "".join(self.history)
            parts.append(history_section)
        
        if self.current_prompt:
            parts.append(f"\n\nCurrent message: {self.current_prompt}")
        
        return "\n".join(parts)
