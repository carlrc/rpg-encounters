"""
Conversation Manager Module

Manages conversation history with sliding window and automatic summarization.
Maintains recent messages and creates memory summaries for long conversations.
"""

import logging
from typing import List, Callable, Optional

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversation history with automatic summarization and memory management.
    
    Features:
    - Sliding window of recent messages
    - Manual summarization trigger
    - Token-aware prompt building with memory summaries
    - In-memory storage for real-time performance
    """
    
    def __init__(self, exchange_threshold: int = 5):
        """
        Initialize the conversation manager.
        
        Args:
            exchange_threshold: Number of exchanges before summarization is recommended
        """
        self.message_history: List[str] = []
        self.memory_summaries: List[str] = []
        self.exchanges_since_summary: int = 0
        self.exchange_threshold: int = exchange_threshold
        
    def add_message(self, content: str) -> None:
        """
        Add a new message to the conversation history.
        
        Args:
            content: The message content
        """
        if not content.strip():
            logger.warning("Empty content provided")
            return
            
        self.message_history.append(content.strip())
        
        # Count exchanges (every 2 messages = 1 exchange)
        if len(self.message_history) % 2 == 0:
            self.exchanges_since_summary += 1
            logger.debug(f"Exchange count: {self.exchanges_since_summary}")
    
    def should_summarize(self) -> bool:
        """
        Check if summarization should be triggered.
        
        Returns:
            True if enough exchanges have occurred since last summary
        """
        return self.exchanges_since_summary >= self.exchange_threshold
    
    def summarize_recent_exchanges(self, llm_func: Callable[[str, Optional[str]], str]) -> None:
        """
        Summarize recent exchanges and store in memory.
        
        Args:
            llm_func: Function that takes (prompt, system_prompt) and returns response
        """
        # Get the last N exchanges to summarize
        messages_to_summarize = self.exchange_threshold * 2  # 2 messages per exchange
        
        if len(self.message_history) < messages_to_summarize:
            logger.warning("Not enough message history to summarize")
            return
            
        # Get the messages to summarize
        recent_messages = self.message_history[-messages_to_summarize:]
        
        # Build summarization prompt
        conversation_text = "\n".join(f"Message {i+1}: {msg}" for i, msg in enumerate(recent_messages))
        
        summarization_prompt = f"""Please create a concise summary of this recent conversation. Focus on:
- Key interactions and dialogue
- Important plot points or story developments
- Character emotions and reactions
- Any significant decisions or actions

Keep the summary under 150 words and maintain the narrative flow.

Conversation to summarize:
{conversation_text}

Summary:"""

        system_prompt = "You are a helpful assistant that creates concise, narrative summaries of conversations."
        
        try:
            summary = llm_func(summarization_prompt, system_prompt)
            self.memory_summaries.append(summary.strip())
            
            # Remove the summarized messages from active history
            self.message_history = self.message_history[:-messages_to_summarize]
            
            # Reset exchange counter
            self.exchanges_since_summary = 0
            
            logger.info(f"Created summary #{len(self.memory_summaries)}: {summary[:100]}...")
            
        except Exception as e:
            logger.error(f"Failed to create summary: {e}")
    
    def build_prompt(self, system_prompt: str, max_tokens: int = 2048) -> str:
        """
        Build a complete prompt including system prompt, memory, and recent messages.
        
        Args:
            system_prompt: The character/system personality prompt
            max_tokens: Maximum tokens for the entire prompt
            
        Returns:
            Complete prompt string ready for the LLM
        """
        prompt_parts = [system_prompt]
        
        # Add memory summaries if any exist
        if self.memory_summaries:
            memory_section = "\n\nPrevious conversation context:\n" + "\n\n".join(self.memory_summaries)
            prompt_parts.append(memory_section)
        
        # Add recent message history
        if self.message_history:
            recent_section = "\n\nRecent conversation:\n" + "\n".join(self.message_history)
            prompt_parts.append(recent_section)
        
        # Combine all parts
        full_prompt = "\n".join(prompt_parts)
        
        return full_prompt
    
    def clear_history(self) -> None:
        """Clear all conversation history and memory summaries."""
        self.message_history.clear()
        self.memory_summaries.clear()
        self.exchanges_since_summary = 0
        logger.info("Conversation history cleared")


# Example usage
if __name__ == "__main__":
    # Simple test function that mimics LLM behavior
    def mock_llm_func(prompt: str, system_prompt: str = None) -> str:
        return f"Summary of conversation with {len(prompt.split())} words"
    
    # Test the conversation manager
    conv_mgr = ConversationManager(exchange_threshold=2)
    
    # Add some test messages
    conv_mgr.add_message("Hello, I'm a wizard!")
    conv_mgr.add_message("Greetings, wise wizard! What brings you to my tavern?")
    conv_mgr.add_message("I need information about the dragon.")
    conv_mgr.add_message("Ah, the dragon... *leans in closer* That's dangerous talk, friend.")
    
    print(f"Should summarize: {conv_mgr.should_summarize()}")
    
    if conv_mgr.should_summarize():
        conv_mgr.summarize_recent_exchanges(mock_llm_func)
    
    # Build a prompt
    system_prompt = "You are a gruff tavern keeper in a fantasy world."
    prompt = conv_mgr.build_prompt(system_prompt, max_tokens=500)
    print(f"\nGenerated prompt:\n{prompt}")
