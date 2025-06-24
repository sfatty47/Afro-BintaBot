from chatbot import culturally_aware_chat
from voice_utils import voice_assistant
import time

def voice_chat():
    """Main voice chat loop"""
    print("🎤 Welcome to BintaBot Voice Assistant!")
    print("You can speak to me or type 'quit' to exit.")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Press Enter to speak")
        print("2. Type your message")
        print("3. Type 'quit' to exit")
        
        choice = input("\nChoose option (1/2/3): ").strip()
        
        if choice == "3" or choice.lower() == "quit":
            voice_assistant.speak("Goodbye! May wisdom guide your path.")
            print("👋 Goodbye! May wisdom guide your path.")
            break
        
        elif choice == "1":
            # Voice input
            user_input = voice_assistant.listen()
            if user_input:
                print(f"\nYou said: {user_input}")
                response = culturally_aware_chat(user_input)
                voice_assistant.speak(response)
            else:
                voice_assistant.speak("I didn't catch that. Could you please repeat?")
        
        elif choice == "2":
            # Text input
            user_input = input("\nType your message: ").strip()
            if user_input.lower() == "quit":
                voice_assistant.speak("Goodbye! May wisdom guide your path.")
                print("👋 Goodbye! May wisdom guide your path.")
                break
            
            if user_input:
                response = culturally_aware_chat(user_input)
                print(f"\nBintaBot: {response}")
                
                # Ask if user wants voice response
                voice_choice = input("\nWould you like me to speak this response? (y/n): ").strip().lower()
                if voice_choice in ['y', 'yes']:
                    voice_assistant.speak(response)
        
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

def simple_voice_chat():
    """Simplified voice-only chat"""
    print("🎤 BintaBot Voice Assistant - Speak to me!")
    print("Say 'goodbye' to exit.")
    print("=" * 50)
    
    while True:
        user_input = voice_assistant.listen()
        
        if user_input:
            if "goodbye" in user_input or "exit" in user_input or "quit" in user_input:
                voice_assistant.speak("Goodbye! May wisdom guide your path.")
                print("👋 Goodbye! May wisdom guide your path.")
                break
            
            response = culturally_aware_chat(user_input)
            voice_assistant.speak(response)
        else:
            voice_assistant.speak("I didn't catch that. Could you please repeat?")

if __name__ == "__main__":
    try:
        voice_chat()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! May wisdom guide your path.")
    except Exception as e:
        print(f"An error occurred: {e}")
        voice_assistant.speak("I encountered an error. Please try again.") 