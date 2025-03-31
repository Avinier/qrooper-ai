import praw
import json
import os
from datetime import datetime
import numpy as np
from astrapy import DataAPIClient


class RedditAstraIntegrator:
    def __init__(self, reddit_client_id, reddit_client_secret, reddit_user_agent,
                 astra_token, astra_endpoint, collection_name="you",
                 output_dir="reddit_data"):
        """Initialize Reddit scraper and AstraDB connection."""
        # Initialize Reddit client
        self.reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent
        )

        # Initialize AstraDB
        self.astra_client = DataAPIClient(astra_token)
        self.db = self.astra_client.get_database_by_api_endpoint(astra_endpoint)
        self.collection = self.db[collection_name]
        self.vector_dim = 1536

        # Setup output directory
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def create_vector(self, text: str) -> list:
        """Create normalized vector for text embedding."""
        vector = np.random.normal(0, 1, self.vector_dim)
        normalized_vector = vector / np.linalg.norm(vector)
        return normalized_vector.tolist()

    def prepare_document(self, post_info: dict) -> dict:
        """Prepare Reddit post data for AstraDB storage."""
        try:
            # Combine text content for vector creation
            text_content = f"{post_info.get('title', '')} {post_info.get('selftext', '')} "
            text_content += ' '.join([c.get('body', '') for c in post_info.get('comments', [])][:5])

            # Truncate content if needed
            content_bytes = text_content.encode('utf-8')
            if len(content_bytes) > 8000:
                content_bytes = content_bytes[:8000]
                text_content = content_bytes.decode('utf-8', errors='ignore')

            # Create metadata with essential fields
            metadata = {
                'title': post_info.get('title', '')[:500],
                'url': post_info.get('url', '')[:500],
                'subreddit': post_info.get('subreddit', ''),
                'author': post_info.get('author', ''),
                'score': post_info.get('score', 0),
                'num_comments': post_info.get('num_comments', 0),
                'created_utc': post_info.get('created_utc'),
                'topic': post_info.get('topic', ''),
                'scraped_at': datetime.now().isoformat()
            }

            # Add truncated comments
            if 'comments' in post_info:
                metadata['comments'] = [
                    {
                        'body': c.get('body', '')[:500],
                        'author': c.get('author', '')[:100],
                        'score': c.get('score', 0)
                    }
                    for c in post_info['comments'][:5]  # Limit to top 5 comments
                ]

            return {
                'content': text_content,
                'metadata': metadata,
                '$vector': self.create_vector(text_content)
            }
        except Exception as e:
            print(f"Error preparing document: {e}")
            return None

    def search_and_store_posts(self, topic: str, limit: int = 5) -> dict:
        """Search for Reddit posts and store them in AstraDB."""
        results = {
            'posts_found': 0,
            'posts_stored': 0,
            'posts_failed': 0,
            'file_path': None
        }

        try:
            # Generate subreddits based on topic
            subreddits = self._generate_subreddits_for_topic(topic)
            all_posts = []

            # Search each subreddit
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    top_posts = list(subreddit.top(time_filter='week', limit=limit))
                    results['posts_found'] += len(top_posts)

                    for submission in top_posts:
                        try:
                            submission.comments.replace_more(limit=None)

                            post_info = {
                                'title': submission.title,
                                'url': submission.url,
                                'subreddit': subreddit_name,
                                'topic': topic,
                                'author': str(submission.author),
                                'score': submission.score,
                                'num_comments': submission.num_comments,
                                'created_utc': submission.created_utc,
                                'selftext': submission.selftext,
                                'comments': self._parse_comments_recursively(submission.comments)
                            }

                            # Prepare and store document
                            document = self.prepare_document(post_info)
                            if document:
                                try:
                                    self.collection.insert_one(document)
                                    results['posts_stored'] += 1
                                    all_posts.append(post_info)
                                except Exception as store_error:
                                    results['posts_failed'] += 1
                                    print(f"Failed to store post in AstraDB: {store_error}")

                        except Exception as post_err:
                            results['posts_failed'] += 1
                            print(f"Error processing post: {post_err}")

                except Exception as subreddit_err:
                    print(f"Error accessing subreddit {subreddit_name}: {subreddit_err}")

            # Save local copy
            if all_posts:
                results['file_path'] = self._save_local_copy(all_posts, topic)

            return results

        except Exception as e:
            print(f"Error in search and store process: {e}")
            return results

    def _generate_subreddits_for_topic(self, topic: str) -> list:
        """Generate relevant subreddits for a topic."""
        topic_subreddit_map = {
            'coffee': ['Coffee', 'Coffee_Shop', 'espresso', 'caffeine'],
            'programming': ['Python', 'ProgrammingBuddies', 'learnprogramming', 'coding'],
            'technology': ['technology', 'gadgets', 'tech'],
            'science': ['science', 'space', 'physics', 'biology'],
            'tennis': ['tennis', 'ATP_Tour', 'WTA', 'TennisPro'],
            'ram': ['hardware', 'computer', 'buildapc', 'techsupport']
        }

        topic_lower = topic.lower()
        return topic_subreddit_map.get(topic_lower, [topic, f'{topic}subreddit'])

    def _parse_comments_recursively(self, comments, depth=0, max_depth=3):
        """Parse comments recursively with depth limit."""
        if depth >= max_depth:
            return []

        parsed_comments = []
        for comment in comments:
            try:
                parsed_comment = {
                    'id': comment.id,
                    'author': str(comment.author) if comment.author else 'Deleted',
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'depth': depth
                }

                if hasattr(comment, 'replies') and comment.replies:
                    parsed_comment['replies'] = self._parse_comments_recursively(
                        comment.replies, depth + 1, max_depth
                    )

                parsed_comments.append(parsed_comment)

            except Exception as e:
                print(f"Error parsing comment: {e}")

        return parsed_comments

    def _save_local_copy(self, posts: list, topic: str) -> str:
        """Save local copy of posts."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{topic}_posts_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=4, ensure_ascii=False, default=str)
            return filepath
        except Exception as e:
            print(f"Error saving local copy: {e}")
            return None