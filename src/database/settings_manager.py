"""
Settings Manager - Store and retrieve application settings in MongoDB
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pymongo.collection import Collection
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config
from src.database.mongodb_client import get_collection

logger = logging.getLogger(__name__)

# Settings collection name
SETTINGS_COLLECTION = "app_settings"


def get_settings_collection() -> Collection:
    """Get the settings collection"""
    from pymongo import MongoClient
    client = MongoClient(config.MONGODB_URI)
    db = client[config.MONGODB_DATABASE]
    return db[SETTINGS_COLLECTION]


def save_llm_settings(
    provider: str,
    api_key: str,
    model: Optional[str] = None,
    user_id: str = "default"
) -> bool:
    """
    Save LLM configuration settings to MongoDB

    Args:
        provider: LLM provider (OpenRouter, Claude, Custom)
        api_key: API key (encrypted/hashed in production)
        model: Selected model (for OpenRouter)
        user_id: User identifier (default: "default" for single-user setup)

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        collection = get_settings_collection()

        settings_doc = {
            "user_id": user_id,
            "setting_type": "llm_config",
            "provider": provider,
            "api_key": api_key,  # WARNING: In production, encrypt this!
            "model": model,
            "last_updated": datetime.utcnow(),
            "updated_at": datetime.utcnow().isoformat()
        }

        # Upsert: update if exists, insert if not
        result = collection.update_one(
            {
                "user_id": user_id,
                "setting_type": "llm_config"
            },
            {"$set": settings_doc},
            upsert=True
        )

        logger.info(f"LLM settings saved for user: {user_id}, provider: {provider}")
        return True

    except Exception as e:
        logger.error(f"Error saving LLM settings: {e}")
        return False


def load_llm_settings(user_id: str = "default") -> Optional[Dict[str, Any]]:
    """
    Load LLM configuration settings from MongoDB

    Args:
        user_id: User identifier (default: "default" for single-user setup)

    Returns:
        Dictionary with settings or None if not found
    """
    try:
        collection = get_settings_collection()

        settings_doc = collection.find_one({
            "user_id": user_id,
            "setting_type": "llm_config"
        })

        if settings_doc:
            logger.info(f"LLM settings loaded for user: {user_id}")
            return {
                "provider": settings_doc.get("provider"),
                "api_key": settings_doc.get("api_key"),
                "model": settings_doc.get("model"),
                "last_updated": settings_doc.get("last_updated")
            }
        else:
            logger.info(f"No LLM settings found for user: {user_id}")
            return None

    except Exception as e:
        logger.error(f"Error loading LLM settings: {e}")
        return None


def clear_llm_settings(user_id: str = "default") -> bool:
    """
    Clear/delete LLM configuration settings

    Args:
        user_id: User identifier (default: "default" for single-user setup)

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        collection = get_settings_collection()

        result = collection.delete_one({
            "user_id": user_id,
            "setting_type": "llm_config"
        })

        logger.info(f"LLM settings cleared for user: {user_id}")
        return result.deleted_count > 0

    except Exception as e:
        logger.error(f"Error clearing LLM settings: {e}")
        return False


def save_user_preference(
    preference_name: str,
    preference_value: Any,
    user_id: str = "default"
) -> bool:
    """
    Save a generic user preference to MongoDB

    Args:
        preference_name: Name of the preference
        preference_value: Value to save
        user_id: User identifier

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        collection = get_settings_collection()

        preference_doc = {
            "user_id": user_id,
            "setting_type": "user_preference",
            "preference_name": preference_name,
            "preference_value": preference_value,
            "last_updated": datetime.utcnow(),
            "updated_at": datetime.utcnow().isoformat()
        }

        result = collection.update_one(
            {
                "user_id": user_id,
                "setting_type": "user_preference",
                "preference_name": preference_name
            },
            {"$set": preference_doc},
            upsert=True
        )

        logger.info(f"Preference '{preference_name}' saved for user: {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving preference: {e}")
        return False


def load_user_preference(
    preference_name: str,
    user_id: str = "default"
) -> Optional[Any]:
    """
    Load a generic user preference from MongoDB

    Args:
        preference_name: Name of the preference
        user_id: User identifier

    Returns:
        Preference value or None if not found
    """
    try:
        collection = get_settings_collection()

        preference_doc = collection.find_one({
            "user_id": user_id,
            "setting_type": "user_preference",
            "preference_name": preference_name
        })

        if preference_doc:
            return preference_doc.get("preference_value")
        else:
            return None

    except Exception as e:
        logger.error(f"Error loading preference: {e}")
        return None


def get_all_settings(user_id: str = "default") -> Dict[str, Any]:
    """
    Get all settings for a user

    Args:
        user_id: User identifier

    Returns:
        Dictionary with all settings
    """
    try:
        collection = get_settings_collection()

        all_settings = list(collection.find({"user_id": user_id}))

        result = {
            "llm_config": None,
            "preferences": {}
        }

        for setting in all_settings:
            if setting.get("setting_type") == "llm_config":
                result["llm_config"] = {
                    "provider": setting.get("provider"),
                    "api_key": setting.get("api_key"),
                    "model": setting.get("model"),
                    "last_updated": setting.get("last_updated")
                }
            elif setting.get("setting_type") == "user_preference":
                pref_name = setting.get("preference_name")
                pref_value = setting.get("preference_value")
                result["preferences"][pref_name] = pref_value

        return result

    except Exception as e:
        logger.error(f"Error getting all settings: {e}")
        return {"llm_config": None, "preferences": {}}
