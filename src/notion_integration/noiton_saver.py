import os
import json
import requests
from pathlib import Path
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class NotionSaver:
    def __init__(self, notion_token=None, parent_page_id=None):
        """
        Initialize the Notion integration
        
        Args:
            notion_token (str, optional): Your Notion integration token. If None, reads from .env
            parent_page_id (str, optional): Parent page ID. If None, reads from .env
        """
        # Load from environment variables if not provided
        self.notion_token = notion_token or os.getenv('NOTION_TOKEN')
        self.parent_page_id = parent_page_id or os.getenv('NOTION_PARENT_PAGE_ID')
        
        # Validate token
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN not found. Please provide it as parameter or set it in .env file")
        
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"
        
        print(f"🔑 Loaded Notion token: {self.notion_token[:10]}...")
        if self.parent_page_id:
            print(f"📄 Using parent page ID: {self.parent_page_id}")
        else:
            print("📄 No parent page ID found in environment")
        
        # If no parent page ID found, user needs to set it manually
        if not self.parent_page_id:
            print("� No parent page ID found. You'll need to set it manually using set_parent_page_id()")
    
    @classmethod
    def from_env(cls):
        """
        Create NotionSaver instance using environment variables
        
        Returns:
            NotionSaver: Configured instance
        """
        return cls(
            notion_token=None,  
            parent_page_id=None
        )
    
    def set_parent_page_id(self, page_id):
        """
        Set the parent page ID manually
        
        Args:
            page_id (str): The parent page ID
        """
        self.parent_page_id = page_id
        print(f"✅ Parent page ID set to: {page_id}")
    
    def create_page(self, title, content, youtube_url=None):
        """
        Create a new page in Notion
        
        Args:
            title (str): Page title
            content (str): Text content to add to the page
            youtube_url (str, optional): YouTube URL to embed
            
        Returns:
            dict: Notion API response or None if failed
        """
        url = f"{self.base_url}/pages"
        
        # Convert content to Notion blocks
        content_blocks = self._text_to_blocks(content)
        
        # Prepare the page data
        if self.parent_page_id:
            # Create as child page
            page_data = {
                "parent": {"page_id": self.parent_page_id},
                "properties": {
                    "title": {
                        "title": [{"text": {"content": title}}]
                    }
                },
                "children": []
            }
        else:
            # If no parent page and auto-creation failed, provide guidance
            print("❌ No parent page available. Please:")
            print("   1. Create a page in Notion manually")
            print("   2. Share it with your integration") 
            print("   3. Use: notion.set_parent_page_id('page_id')")
            return None
        
        # Add YouTube embed if URL is provided
        if youtube_url:
            page_data["children"].append({
                "object": "block",
                "type": "embed",
                "embed": {"url": youtube_url}
            })
            
            # Add a divider
            page_data["children"].append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        
        # Add the content blocks
        page_data["children"].extend(content_blocks)
        
        try:
            response = requests.post(url, headers=self.headers, json=page_data)
            
            # Print the request data for debugging
            if response.status_code != 200:
                print(f"Request data: {json.dumps(page_data, indent=2)}")
                print(f"Response status: {response.status_code}")
                print(f"Response text: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating page: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def read_file(self, file_path):
        """
        Read content from a text file
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: File content or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def extract_youtube_url(self, content):
        """
        Extract YouTube URL from text content
        
        Args:
            content (str): Text content to search
            
        Returns:
            str: YouTube URL or None if not found
        """
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://youtu\.be/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
        ]
        
        for pattern in youtube_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(0)
        return None
    
    def extract_title_from_content(self, content):
        """
        Extract the first # heading from content to use as page title
        
        Args:
            content (str): Text content to search
            
        Returns:
            str: Extracted title or None if not found
        """
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                # Remove the # and any extra whitespace
                title = line[2:].strip()
                return title
        return None
    
    def process_file(self, file_path, youtube_url=None):
        """
        Process a single file and create a Notion page
        
        Args:
            file_path (str): Path to the file
            youtube_url (str, optional): YouTube URL to embed
            
        Returns:
            dict: Created page data or None if failed
        """
        # Read file content
        content = self.read_file(file_path)
        if not content:
            return None
        
        # Extract YouTube URL if not provided
        if not youtube_url:
            youtube_url = self.extract_youtube_url(content)
        
        # Try to extract title from content first
        title = self.extract_title_from_content(content)
        
        # Fallback to filename if no title found in content
        if not title:
            title = Path(file_path).stem
            print(f"⚠️ No # heading found in {file_path}, using filename as title")
        else:
            print(f"📝 Using title from content: {title}")
        
        # Create the page
        return self.create_page(title, content, youtube_url)
    
    def _text_to_blocks(self, text_content):
        """
        Convert plain text to Notion blocks (private method)
        
        Args:
            text_content (str): Text content
            
        Returns:
            list: List of Notion blocks
        """
        blocks = []
        paragraphs = text_content.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # Check if it's a heading
                if paragraph.startswith('#'):
                    heading_text = paragraph.lstrip('#').strip()
                    heading_level = min(len(paragraph) - len(paragraph.lstrip('#')), 3)
                    
                    blocks.append({
                        "object": "block",
                        "type": f"heading_{heading_level}",
                        f"heading_{heading_level}": {
                            "rich_text": [{"type": "text", "text": {"content": heading_text}}]
                        }
                    })
                else:
                    # Regular paragraph
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": paragraph}}]
                        }
                    })
        
        return blocks
