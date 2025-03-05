from typing import Optional, Dict, Any
from twilio.rest import Client
from openai import OpenAI
from app.core.config import settings
import json
import asyncio

class AICallService:
    def __init__(self):
        self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def initiate_call(self, phone_number: str, agent_config: Dict[str, Any]) -> str:
        """
        Initiates a call to the specified phone number using the configured AI agent.
        Returns the call SID.
        """
        call = self.twilio_client.calls.create(
            url=f"{settings.BASE_URL}/api/v1/calls/webhook",
            to=phone_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            status_callback=f"{settings.BASE_URL}/api/v1/calls/status",
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        return call.sid
    
    async def handle_conversation(self, call_sid: str, audio_stream: bytes, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the audio stream and generates AI response.
        Returns the response and conversation data.
        """
        # Convert audio to text using OpenAI Whisper
        transcript = await self._transcribe_audio(audio_stream)
        
        # Generate AI response
        response = await self._generate_response(transcript, agent_config)
        
        # Convert response to speech with personality-driven voice
        audio_response = await self._generate_speech(
            response['text'],
            voice_style=agent_config['personality']['voice_style']
        )
        
        # Analyze conversation
        sentiment = await self._analyze_sentiment(transcript)
        
        return {
            'transcript': transcript,
            'response': response,
            'audio': audio_response,
            'sentiment': sentiment,
            'conversation_data': {
                'intent': response.get('intent'),
                'key_points': response.get('key_points'),
                'next_actions': response.get('next_actions')
            }
        }
    
    async def _transcribe_audio(self, audio: bytes) -> str:
        """Transcribes audio using OpenAI Whisper"""
        transcript = await self.openai_client.audio.transcriptions.create(
            file=audio,
            model="whisper-1"
        )
        return transcript.text
    
    async def _generate_response(self, text: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generates AI response using OpenAI with personality-driven prompting"""
        system_prompt = self._create_personality_prompt(agent_config)
        conversation_context = self._get_conversation_context(text)
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": conversation_context}
            ],
            temperature=0.7,
            functions=[{
                "name": "analyze_conversation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intent": {"type": "string"},
                        "key_points": {"type": "array", "items": {"type": "string"}},
                        "next_actions": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }]
        )
        
        return {
            'text': response.choices[0].message.content,
            'tokens': response.usage.total_tokens,
            'intent': response.choices[0].message.function_call.arguments.get('intent'),
            'key_points': response.choices[0].message.function_call.arguments.get('key_points'),
            'next_actions': response.choices[0].message.function_call.arguments.get('next_actions')
        }
    
    def _create_personality_prompt(self, agent_config: Dict[str, Any]) -> str:
        """Creates a personality-driven system prompt"""
        personality = agent_config['personality']
        return f"""You are a professional and friendly sales representative. Your communication style is:
- Natural and conversational, using contractions and occasional conversational fillers
- Warm and engaging, with a friendliness level of {personality['conversation_style']['friendliness']}/10
- Empathetic and understanding, focusing on building rapport
- Professional but not overly formal
- Enthusiastic about helping potential clients

Key behaviors:
1. Use active listening and acknowledge what the person is saying
2. Maintain a natural conversation flow
3. Show genuine interest in their business needs
4. Be transparent about who you are at the appropriate moment
5. Focus on building trust and rapport before moving to any pitch

Your goal is to:
1. Establish a genuine connection
2. Understand their business challenges
3. Naturally introduce our AI capabilities when relevant
4. Position our solution as a way to help their business

Remember: The key is to be natural and helpful, not salesy or pushy."""
    
    def _get_conversation_context(self, text: str) -> str:
        """Prepares the conversation context with the latest user input"""
        return f"""The person said: "{text}"

Consider:
1. The current stage of the conversation
2. The person's tone and potential concerns
3. The most natural way to respond
4. How to maintain the flow while moving toward our objectives

Respond naturally as a professional sales representative:"""
    
    async def _generate_speech(self, text: str, voice_style: str = "natural") -> bytes:
        """Converts text to speech using OpenAI TTS with personality-appropriate voice"""
        voice_mapping = {
            "natural": "nova",
            "professional": "onyx",
            "friendly": "shimmer"
        }
        
        response = await self.openai_client.audio.speech.create(
            model="tts-1",
            voice=voice_mapping.get(voice_style, "nova"),
            input=text
        )
        return response.content
    
    async def _analyze_sentiment(self, text: str) -> float:
        """Analyzes the sentiment of the conversation"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "Analyze the sentiment of the following text and return a score from -1 (very negative) to 1 (very positive)."},
                {"role": "user", "content": text}
            ]
        )
        return float(response.choices[0].message.content)
    
    async def end_call(self, call_sid: str) -> None:
        """Ends the active call"""
        self.twilio_client.calls(call_sid).update(status="completed") 