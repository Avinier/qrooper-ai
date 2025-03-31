import os
import json
import time
from datetime import datetime
import googleapiclient.discovery
import googleapiclient.errors
from pathlib import Path
import pandas as pd
import numpy as np
from astrapy import DataAPIClient
from dotenv import load_dotenv


class YouTubeAstraIntegrator:
    def __init__(self, youtube_api_key, astra_token, astra_endpoint, collection_name="youtube_data",
                 output_dir='youtube_data'):
        """
        Initialize YouTube scraper and AstraDB uploader.
        """
        # Initialize YouTube API client
        if not youtube_api_key:
            raise ValueError("YouTube API key is required")

        try:
            self.youtube = googleapiclient.discovery.build(
                "youtube", "v3", developerKey=youtube_api_key
            )
        except Exception as e:
            print(f"Error initializing YouTube API client: {e}")
            self.youtube = None

        # Initialize AstraDB client
        self.client = DataAPIClient(astra_token)
        self.db = self.client.get_database_by_api_endpoint(astra_endpoint)
        self.collection = self.db[collection_name]
        self.vector_dim = 1536

        # Create output directory
        self.data_dir = Path(output_dir)
        self.data_dir.mkdir(exist_ok=True)

        print(f"Connected to YouTube API and Astra DB collection: {collection_name}")

    def create_vector(self, text):
        """Create normalized vector for text embedding."""
        vector = np.random.normal(0, 1, self.vector_dim)
        normalized_vector = vector / np.linalg.norm(vector)
        return normalized_vector.tolist()

    def prepare_document(self, video_data):
        """Prepare video data for AstraDB storage."""
        try:
            # Create a simpler text content for vector creation
            title = video_data.get('title', '')[:1000]
            description = video_data.get('description', '')[:3000]

            comment_texts = []
            for comment in video_data.get('comments', [])[:5]:
                comment_text = comment.get('text', '')[:500]
                comment_texts.append(comment_text)

            text_content = f"{title} {description} {' '.join(comment_texts)}"

            content_bytes = text_content.encode('utf-8')
            if len(content_bytes) > 8000:
                content_bytes = content_bytes[:8000]
                text_content = content_bytes.decode('utf-8', errors='ignore')

            metadata = {
                'video_id': video_data.get('video_id', ''),
                'title': title,
                'channel_title': video_data.get('channel_title', '')[:100],
                'view_count': video_data.get('view_count', 0),
                'like_count': video_data.get('like_count', 0),
                'comment_count': video_data.get('comment_count', 0),
                'published_at': video_data.get('published_at', ''),
                'scraped_at': datetime.now().isoformat(),
                'comments': [{'text': t[:500], 'author': c.get('author', '')[:100]}
                             for t, c in zip(comment_texts, video_data.get('comments', [])[:5])]
            }

            document = {
                'content': text_content,
                'metadata': metadata,
                '$vector': self.create_vector(text_content)
            }

            return document
        except Exception as e:
            print(f"Error preparing document: {e}")
            return None

    def get_video_comments(self, video_id, max_comments=50):
        """Get comments for a video."""
        comments = []
        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(max_comments, 100)
            )

            while request and len(comments) < max_comments:
                response = request.execute()

                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    comment_data = {
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'like_count': comment['likeCount'],
                        'published_at': comment['publishedAt']
                    }
                    comments.append(comment_data)

                request = self.youtube.commentThreads().list_next(request, response)

        except Exception as e:
            print(f"Error fetching comments: {e}")

        return comments

    def _save_data(self, data, prefix):
        """Save local copy of data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_file = self.data_dir / f'{prefix}_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        try:
            flat_data = {
                'video_id': data['video_id'],
                'title': data['title'],
                'channel_title': data['channel_title'],
                'view_count': data['view_count'],
                'like_count': data['like_count'],
                'comment_count': data['comment_count'],
                'published_at': data['published_at']
            }

            csv_file = self.data_dir / f'{prefix}_{timestamp}.csv'
            pd.DataFrame([flat_data]).to_csv(csv_file, index=False)

            print(f"Data saved to {json_file} and {csv_file}")
        except Exception as e:
            print(f"Error saving CSV: {e}")