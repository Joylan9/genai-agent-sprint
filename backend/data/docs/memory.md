# Memory Management

The agent maintains state through two layers:
1. Short-term Memory: Recent conversation history stored in-memory during execution.
2. Long-term Memory: MongoDB persistence for session history across restarts.
3. Memory Optimization: Truncation of old messages to respect LLM context windows.
4. Privacy: Memory is compartmentalized by session ID.
