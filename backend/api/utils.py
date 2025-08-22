import os
from django.utils import timezone
from django.utils.text import slugify

def course_image_upload_path(instance, filename):
    """
    Generate ultra-compact upload path for course images: cid.jpg (no folder)
    Target: Entire URL < 64 bytes
    """
    if hasattr(instance, 'course_id'):
        course_id = instance.course_id
    elif hasattr(instance, 'course') and instance.course:
        course_id = instance.course.course_id
    else:
        course_id = 'u'
    
    # Get file extension
    ext = os.path.splitext(filename)[1]
    # Create ultra-compact filename: just cid.ext (no folder)
    new_filename = f"{course_id}{ext}"
    
    return new_filename

def course_video_upload_path(instance, filename):
    """
    Generate ultra-compact upload path for course videos: cid.mp4 (no folder)
    Target: Entire URL < 64 bytes
    """
    if hasattr(instance, 'course_id'):
        course_id = instance.course_id
    elif hasattr(instance, 'course') and instance.course:
        course_id = instance.course.course_id
    elif hasattr(instance, 'variant') and instance.variant and instance.variant.course:
        course_id = instance.variant.course.course_id
    else:
        course_id = 'u'
    
    # Get file extension
    ext = os.path.splitext(filename)[1]
    # Create ultra-compact filename: just cid.ext (no folder)
    new_filename = f"{course_id}{ext}"
    
    return new_filename

def course_file_upload_path(instance, filename):
    """
    Generate ultra-compact upload path for course files: cid.pdf (no folder)
    Target: Entire URL < 64 bytes
    """
    if hasattr(instance, 'course_id'):
        course_id = instance.course_id
    elif hasattr(instance, 'course') and instance.course:
        course_id = instance.course.course_id
    elif hasattr(instance, 'variant') and instance.variant and instance.variant.course:
        course_id = instance.variant.course.course_id
    else:
        course_id = 'u'
    
    # Get file extension
    ext = os.path.splitext(filename)[1]
    # Create ultra-compact filename: just cid.ext (no folder)
    new_filename = f"{course_id}{ext}"
    
    return new_filename

def teacher_image_upload_path(instance, filename):
    """
    Generate ultra-compact upload path for teacher images: tid.jpg (no folder)
    Target: Entire URL < 64 bytes
    """
    if hasattr(instance, 'user') and instance.user:
        teacher_id = instance.user.id
    else:
        teacher_id = 'u'
    
    # Get file extension
    ext = os.path.splitext(filename)[1]
    # Create ultra-compact filename: just tid.ext (no folder)
    new_filename = f"{teacher_id}{ext}"
    
    return new_filename

def category_image_upload_path(instance, filename):
    """
    Generate ultra-compact upload path for category images: cid.jpg (no folder)
    Target: Entire URL < 64 bytes
    """
    if hasattr(instance, 'id'):
        category_id = instance.id
    else:
        category_id = 'u'
    
    # Get file extension
    ext = os.path.splitext(filename)[1]
    # Create ultra-compact filename: just cid.ext (no folder)
    new_filename = f"{category_id}{ext}"
    
    return new_filename

def user_avatar_upload_path(instance, filename):
    """
    Generate ultra-compact upload path for user avatars: uid.jpg (no folder)
    Target: Entire URL < 64 bytes
    """
    if hasattr(instance, 'id'):
        user_id = instance.id
    else:
        user_id = 'u'
    
    # Get file extension
    ext = os.path.splitext(filename)[1]
    # Create ultra-compact filename: just uid.ext (no folder)
    new_filename = f"{user_id}{ext}"
    
    return new_filename

def certificate_pdf_upload_path(instance, filename):
    """
    Generate ultra-compact upload path for certificates: ciduid.pdf (no folder, no dash)
    Target: Entire URL < 64 bytes
    """
    if hasattr(instance, 'course') and instance.course:
        course_id = instance.course.course_id
    else:
        course_id = 'u'
    
    if hasattr(instance, 'user') and instance.user:
        user_id = instance.user.id
    else:
        user_id = 'u'
    
    # Get file extension
    ext = os.path.splitext(filename)[1]
    
    # For very long course IDs, truncate to first 3 characters
    if len(course_id) > 3:
        course_id = course_id[:3]
    
    # For very long user IDs, truncate to first 2 characters
    if len(str(user_id)) > 2:
        user_id = str(user_id)[:2]
    
    # Create ultra-compact filename: ciduid.ext (truncated if needed)
    new_filename = f"{course_id}{user_id}{ext}"
    
    return new_filename

def get_file_type(filename):
    """
    Determine if a file is an image, video, or other file type
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'}
    
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in image_extensions:
        return 'image'
    elif ext in video_extensions:
        return 'video'
    else:
        return 'file'

def get_compact_filename(instance, filename, prefix=''):
    """
    Generate ultra-compact filename for any file type
    Target: < 64 bytes total URL length
    """
    # Get instance ID (course_id, user_id, etc.)
    instance_id = None
    if hasattr(instance, 'course_id'):
        instance_id = instance.course_id
    elif hasattr(instance, 'id'):
        instance_id = instance.id
    elif hasattr(instance, 'user') and instance.user:
        instance_id = instance.user.id
    else:
        instance_id = 'u'
    
    # Get file extension
    ext = os.path.splitext(filename)[1]
    
    # Create ultra-compact filename: prefix-id.ext
    if prefix:
        new_filename = f"{prefix}-{instance_id}{ext}"
    else:
        new_filename = f"{instance_id}{ext}"
    
    return new_filename

def get_upload_path_info():
    """
    Return information about the ultra-compact naming system
    """
    return {
        "naming_convention": "Ultra-Compact URLs - Entire URL < 64 bytes (NO FOLDERS)",
        "prefixes": {
            "none": "no folder prefixes - just filename"
        },
        "examples": {
            "course_image": "ABC123.jpg",
            "course_video": "ABC123.mp4",
            "teacher_image": "789.jpg",
            "user_avatar": "456.jpg",
            "certificate": "ABC123-789.pdf"
        },
        "url_lengths": {
            "base_cloudinary": "https://res.cloudinary.com/dzywzlqfh/image/upload/v1/",
            "base_length": 53,
            "course_image": "ABC123.jpg",
            "path_length": 11,
            "total_example": "https://res.cloudinary.com/dzywzlqfh/image/upload/v1/ABC123.jpg",
            "total_length": 64
        }
    }

def calculate_url_length(cloud_name, path):
    """
    Calculate the total URL length for a given path
    """
    base_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/v1/"
    full_url = base_url + path
    return len(full_url), full_url

def get_ultra_compact_path(instance, filename, file_type):
    """
    Get the most compact path possible for a file
    """
    if hasattr(instance, 'course_id'):
        return f"{instance.course_id}{os.path.splitext(filename)[1]}"
    elif hasattr(instance, 'id'):
        return f"{instance.id}{os.path.splitext(filename)[1]}"
    else:
        return f"u{os.path.splitext(filename)[1]}"

def get_minimal_path(instance, filename):
    """
    Get the absolute minimal path possible
    """
    # Get file extension
    ext = os.path.splitext(filename)[1]
    
    # For course files, use just the course ID
    if hasattr(instance, 'course_id'):
        return f"{instance.course_id}{ext}"
    
    # For other files, use just the ID
    if hasattr(instance, 'id'):
        return f"{instance.id}{ext}"
    
    # Fallback
    return f"u{ext}"

# Legacy path support for existing files
def get_legacy_compatible_path(instance, filename, new_path_func):
    """
    Generate a path that's compatible with both old and new systems
    This ensures existing files continue to work while new files use compact paths
    """
    # For new uploads, use the compact path
    if not instance.pk:  # New instance
        return new_path_func(instance, filename)
    
    # For existing instances, check if they have old-style paths
    # If they do, maintain compatibility by using a hybrid approach
    if hasattr(instance, 'image') and instance.image:
        current_path = str(instance.image)
        if 'course-file' in current_path or 'user_folder' in current_path:
            # This is an existing file with old path, keep it
            return current_path
    
    # Use new compact path for new files
    return new_path_func(instance, filename)
