###
# exceptions.py
# This file defines custom exception classes for the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###

"""
Custom exception classes for better error handling and distinction
between different types of errors occurring in the OSSL2Gif application.
"""


class OSSL2GifError(Exception):
	"""
	Base exception class for all OSSL2Gif-specific errors.
	All other custom exceptions inherit from this class.
	"""
	pass


class ImageLoadError(OSSL2GifError):
	"""
	Raised when there's an error loading an image or GIF file.
	
	Common causes:
	- File not found or inaccessible
	- File is corrupted or not a valid image format
	- Insufficient memory to load the image
	- Unsupported image format
	"""
	pass


class ImageProcessingError(OSSL2GifError):
	"""
	Raised when there's an error during image processing operations.
	
	Common causes:
	- Failed to resize or transform image
	- Failed to apply effects (blur, sharpen, grayscale, etc.)
	- Memory issues during complex operations
	- Invalid image mode or format for the operation
	"""
	pass


class TextureGenerationError(OSSL2GifError):
	"""
	Raised when there's an error generating the texture sheet.
	
	Common causes:
	- Invalid texture dimensions
	- Memory insufficient for texture sheet
	- Failed to composite frames
	- Invalid background color format
	"""
	pass


class FileOperationError(OSSL2GifError):
	"""
	Raised when there's an error during file save/export operations.
	
	Common causes:
	- File permission denied
	- Disk full
	- Invalid file path or name
	- Unsupported file format
	- File locked by another process
	"""
	pass


class ConfigurationError(OSSL2GifError):
	"""
	Raised when there's an error in configuration or settings.
	
	Common causes:
	- Invalid configuration file format
	- Missing required configuration options
	- Invalid parameter values
	- Incompatible settings
	"""
	pass


class ThreadingError(OSSL2GifError):
	"""
	Raised when there's an error in threading operations.
	
	Common causes:
	- Thread creation failed
	- Queue operation timeout
	- Thread synchronization issues
	- Daemon thread unexpected termination
	"""
	pass


class LSLExportError(OSSL2GifError):
	"""
	Raised when there's an error exporting LSL (Linden Scripting Language) scripts.
	
	Common causes:
	- Invalid tile dimensions
	- File write permissions
	- Invalid script parameters
	- Unsupported characters in script name
	"""
	pass


class ValidationError(OSSL2GifError):
	"""
	Raised when user input validation fails.
	
	Common causes:
	- Invalid numeric values
	- Out of range parameters
	- Missing required fields
	- Type mismatch in parameters
	"""
	pass
