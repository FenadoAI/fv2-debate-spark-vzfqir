from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime
from openai import OpenAI

# Try to import Gemini, but make it optional
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client[os.environ['DB_NAME']]

# OpenAI client
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Gemini client
if GEMINI_AVAILABLE:
    gemini_client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
else:
    gemini_client = None

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class DebateTopicRequest(BaseModel):
    topic: str

class Argument(BaseModel):
    point: str
    supporting_facts: List[str]

class DebateResponse(BaseModel):
    topic: str
    arguments_for: List[Argument]
    arguments_against: List[Argument]

class GeminiRequest(BaseModel):
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7

class GeminiResponse(BaseModel):
    response: str
    model: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

def generate_mock_debate_arguments(topic: str) -> dict:
    """Generate mock debate arguments for demo purposes"""
    # Create topic-specific arguments or use generic ones
    topic_lower = topic.lower()

    if "social media" in topic_lower:
        return {
            "arguments_for": [
                {
                    "point": "Protecting vulnerable populations from harmful content",
                    "supporting_facts": [
                        "Studies show increased rates of cyberbullying and mental health issues among teens",
                        "Misinformation can lead to real-world harm and violence",
                        "Regulation exists for other media forms like television and radio"
                    ]
                },
                {
                    "point": "Preventing spread of misinformation and fake news",
                    "supporting_facts": [
                        "False information spreads 6x faster than true information on social platforms",
                        "Election interference through coordinated disinformation campaigns",
                        "Health misinformation during COVID-19 pandemic led to preventable deaths"
                    ]
                },
                {
                    "point": "Ensuring fair market competition",
                    "supporting_facts": [
                        "Major platforms have monopolistic control over information flow",
                        "Small businesses depend on these platforms with no alternatives",
                        "Data privacy violations affect billions of users globally"
                    ]
                }
            ],
            "arguments_against": [
                {
                    "point": "Protecting free speech and expression rights",
                    "supporting_facts": [
                        "First Amendment protects freedom of expression in democratic societies",
                        "Government regulation could lead to censorship of legitimate viewpoints",
                        "Private companies should determine their own content policies"
                    ]
                },
                {
                    "point": "Innovation and technological progress concerns",
                    "supporting_facts": [
                        "Heavy regulation could stifle innovation in tech sector",
                        "Compliance costs would favor large companies over startups",
                        "Global competitiveness could be affected by restrictive policies"
                    ]
                },
                {
                    "point": "Practical enforcement challenges",
                    "supporting_facts": [
                        "Difficult to define and consistently apply content standards",
                        "Cross-border nature of internet makes regulation complex",
                        "Risk of government overreach into private communications"
                    ]
                }
            ]
        }

    # Generic arguments for any topic
    return {
        "arguments_for": [
            {
                "point": f"Supporting {topic} brings positive societal benefits",
                "supporting_facts": [
                    "Research indicates potential improvements in quality of life",
                    "Expert consensus suggests this approach addresses key challenges",
                    "Successful implementation examples exist in other contexts"
                ]
            },
            {
                "point": f"Economic advantages of implementing {topic}",
                "supporting_facts": [
                    "Cost-benefit analysis shows long-term financial gains",
                    "Job creation and economic growth opportunities",
                    "Reduced social costs and improved resource allocation"
                ]
            },
            {
                "point": f"Moral and ethical imperative to support {topic}",
                "supporting_facts": [
                    "Aligns with fundamental principles of justice and fairness",
                    "Addresses inequality and promotes equal opportunities",
                    "Future generations will benefit from this decision"
                ]
            }
        ],
        "arguments_against": [
            {
                "point": f"Potential negative consequences of {topic}",
                "supporting_facts": [
                    "Unintended side effects may outweigh intended benefits",
                    "Historical examples show similar approaches have failed",
                    "Risk of creating new problems while solving existing ones"
                ]
            },
            {
                "point": f"Economic costs and resource allocation concerns",
                "supporting_facts": [
                    "Implementation requires significant financial investment",
                    "Opportunity cost of not investing resources elsewhere",
                    "Taxpayer burden and questions of fiscal responsibility"
                ]
            },
            {
                "point": f"Individual rights and freedom concerns",
                "supporting_facts": [
                    "May infringe on personal choice and autonomy",
                    "Government intervention in private matters raises concerns",
                    "Slippery slope toward increased regulation and control"
                ]
            }
        ]
    }

@api_router.post("/generate-debate", response_model=DebateResponse)
async def generate_debate_arguments(request: DebateTopicRequest):
    try:
        # Try Gemini first, fallback to OpenAI, then mock data
        parsed_response = None

        if GEMINI_AVAILABLE and gemini_client:
            try:
                # Use Gemini API
                prompt = f"""
                Generate balanced debate arguments for the topic: "{request.topic}"

                Please provide:
                1. 3-4 strong arguments FOR the topic with supporting facts
                2. 3-4 strong arguments AGAINST the topic with supporting facts

                Format the response as JSON with this structure:
                {{
                    "arguments_for": [
                        {{
                            "point": "Main argument point",
                            "supporting_facts": ["Fact 1", "Fact 2", "Fact 3"]
                        }}
                    ],
                    "arguments_against": [
                        {{
                            "point": "Main argument point",
                            "supporting_facts": ["Fact 1", "Fact 2", "Fact 3"]
                        }}
                    ]
                }}

                Ensure arguments are well-researched, factual, and present both sides fairly.
                """

                response = gemini_client.models.generate_content(
                    model='gemini-2.0-flash-001',
                    contents=prompt,
                    config={
                        'system_instruction': 'You are a knowledgeable debate coach who provides balanced, well-researched arguments for any topic. Always respond with valid JSON only.',
                        'temperature': 0.7,
                        'max_output_tokens': 2000
                    }
                )

                ai_response = response.text
                parsed_response = json.loads(ai_response)

            except Exception as gemini_error:
                logger.warning(f"Gemini API failed: {str(gemini_error)}, trying OpenAI...")
                parsed_response = None
        else:
            # Gemini not available, skip to OpenAI
            parsed_response = None

        # Fallback to OpenAI if Gemini failed or not available
        if parsed_response is None:
            if not os.environ.get('OPENAI_API_KEY', '').startswith('sk-placeholder'):
                try:
                    response = openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a knowledgeable debate coach who provides balanced, well-researched arguments for any topic. Always respond with valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=2000
                    )

                    ai_response = response.choices[0].message.content
                    parsed_response = json.loads(ai_response)
                except Exception as openai_error:
                    logger.warning(f"OpenAI API also failed: {str(openai_error)}, using mock data...")

        # Final fallback to mock data
        if parsed_response is None:
            parsed_response = generate_mock_debate_arguments(request.topic)

        # Create the response
        debate_response = DebateResponse(
            topic=request.topic,
            arguments_for=[Argument(**arg) for arg in parsed_response["arguments_for"]],
            arguments_against=[Argument(**arg) for arg in parsed_response["arguments_against"]]
        )

        return debate_response

    except Exception as e:
        logger.error(f"Error generating debate arguments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate debate arguments")

@api_router.post("/gemini-generate", response_model=GeminiResponse)
async def generate_with_gemini(request: GeminiRequest):
    """Generate text using Gemini AI"""
    if not GEMINI_AVAILABLE or gemini_client is None:
        raise HTTPException(
            status_code=503,
            detail="Gemini API is not available. Please install google-genai package and ensure GEMINI_API_KEY is set."
        )

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=request.prompt,
            config={
                'temperature': request.temperature,
                'max_output_tokens': request.max_tokens
            }
        )

        return GeminiResponse(
            response=response.text,
            model='gemini-2.0-flash-001'
        )

    except Exception as e:
        logger.error(f"Error generating content with Gemini: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate content with Gemini: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    mongo_client.close()
