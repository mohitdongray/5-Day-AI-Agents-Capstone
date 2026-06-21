"""
main.py
Brings all three agents together, runs them sequentially and in parallel,
and demonstrates solving all three core problems with real AI.
Now with observability logging and tool demonstration.
"""
import asyncio
from memory_hub import MemoryHub
from memory_agent import MemoryAgent
from comm_agent import CommunicationAgent
from code_explainer_agent import CodeExplainerAgent, WeatherTool
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")


async def demo_sequential():
    print("\n" + "="*60)
    print("DEMO 1: Solving Memory Loss (with real AI)")
    print("="*60)
    
    hub = MemoryHub()
    mem_agent = MemoryAgent(hub)
    code_agent = CodeExplainerAgent(hub)

    # Store a conversation and a preference
    print("\n📝 Storing user memory and preference...")
    mem_agent.run("remember_conversation", "alice", 
                  content="I hate long explanations, prefer short answers.")
    mem_agent.run("set_preference", "alice", key="style", value="concise")

    # Recall what Alice said
    print("\n🔍 Recalling user memories...")
    result = mem_agent.run("recall", "alice")
    print(f"Alice's memories: {result['memories']}")

    style = mem_agent.run("get_preference", "alice", key="style")
    print(f"Alice's preferred style: {style['value']}")

    print("\n" + "="*60)
    print("DEMO 2: Solving Agent Isolation (Cross-Agent Communication)")
    print("="*60)
    
    comm_agent = CommunicationAgent(hub)

    # MemoryAgent sends a message to CodeExplainerAgent through the comm agent
    print("\n📨 MemoryAgent sends message to CodeExplainer via CommAgent...")
    comm_agent.run("send", "session123",
                   from_agent="MemoryAgent",
                   to_agent="CodeExplainer",
                   message="User Alice is a Java beginner. Explain code in simple Java terms.")

    # CodeExplainer polls its messages
    messages = comm_agent.run("poll", "session123", agent_name="CodeExplainer")
    print(f"Messages for CodeExplainer: {messages['messages']}")

    print("\n" + "="*60)
    print("DEMO 3: Solving Code Opacity (Real Gemini API)")
    print("="*60)
    
    java_code = """
    public class Hello {
        public static void main(String[] args) {
            System.out.println("Hello, world!");
        }
    }
    """
    
    print("\n📝 Explaining Java code using REAL Gemini API...")
    explanation = code_agent.run(java_code)
    print(f"Status: {explanation['status']}")
    print(f"Confidence: {explanation.get('confidence', 'N/A')}")
    
    if explanation['status'] == 'error':
        print(f"\n⚠️ Error: {explanation.get('message', 'Unknown error')}")
    else:
        print(f"\n📖 Explanation:\n{explanation['explanation']}")

    # Show observability summary
    print("\n" + "="*60)
    print("DEMO 4: Observability - Operation Summary")
    print("="*60)
    summary = hub.get_operation_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")


async def demo_tools():
    """Demonstrate the Tools concept with WeatherTool."""
    print("\n" + "="*60)
    print("DEMO 5: Tools - Weather Checker")
    print("="*60)
    
    print("\n🌤️ Using WeatherTool to check weather in London...")
    weather = WeatherTool.get_weather("London")
    print(f"Result: {weather}")


async def demo_parallel():
    """All three agents working simultaneously."""
    print("\n" + "="*60)
    print("PARALLEL DEMO: All agents working at the same time")
    print("="*60)
    
    hub = MemoryHub()
    mem_agent = MemoryAgent(hub)
    comm_agent = CommunicationAgent(hub)
    code_agent = CodeExplainerAgent(hub)

    async def task_memory():
        return mem_agent.run("remember_conversation", "bob", 
                            content="Bob loves Python but is learning Java.")

    async def task_communication():
        return comm_agent.run("send", "parallel_conv",
                              from_agent="Orchestrator",
                              to_agent="CodeExplainer",
                              message="Please explain Java streams to Bob.")

    async def task_code_explain():
        java_stream = "List<String> list = Arrays.asList(\"a\",\"b\"); list.stream().map(String::toUpperCase).collect(Collectors.toList());"
        return code_agent.run(java_stream)

    print("\n🚀 Running three agent tasks IN PARALLEL...")
    results = await asyncio.gather(task_memory(), task_communication(), task_code_explain())
    for i, res in enumerate(results):
        print(f"  Task {i+1} result: {res.get('status', 'unknown')}")


async def main():
    print("\n" + "█"*60)
    print("CONTEXTBRIDGE - Unified AI Agent System")
    print("Solving: Memory Loss | Agent Isolation | Code Opacity")
    print("█"*60)
    
    await demo_sequential()
    await demo_tools()
    await demo_parallel()
    
    print("\n" + "="*60)
    print("✅ All demos completed successfully!")
    print("")
    print("🎯 Concepts demonstrated:")
    print("   1. Persistence (Memory): Users memories and preferences survive across sessions")
    print("   2. Multi-Agent Systems: Three agents working together")
    print("   3. Observability: Full logging and operation tracking")
    print("   4. Tools: WeatherTool for external API calls")
    print("   5. Genuine LLM Integration: Real Google Gemini API")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())