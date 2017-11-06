"""
Python wrapper for HUD.ai data access layer

Example usage:

from hudai.client import Client as HudAiClient

client = HudAiClient()
"""

__package_name__ = 'hudai'
__description__ = ('HUD.ai API python bindings')
__keywords__ = ['hud.ai', 'hudai', 'foundry.ai', 'foundrydc']
__url__ = 'https://github.com/FoundryAI/hud-ai-python'
__version__ = '2.11.2'
__author__ = 'HUD.ai Engineering'
__email__ = 'engineering@hud.ai'
__license__ = 'MIT'

from .client import Client
