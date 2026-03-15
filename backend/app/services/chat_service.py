"""
Chat Service - Handles chat history storage with user support
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from collections import namedtuple

from app.models.db_models import ChatHistory, Document

class ChatService:
    
    @staticmethod
    def save_chat(
        db: Session,
        user_id: str,
        prompt: str,
        response: str,
        state: str,
        document_id: Optional[str] = None,
        laws_retrieved: int = 0
    ) -> ChatHistory:
        """Save chat interaction to database"""
        
        chat = ChatHistory(
            document_id=document_id,
            user_id=user_id,
            prompt=prompt,
            response=response,
            state=state,
            laws_retrieved=laws_retrieved
        )
        
        db.add(chat)
        db.commit()
        db.refresh(chat)
        
        return chat
    
    @staticmethod
    def get_document_chats(db: Session, document_id: str) -> List[ChatHistory]:
        """Get all chats for a document"""
        return db.query(ChatHistory).filter(
            ChatHistory.document_id == document_id
        ).order_by(ChatHistory.created_at).all()
    
    @staticmethod
    def get_user_chats(db: Session, user_id: str, limit: int = 50) -> List[ChatHistory]:
        """Get recent chats for a user"""
        return db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_user_conversations(db: Session, user_id: str):
        """
        Get all conversations for a user (grouped by document).
        Returns list of documents with their latest chat info.
        """
        # Subquery to get latest chat timestamp per document
        latest_chats = db.query(
            ChatHistory.document_id,
            func.max(ChatHistory.created_at).label('last_chat_time')
        ).filter(
            ChatHistory.user_id == user_id,
            ChatHistory.document_id.isnot(None)
        ).group_by(ChatHistory.document_id).subquery()
        
        # Join with documents and get conversation details
        conversations = db.query(
            Document.id.label('document_id'),
            Document.filename,
            Document.state,
            ChatHistory.prompt.label('last_prompt'),
            latest_chats.c.last_chat_time,
            func.count(ChatHistory.id).label('message_count')
        ).join(
            latest_chats,
            Document.id == latest_chats.c.document_id
        ).join(
            ChatHistory,
            (ChatHistory.document_id == Document.id) &
            (ChatHistory.created_at == latest_chats.c.last_chat_time)
        ).filter(
            Document.user_id == user_id
        ).group_by(
            Document.id,
            Document.filename,
            Document.state,
            ChatHistory.prompt,
            latest_chats.c.last_chat_time
        ).order_by(
            desc(latest_chats.c.last_chat_time)
        ).all()
        
        # Convert to named tuples
        ConversationInfo = namedtuple('ConversationInfo', [
            'document_id', 'filename', 'state', 'last_prompt', 
            'last_chat_time', 'message_count'
        ])
        
        return [ConversationInfo(*conv) for conv in conversations]

# Singleton instance
chat_service = ChatService()