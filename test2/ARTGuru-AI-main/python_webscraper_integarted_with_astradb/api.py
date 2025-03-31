import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from youtube_astra_integrator import YouTubeAstraIntegrator
from instagram_astra_integrator import InstagramAstraIntegrator
from reddit_astra_integrator import RedditAstraIntegrator


# Load environment variables
load_dotenv()

app = FastAPI(title="Social Media Data Scraper API")


# Model classes
class SearchRequest(BaseModel):
    keyword: str
    max_results: Optional[int] = 20


class InstagramSearchRequest(BaseModel):
    hashtag: str
    amount: Optional[int] = 20


class SearchResponse(BaseModel):
    videos_stored: int
    videos_failed: int
    message: str


class InstagramResponse(BaseModel):
    posts_found: int
    posts_stored: int
    posts_failed: int
    file_path: Optional[str]
    message: str

# Add new model
class RedditSearchRequest(BaseModel):
    topic: str
    limit: Optional[int] = 5

class RedditResponse(BaseModel):
    posts_found: int
    posts_stored: int
    posts_failed: int
    file_path: Optional[str]
    message: str

# Initialize credentials
youtube_api_key = os.getenv('YOUTUBE_API_KEY')
astra_token = os.getenv('ASTRA_DB_TOKEN')
astra_endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')
instagram_username = os.getenv('INSTAGRAM_USERNAME')
instagram_password = os.getenv('INSTAGRAM_PASSWORD')
# Add to environment variables
reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
reddit_user_agent = os.getenv('REDDIT_USER_AGENT')


if not all([youtube_api_key, astra_token, astra_endpoint]):
    raise Exception("Missing required environment variables")

# Initialize services
youtube_integrator = None
instagram_integrator = None

try:
    youtube_integrator = YouTubeAstraIntegrator(
        youtube_api_key=youtube_api_key,
        astra_token=astra_token,
        astra_endpoint=astra_endpoint,
        collection_name="you"
    )
except Exception as e:
    print(f"Error initializing YouTube integrator: {e}")

try:
    instagram_integrator = InstagramAstraIntegrator(
        instagram_username=instagram_username,
        instagram_password=instagram_password,
        astra_token=astra_token,
        astra_endpoint=astra_endpoint,
        collection_name="you"
    )
except Exception as e:
    print(f"Error initializing Instagram integrator: {e}")


@app.post("/youtube/search", response_model=SearchResponse)
async def search_youtube_videos(request: SearchRequest):
    """
    Search YouTube videos and store in AstraDB.
    """
    if not youtube_integrator:
        raise HTTPException(status_code=500, detail="YouTube integrator not initialized")

    try:
        videos_stored = 0
        videos_failed = 0

        print(f"Searching for YouTube videos with keyword: {request.keyword}")

        search_response = youtube_integrator.youtube.search().list(
            q=request.keyword,
            type='video',
            part='id,snippet',
            maxResults=request.max_results
        ).execute()

        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]

        videos_response = youtube_integrator.youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=','.join(video_ids)
        ).execute()

        for video_data in videos_response.get('items', []):
            try:
                comments = youtube_integrator.get_video_comments(video_data['id'])

                video_info = {
                    'video_id': video_data['id'],
                    'title': video_data['snippet']['title'],
                    'description': video_data['snippet']['description'],
                    'published_at': video_data['snippet']['publishedAt'],
                    'channel_title': video_data['snippet']['channelTitle'],
                    'view_count': int(video_data['statistics'].get('viewCount', 0)),
                    'like_count': int(video_data['statistics'].get('likeCount', 0)),
                    'comment_count': int(video_data['statistics'].get('commentCount', 0)),
                    'comments': comments
                }

                document = youtube_integrator.prepare_document(video_info)
                if document:
                    try:
                        youtube_integrator.collection.insert_one(document)
                        videos_stored += 1
                        print(f"Successfully stored video: {video_info['title']}")
                    except Exception as store_error:
                        videos_failed += 1
                        print(f"Failed to store video in AstraDB: {store_error}")

                youtube_integrator._save_data(video_info, f'video_{video_data["id"]}')

            except Exception as e:
                videos_failed += 1
                print(f"Error processing video: {e}")

        return SearchResponse(
            videos_stored=videos_stored,
            videos_failed=videos_failed,
            message=f"YouTube search completed. Stored {videos_stored} videos, failed {videos_failed}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/instagram/search", response_model=InstagramResponse)
async def search_instagram_posts(request: InstagramSearchRequest):
    """
    Search Instagram posts by hashtag and store in AstraDB.
    """
    if not instagram_integrator:
        raise HTTPException(status_code=500, detail="Instagram integrator not initialized")

    try:
        results = instagram_integrator.search_and_store_hashtag_posts(
            request.hashtag,
            request.amount
        )

        return InstagramResponse(
            posts_found=results['posts_found'],
            posts_stored=results['posts_stored'],
            posts_failed=results['posts_failed'],
            file_path=results['file_path'],
            message=f"Found {results['posts_found']} posts, stored {results['posts_stored']} in AstraDB, failed {results['posts_failed']}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add to service initialization
reddit_integrator = None
try:
    reddit_integrator = RedditAstraIntegrator(
        reddit_client_id=reddit_client_id,
        reddit_client_secret=reddit_client_secret,
        reddit_user_agent=reddit_user_agent,
        astra_token=astra_token,
        astra_endpoint=astra_endpoint,
        collection_name="you"
    )
except Exception as e:
    print(f"Error initializing Reddit integrator: {e}")


# Add new endpoint
@app.post("/reddit/search", response_model=RedditResponse)
async def search_reddit_posts(request: RedditSearchRequest):
    """
    Search Reddit posts by topic and store in AstraDB.
    """
    if not reddit_integrator:
        raise HTTPException(status_code=500, detail="Reddit integrator not initialized")

    try:
        results = reddit_integrator.search_and_store_posts(
            request.topic,
            request.limit
        )

        return RedditResponse(
            posts_found=results['posts_found'],
            posts_stored=results['posts_stored'],
            posts_failed=results['posts_failed'],
            file_path=results['file_path'],
            message=f"Found {results['posts_found']} posts, stored {results['posts_stored']} in AstraDB, failed {results['posts_failed']}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Update health check to include Reddit
@app.get("/health")
async def health_check():
    return {
        "youtube_status": "healthy" if youtube_integrator else "unhealthy",
        "instagram_status": "healthy" if instagram_integrator else "unhealthy",
        "reddit_status": "healthy" if reddit_integrator else "unhealthy",
        "youtube_api": "configured" if youtube_api_key else "missing",
        "astra_db": "configured" if astra_token and astra_endpoint else "missing",
        "instagram_auth": "configured" if instagram_username and instagram_password else "missing",
        "reddit_auth": "configured" if all([reddit_client_id, reddit_client_secret, reddit_user_agent]) else "missing"
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)