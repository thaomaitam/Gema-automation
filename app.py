"""
Gemma Android Automation App
Entry point for interactive automation using gemma-3n-E4B-it via Ollama
"""
import sys
from agent.model import GemmaAgent, list_available_models, check_model_available
import config


def print_banner():
    """Print application banner."""
    print("\n" + "=" * 60)
    print("  🤖 GEMMA ANDROID AUTOMATION")
    print("  Powered by gemma-3n-E4B-it via Ollama")
    print("=" * 60 + "\n")


def select_model() -> str:
    """Let user select a model from available options."""
    print("📋 Checking available models...")
    available = list_available_models()
    
    if not available:
        print("⚠️  No Ollama models found. Please install models first:")
        print("   ollama pull gemma3n:e4b")
        sys.exit(1)
    
    print("\n🔍 Available Models:")
    for i, model in enumerate(available, 1):
        default_marker = " (default)" if config.DEFAULT_MODEL in model else ""
        print(f"   {i}. {model}{default_marker}")
    
    print(f"\n   0. Use default: {config.DEFAULT_MODEL}")
    
    while True:
        choice = input("\n👉 Select model (0-{0}): ".format(len(available))).strip()
        
        if choice == "" or choice == "0":
            if check_model_available(config.DEFAULT_MODEL):
                return config.DEFAULT_MODEL
            else:
                print(f"⚠️  Default model '{config.DEFAULT_MODEL}' not found.")
                print(f"   Pull it with: ollama pull {config.DEFAULT_MODEL}")
                continue
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available):
                return available[idx]
        except ValueError:
            pass
        
        print("❌ Invalid selection. Try again.")


def run_interactive_loop(agent: GemmaAgent):
    """Run the interactive automation loop."""
    print("\n" + "-" * 60)
    print("💡 Enter your automation task. Type 'quit' to exit.")
    print("   Example: 'Take a screenshot of the current screen'")
    print("   Example: 'Open Settings and navigate to About Phone'")
    print("-" * 60 + "\n")
    
    while True:
        try:
            user_input = input("📝 Task: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'reset':
                agent.reset()
                print("🔄 Conversation reset.\n")
                continue
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            # Execute the task
            print("\n🤖 Processing...")
            response = agent.chat(user_input, verbose=True)
            print(f"\n📢 Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted. Type 'quit' to exit.\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def print_help():
    """Print help information."""
    print("""
📚 COMMANDS:
   quit/exit/q  - Exit the application
   reset        - Reset conversation history
   help         - Show this help message

📋 AUTOMATION EXAMPLES:
   • Take a screenshot
   • List connected devices
   • Tap at coordinates (500, 800)
   • Type "Hello World" into the text field
   • Swipe up to scroll
   • Navigate to Settings > About Phone
   • Record a video of my actions
""")


def main():
    """Main entry point."""
    print_banner()
    
    # Select model
    model = select_model()
    print(f"\n✅ Using model: {model}")
    
    # Initialize agent
    print("🚀 Initializing Gemma Agent...")
    try:
        agent = GemmaAgent(model=model)
        print("✅ Agent ready!\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        sys.exit(1)
    
    # Run interactive loop
    run_interactive_loop(agent)


if __name__ == "__main__":
    main()
